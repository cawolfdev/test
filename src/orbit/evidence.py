"""Lossless evidence of unaccepted generations and 3D visibility diagnostics."""
from __future__ import annotations
from pathlib import Path
from shutil import copy2
from dataclasses import dataclass, asdict
from PIL import Image
import numpy as np
from .core import sha256,save_json,read_json
from .render import Renderer,load_fixed_mesh
from .domain import OrbitSpec
from .visibility import decode_visibility, visibility_vertex_colors

@dataclass(frozen=True)
class AttemptEvidence:
    id: str
    source_filename: str
    evidence_path: str
    sha256: str
    width: int
    height: int
    disposition: str
    reason: str


def record_rejected_attempts(repository:Path, originals:list[Path]) -> dict:
    """Copy unaccepted image files exactly, deduplicating references and prior copies."""
    reference_hashes={sha256(x) for x in (repository/'assets/references').glob('*.png')}
    destination=repository/'evidence/rejected/unverified'
    destination.mkdir(parents=True,exist_ok=True)
    seen=set()
    entries=[]
    for source in sorted(originals,key=lambda p:p.name):
        if not source.is_file():raise FileNotFoundError(source)
        digest=sha256(source)
        if digest in seen or digest in reference_hashes:continue
        seen.add(digest)
        ident=f'attempt_{len(entries)+1:03d}'
        file=destination/f'{ident}{source.suffix.lower()}'
        copy2(source,file)
        if sha256(file)!=digest:raise RuntimeError('Evidence copy corrupted')
        with Image.open(file) as im:w,h=im.size
        reason=('Multi-view labeled collage rather than independent full-frame image'
                if 'collage_montage' in source.name else
                'Unconstrained rear perspective/head turn; camera-only pose not confirmed'
                if 'outdoor_landscape_' in source.name else
                'Exploratory generation without verified 3D correspondence or native photo provenance')
        entries.append(asdict(AttemptEvidence(
            id=ident,source_filename=source.name,evidence_path=f'rejected/unverified/{file.name}',
            sha256=digest,width=w,height=h,disposition='NOT_ACCEPTED_AS_ORBIT_CHECKPOINT',reason=reason)))
    manifest={'project':'wildlife-bodybuilder','source':'available historical generation files',
              'classification':'unaccepted checkpoint attempts; some useful as visual explorations',
              'original_bytes_preserved':True,'count':len(entries),'attempts':entries}
    save_json(repository/'evidence/rejected.json',manifest)
    return manifest


def render_all_visibility_diagnostics(repository:Path, *,spec:OrbitSpec=OrbitSpec()) -> list[dict]:
    mesh=load_fixed_mesh(repository/'assets/geometry/fixed_pose_proxy.glb')
    renderer=Renderer(mesh,spec)
    root=repository/'output/orbit_000_120'
    output=repository/'evidence/visibility'
    output.mkdir(parents=True,exist_ok=True)
    evidence=[]
    for angle in spec.angles:
        with np.load(root/f'{angle:03d}/visibility.npz',allow_pickle=False) as masks:
            visible=decode_visibility(masks['visible'],len(mesh.vertices))
            new=decode_visibility(masks['newly'],len(mesh.vertices))
        dest=output/f'angle_{angle:03d}_1080x1920.png'
        renderer.render_diagnostic(angle,dest,visibility_vertex_colors(visible,new))
        with Image.open(dest) as im:size=list(im.size)
        evidence.append({'angle':angle,'image':str(dest.relative_to(repository)),
                         'sha256':sha256(dest),'size':size,'newly_visible_vertex_samples':int(new.sum())})
        print(f'[evidence {angle:03d}°] diagnostic saved {size[0]}x{size[1]} ; {int(new.sum())} newly exposed samples',flush=True)
    save_json(repository/'evidence/visibility.json',{'method':'occlusion-aware sampled vertex visibility',
            'not_a_photographic_output':True,'count':len(evidence),'images':evidence})
    return evidence


def inspect_evidence(repository:Path) -> dict:
    attempts=read_json(repository/'evidence/rejected.json')
    visibility=read_json(repository/'evidence/visibility.json')
    if len(visibility['images'])!=9:raise ValueError('Expected nine visibility diagnostic frames')
    for entry in attempts['attempts']:
        image=repository/'evidence'/entry['evidence_path']
        if not image.is_file() or sha256(image)!=entry['sha256']:raise ValueError(f'Lost attempt: {image}')
    for entry in visibility['images']:
        image=repository/entry['image']
        if not image.is_file() or sha256(image)!=entry['sha256']:raise ValueError(f'Lost diagnostic: {image}')
    for angle in (0,60):
        for name in (f'registration_{angle:03d}.json',f'registration_{angle:03d}_1080x1920.png',
                     f'reference_mask_{angle:03d}.png'):
            if not (repository/'output/registration'/name).is_file():raise ValueError(f'Missing registration evidence {name}')
    return {'historical_attempts':len(attempts['attempts']),
            'visibility_diagnostics':len(visibility['images']),
            'registration_diagnostics':2,'all_digests_checked':True}
