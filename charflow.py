#!/usr/bin/env python3
"""Depth-first, single-character generation workflow with explicit Git audit trail.

No image is ever produced from a prior image. Composites only assemble approved results.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for dirname in ['images','approvals','requests','submissions','results','failures','rejected','composites']:
    (ROOT/dirname).mkdir(exist_ok=True)


def utc():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, obj):
    path.parent.mkdir(exist_ok=True, parents=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    tmp.replace(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit(files, message):
    paths = [str(p.relative_to(ROOT)) for p in files]
    subprocess.run(['git', 'add', '--', *paths], cwd=ROOT, check=True)
    s=subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT)
    if s.returncode == 0:
        return '(no new changes)'
    subprocess.run(['git','commit','-m',message],cwd=ROOT,check=True)
    commit = subprocess.check_output(['git','rev-parse','--short','HEAD'],cwd=ROOT,text=True).strip()
    if os.environ.get('CHARFLOW_PUSH') == '1':
        # Remote synchronization is a hard gate in CI/manual runs where requested.
        # A failed push raises immediately, before any next generation step.
        env = os.environ.copy()
        env['GIT_TERMINAL_PROMPT'] = '0'
        subprocess.run(['git','push','-u','origin',
            'HEAD:refs/heads/charflow/independent-images'],
            cwd=ROOT,env=env,check=True)
    return commit


def codes():
    return [f'{a}_{i}' for a in [1,2,3] for i in range(1,9)]


def next_code():
    for code in codes():
        if not (ROOT/f'approvals/image_{code}.json').exists():
            return code
    return None


def files_for(code):
    return {k: ROOT/dir/f'image_{code}.{extension}' for k, dir, extension in [
        ('prompt','prompts','txt'),('request','requests','json'),
        ('submission','submissions','json'),('image','images','png'),
        ('result','results','json'),('approval','approvals','json')]}


def print_next(code):
    ff=files_for(code)
    print(f'OUTPUT: images/image_{code}.png | one figure | n=1 | generation from text only')
    print(f'PROMPT FILE: prompts/image_{code}.txt | SHA256 {digest(ff["prompt"])}')
    print('\nBEGIN VERBATIM PROMPT\n')
    print(ff['prompt'].read_text(encoding='utf-8'))
    print('END VERBATIM PROMPT')


def prepare(code):
    ff=files_for(code)
    if ff['image'].exists():
        raise SystemExit('Already generated; review it before advancing.')
    if ff['request'].exists():
        print('Prepared already; no need to overwrite request.'); return
    request={
        'output':f'images/image_{code}.png',
        'prepared_at':utc(),
        'input': 'standalone text prompt only; do not attach another image',
        'prompt_file':f'prompts/image_{code}.txt',
        'prompt_sha256':digest(ff['prompt']),
        'generation': {'n':1,'batching':False, 'image_references':[], 'source_image':None, 'format':'PNG'},
        'state':'prepared',
    }
    atomic_json(ff['request'],request)
    print('PREPARATION COMMIT:', git_commit([ff['request']],f'prepare: image_{code} independent single-image request'))


def submit(code, generator, model):
    ff=files_for(code)
    if not ff['request'].exists():
        raise SystemExit('Run prepare-next before submitting an image generation.')
    if digest(ff['prompt']) != json.loads(ff['request'].read_text())['prompt_sha256']:
        raise SystemExit('Prompt changed after preparation! Reject and explicitly prepare new attempt.')
    if ff['submission'].exists():
        print('Existing submission:',ff['submission']); return
    sub={'output':f'images/image_{code}.png', 'submitted_at':utc(), 'generator':generator,
         'model':model,'n':1,'input_prompt_sha256':digest(ff['prompt']),
         'no_input_images':True,'no_batch':True}
    atomic_json(ff['submission'],sub)
    print('SUBMISSION COMMIT:',git_commit([ff['submission']],f'submit: image_{code} independent generation'))


def import_image(code, source, provenance, model='unspecified'):
    ff=files_for(code)
    if not ff['submission'].exists():
        raise SystemExit('Need submission record before import. Use submit-next.')
    if ff['image'].exists():
        raise SystemExit('Refusing to overwrite an existing image.')
    source=Path(source)
    data=source.read_bytes()
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise SystemExit('Expected a PNG. No conversions of earlier results are allowed.')
    # Pillow used to validate image integrity and enforce single source file.
    try:
        from PIL import Image
        im = Image.open(BytesIO(data)); im.verify()
        im = Image.open(BytesIO(data)); w,h = im.size
    except ImportError:
        w=h=None
    ff['image'].write_bytes(data)
    result={'output':f'images/image_{code}.png','captured_at':utc(),
            'file_sha256':digest(ff['image']),'byte_count':len(data),
            'dimensions':[w,h], 'source_file':str(source),
            'claimed_provenance':provenance,'model':model,
            'provenance_warning':'Manually imported image; this metadata cannot independently prove text-only generation.'}
    atomic_json(ff['result'],result)
    print('IMAGE COMMIT:',git_commit([ff['image'],ff['result']],f'capture: image_{code} PNG + SHA256'))
    print('SHA256:',result['file_sha256'])



def void_submission(code, source, notes):
    """Preserve a nonconforming generation as rejected evidence, then reset the step.

    This NEVER imports the supplied file as an individual source image.
    """
    ff=files_for(code)
    if ff['image'].exists():
        raise SystemExit('An accepted source image exists. Use reject-next instead.')
    if not ff['submission'].exists():
        raise SystemExit('No submitted attempt to reject.')
    source=Path(source)
    if not source.is_file():
        raise SystemExit('Rejected output not found; nothing was changed.')
    stem=f'image_{code}_{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")}'
    target=ROOT/'rejected'/f'{stem}{source.suffix.lower()}'
    shutil.copy2(source,target)
    data={'rejected_at':utc(), 'expected_output':f'images/image_{code}.png',
        'rejected_output':str(target.relative_to(ROOT)),
        'file_sha256':digest(target), 'reason':notes,
        'classification':'not a valid independently generated one-character source'}
    report=target.with_suffix('.json')
    atomic_json(report,data)
    ff['submission'].unlink()
    ff['request'].unlink(missing_ok=True)
    subprocess.run(['git','add','-A','--','rejected','submissions','requests'],cwd=ROOT,check=True)
    subprocess.run(['git','commit','-m',f'reject: image_{code} nonconforming composite generation'],cwd=ROOT,check=True)
    commit=subprocess.check_output(['git','rev-parse','--short','HEAD'],cwd=ROOT,text=True).strip()
    if os.environ.get('CHARFLOW_PUSH') == '1':
        env=os.environ.copy();env['GIT_TERMINAL_PROMPT']='0'
        subprocess.run(['git','push','-u','origin',
            'HEAD:refs/heads/charflow/independent-images'],cwd=ROOT,env=env,check=True)
    print('REJECTION COMMIT:',commit,'| preserved',target.name)


def approve(code, verdict, notes):
    ff=files_for(code)
    if not ff['image'].exists() or not ff['result'].exists():
        raise SystemExit('No complete image to review.')
    data=json.loads(ff['result'].read_text())
    if digest(ff['image'])!=data['file_sha256']:
        raise SystemExit('Image digest differs from captured state.')
    if verdict=='approve':
        if not notes:
            raise SystemExit('Approval notes required.')
        obj={'approved_at':utc(),'image':f'images/image_{code}.png',
             'sha256':data['file_sha256'],'reviewer':'assistant/manual review', 'notes':notes}
        atomic_json(ff['approval'], obj)
        print('APPROVAL COMMIT:',git_commit([ff['approval']],f'approve: image_{code} reviewed source'))
    else:
        rej=(ROOT/'rejected'/f'image_{code}_{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")}.png')
        shutil.move(ff['image'],rej)
        obj={'rejected_at':utc(),'image':str(rej.relative_to(ROOT)),'notes':notes,
             'digest':digest(rej)}
        j=rej.with_suffix('.json');atomic_json(j,obj)
        ff['result'].unlink()
        ff['submission'].unlink()
        ff['request'].unlink()
        # record removals and rejected file together
        subprocess.run(['git','add','-A','--','rejected','results','submissions','requests','images'],cwd=ROOT,check=True)
        subprocess.run(['git','commit','-m',f'reject: image_{code}, retain rejected source'],cwd=ROOT,check=True)
        print('REJECTED AND RETAINED:',rej.name)


def compose(attr):
    from PIL import Image, ImageDraw, ImageFont
    ff=[files_for(f'{attr}_{i}') for i in range(1,9)]
    for f in ff:
        if not f['approval'].exists():
            raise SystemExit('Composite blocked until all eight individual source images have approvals.')
        if digest(f['image'])!=json.loads(f['approval'].read_text())['sha256']:
            raise SystemExit('Composite blocked: image digest changed since approval.')
    canvas=Image.new('RGB',(8*640,1080),(239,239,239))
    draw=ImageDraw.Draw(canvas)
    for n,f in enumerate(ff,1):
        im=Image.open(f['image']).convert('RGB')
        im.thumbnail((624,978))
        x=(n-1)*640+(640-im.width)//2
        y=(996-im.height)//2
        canvas.paste(im,(x,y))
        draw.text(((n-1)*640+300,1018),f'{n}x',fill=(25,25,25))
    out=ROOT/f'composites/image_{attr}.png'
    canvas.save(out)
    print('COMPOSITE COMMIT:',git_commit([out],f'compose: attribute {attr} approved source lineup'))


def status():
    completed=[code for code in codes() if (ROOT/f'approvals/image_{code}.json').exists()]
    generated=[code for code in codes() if (ROOT/f'images/image_{code}.png').exists()]
    now=next_code()
    print('Completed approvals:',len(completed),'/24')
    print('Generated source PNGs:',len(generated),'/24')
    print('Next:',f'image_{now}.png' if now else '(complete)')
    if now:
        ff=files_for(now)
        print('Current stage:', 'review' if ff['image'].exists() else 'submitted' if ff['submission'].exists() else 'prepared' if ff['request'].exists() else 'unprepared')
    print('Git remote:')
    subprocess.run(['git','remote','-v'],cwd=ROOT)


def audit():
    for code in codes():
        ff=files_for(code)
        state='APPROVED' if ff['approval'].exists() else 'GENERATED' if ff['image'].exists() else 'SUBMITTED' if ff['submission'].exists() else 'PREPARED' if ff['request'].exists() else '-'
        dg=digest(ff['image'])[:12] if ff['image'].exists() else '-'
        print(f'image_{code:<4} {state:<10} png={dg}')


def generate_one(code):
    # Each invocation triggers exactly one image request with one independent text-only prompt.
    if not os.environ.get('OPENAI_API_KEY'):
        raise SystemExit('OPENAI_API_KEY is not set. Use import-next for images generated in ChatGPT.')
    print_next(code)
    if input('Type GENERATE to authorize exactly one new billable request: ')!='GENERATE':
        raise SystemExit('Cancelled before submission.')
    model=os.environ.get('CHARFLOW_IMAGE_MODEL','gpt-image-1')
    try:
        from openai import OpenAI
    except ImportError:
        raise SystemExit('Install optional dependency: python -m pip install openai')
    prepare(code)
    submit(code,'OpenAI Images API, fresh text-only generation',model)
    ff=files_for(code)
    try:
        client=OpenAI()
        response=client.images.generate(model=model,prompt=ff['prompt'].read_text(encoding='utf-8'),n=1,size='1024x1536',quality='high')
        data=base64.b64decode(response.data[0].b64_json)
        tmp=ROOT/'images'/'temporary_generation.png';tmp.write_bytes(data)
        import_image(code,tmp,'OpenAI API, standalone text-only prompt, n=1',model)
        tmp.unlink(missing_ok=True)
    except Exception as exc:
        f=ROOT/f'failures/image_{code}_{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")}.json'
        atomic_json(f,{'failure_at':utc(),'error_class':type(exc).__name__,'error':str(exc)[:1000]})
        print('FAILURE COMMIT:',git_commit([f],f'failure: image_{code} API request'))
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='cmd',required=True)
    for c in ['status','next','prepare-next','submit-next','generate-next','audit']:
        sub.add_parser(c)
    ii=sub.add_parser('import-next');ii.add_argument('path');ii.add_argument('--source',required=True);ii.add_argument('--model',default='unknown')
    aa=sub.add_parser('approve-next');aa.add_argument('--notes',required=True)
    rr=sub.add_parser('reject-next');rr.add_argument('--notes',required=True)
    vv=sub.add_parser('void-next');vv.add_argument('path');vv.add_argument('--notes',required=True)
    cc=sub.add_parser('compose');cc.add_argument('--attribute',type=int,choices=[1,2,3],required=True)
    args=p.parse_args()
    if args.cmd=='status':return status()
    if args.cmd=='audit':return audit()
    if args.cmd=='compose':return compose(args.attribute)
    code=next_code()
    if code is None:raise SystemExit('All 24 images approved.')
    if args.cmd=='next':return print_next(code)
    if args.cmd=='prepare-next':return prepare(code)
    if args.cmd=='submit-next':return submit(code,'ChatGPT image_gen (manual import required)','ChatGPT image generation')
    if args.cmd=='generate-next':return generate_one(code)
    if args.cmd=='void-next':return void_submission(code,args.path,args.notes)
    if args.cmd=='import-next':return import_image(code,args.path,args.source,args.model)
    if args.cmd=='approve-next':return approve(code,'approve',args.notes)
    if args.cmd=='reject-next':return approve(code,'reject',args.notes)

if __name__=='__main__':main()
