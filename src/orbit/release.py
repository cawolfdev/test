"""Audited repeatable deliverables; evidence and report live inside the project."""
from __future__ import annotations
from pathlib import Path
from shutil import copyfile
import re
import zipfile
from .audit import verify_orbit
from .domain import OrbitSpec
from .core import save_json,read_json,sha256
from .evidence import inspect_evidence
from .mesh_quality import measure_mesh_quality

PROJECT='wildlife-bodybuilder'
VERSION_RE=re.compile(r'v\d{4}$')


def deliverable_name(kind:str,version:str,extension:str)->str:
    if not VERSION_RE.fullmatch(version):raise ValueError('Version must be zero-padded v0001, v0002, ...')
    if not re.fullmatch(r'[a-z][a-z0-9-]*',kind):raise ValueError('Expected kebab-case deliverable role')
    if extension not in ('zip','png','json','md'):raise ValueError('Unsupported deliverable format')
    return f'{PROJECT}-{kind}-{version}.{extension}'


def _include_project(path:Path)->bool:
    parts=set(path.parts)
    return not(parts & {'__pycache__','.pytest_cache'}) and path.suffix not in ('.pyc','.tmp') and path.name!='index.lock'


def _archive(paths:list[tuple[Path,str]],target:Path)->Path:
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for source,member in sorted(paths,key=lambda p:p[1]):
            archive.write(source,arcname=member)
    return target


def generate_report(repository:Path,version:str)->dict:
    """Source of truth for both embedded and exported reports."""
    orbit=verify_orbit(repository,spec=OrbitSpec())
    evidence=inspect_evidence(repository)
    quality=measure_mesh_quality(repository/'assets/geometry/fixed_pose_proxy.glb')
    registrations=[read_json(repository/f'output/registration/registration_{angle:03d}.json') for angle in (0,60)]
    accepted=orbit['independent_full_hd_photographs']
    report={'project':PROJECT,'version':version,
            'goal':'Geometry-constrained native-HD independent photographs every 15 degrees around one stationary subject',
            'orbit':orbit,
            'mesh_quality':quality,
            'registrations':registrations,
            'evidence':evidence,
            'quality_gates':{
                'nine_geometry_checkpoints_verified':orbit['geometry_checkpoints']==9,
                'reference_masks_independently_reviewed':False,
                'silhouette_gate_000_passed':registrations[0]['quality_gate']['passed'],
                'silhouette_gate_060_passed':registrations[1]['quality_gate']['passed'],
                'anatomical_mesh_photo_ready':quality['photo_ready'],
                'accepted_native_hd_photographic_checkpoints':accepted},
            'next_action':'Fit a complete, rigged 3D body and head against both reference silhouettes; rerun registration before attempting image synthesis',
            'release_note':'Native 3D diagnostic images are not photorealistic outputs. Rejected generations are archived unchanged.',
            'source_references':{'0':'approximate historical photographic reference, replacement not accepted', '60':'approximate historical photographic reference, replacement not accepted'},
            'remote_branch':{'repository':'cawolfdev/test','branch':'wildlife-bodybuilder-portrait','status':'branch created; not fully synchronized'}}
    # Preserve operational status without mutating files during a read-only report calculation.
    current_file=repository/'reports/current.json'
    if current_file.is_file():
        previous=read_json(current_file)
        for name in ('photographic_attempts_current', 'github_sync', 'hd_definition',
                     'photo_orbit_angles', 'photographic_viewpoints_0_30_60_90_120',
                     'last_generation', 'accepted_photographs', 'release_status'):
            if name in previous:report[name]=previous[name]
        if 'goal' in previous:report['goal']=previous['goal']
        if 'next_action' in previous:report['next_action']=previous['next_action']
    return report


def release(repository:Path,output:Path,*,version:str)->dict:
    """Publish stable-named sources, complete evidence, and verified geometry."""
    if not VERSION_RE.fullmatch(version):raise ValueError('Invalid version string')
    output.mkdir(parents=True,exist_ok=True)
    report=generate_report(repository,version)
    save_json(repository/'reports/current.json',report)
    save_json(repository/'output/orbit_000_120/verification.json',report['orbit'])
    exported={}
    overview=output/deliverable_name('overview',version,'md')
    copyfile(repository/'docs/OVERVIEW.md',overview)
    exported['overview']=overview
    report_file=output/deliverable_name('report',version,'json')
    copyfile(repository/'reports/current.json',report_file)
    exported['report']=report_file
    preview=output/deliverable_name('preview',version,'png')
    copyfile(repository/'output/orbit_000_120/120/geometry_native_1080x1920.png',preview)
    exported['preview']=preview
    visibility=output/deliverable_name('visibility',version,'png')
    copyfile(repository/'evidence/visibility/angle_120_1080x1920.png',visibility)
    exported['visibility']=visibility
    progress=repository/'evidence/progress/progress_4_panel.png'
    if progress.exists():
        dest=output/deliverable_name('progress',version,'png')
        copyfile(progress,dest)
        exported['progress']=dest
    # Pack evidence images and registration diagnostics as independent downloadable evidence.
    evidence_paths=[(p,f'{PROJECT}/{p.relative_to(repository).as_posix()}')
                    for area in (repository/'evidence',repository/'output/registration')
                    for p in area.rglob('*') if p.is_file()]
    ev=output/deliverable_name('evidence',version,'zip')
    _archive(evidence_paths,ev)
    exported['evidence']=ev
    # Save project after report/evidence are finalized: both ship inside the repository.
    project_paths=[(p,f'{PROJECT}/{p.relative_to(repository).as_posix()}')
                  for p in repository.rglob('*') if p.is_file() and _include_project(p.relative_to(repository))]
    project=output/deliverable_name('project',version,'zip')
    _archive(project_paths,project)
    exported['project']=project
    checkpoint_paths=[(p,f'{PROJECT}/{p.relative_to(repository).as_posix()}')
                      for p in (repository/'output/orbit_000_120').rglob('*') if p.is_file()]
    checkpoints=output/deliverable_name('checkpoints',version,'zip')
    _archive(checkpoint_paths,checkpoints)
    exported['checkpoints']=checkpoints
    manifest={'project':PROJECT,'version':version,
              'files':{k:{'filename':p.name,'sha256':sha256(p),'size_bytes':p.stat().st_size}
                       for k,p in sorted(exported.items())}}
    man=output/deliverable_name('manifest',version,'json')
    save_json(man,manifest)
    exported['manifest']=man
    return {kind:str(path) for kind,path in exported.items()}
