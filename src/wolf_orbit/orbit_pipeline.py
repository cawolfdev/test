"""Domain-level composition for source-locked, native-HD camera orbit runs.

This module deliberately delegates hashing, file copying, ray casting and image
validation to existing lower layers. Geometric guides are not photographic frames.
"""
from dataclasses import asdict, dataclass
from pathlib import Path
import json
from .assets import copy_if_different, sha256
from .hd_orbit import OrbitJob, angles, dependencies, load_records, register_frame, status, task_request
from .surface import View
from .preview import contact_sheet


@dataclass(frozen=True)
class RunSpec:
    version: str = 'v0002'
    target_angle: int = 120
    step_angle: int = 15
    native_min_width: int = 1920
    native_min_height: int = 1080
    guide_width: int = 1920
    guide_height: int = 1755


def run_root(project: Path, spec: RunSpec) -> Path:
    return Path(project) / 'runs' / spec.version


def job_for(run: Path, spec: RunSpec) -> OrbitJob:
    return OrbitJob(source=run / 'source.png', target_angle=spec.target_angle,
                    step_angle=spec.step_angle, model=run / 'proxy.glb',
                    min_generated_width=spec.native_min_width,
                    min_generated_height=spec.native_min_height)


def prepare(project: Path, source: Path, model: Path, spec: RunSpec) -> dict:
    """Copy immutable inputs and register true source as checkpoint zero only."""
    root = run_root(project, spec)
    root.mkdir(parents=True, exist_ok=True)
    for existing, expected in [(root / 'source.png', source), (root / 'proxy.glb', model)]:
        if existing.exists() and sha256(existing) != sha256(expected):
            raise ValueError(f'Immutable run input changed: {existing}')
        copy_if_different(expected, existing)
    job = job_for(root, spec)
    image_record = (load_records(root) or (None,))[0]
    if image_record is None:
        register_frame(root, job, 0, job.source, 'anchor')
    evidence = dependencies(job)
    plan = {
        'version': spec.version, 'goal': 'nine independent camera views at 15-degree intervals',
        'spec': asdict(spec), 'angles': angles(job), 'inputs': evidence,
        'anchor_is_native': True,
        'anchor_meets_generated_full_hd_width': False,
        'geometry_status': 'coarse proxy; unregistered to uploaded source',
        'photographic_status': 'anchor only, other angles awaiting independent native-HD render',
        'safety': 'no atlas crops, no upscaled guides substituted for photographs',
    }
    _write_json_if_changed(root / 'plan.json', plan)
    return plan


def geometry_guide(project: Path, angle: int, spec: RunSpec) -> Path:
    """Render one selected full-size geometric guide; never synthesize a photo."""
    root = run_root(project, spec)
    job = job_for(root, spec)
    if angle not in angles(job):
        raise ValueError(f'Angle not in fixed schedule: {angle}')
    # Existing geometric raycaster reused; each requested angle is independently rasterized.
    from .surface import human_faced_proxy, cast_visible_surface
    from .texture_orbit import render_geometry
    from PIL import Image
    path = root / 'hd' / 'guides' / f'{angle:03d}.png'
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        frame = cast_visible_surface(angle, View(width=spec.guide_width, height=spec.guide_height), human_faced_proxy())
        Image.fromarray(render_geometry(frame, human_faced_proxy())).save(path)
    return path


def geometry_sequence(project: Path, spec: RunSpec) -> tuple[Path, ...]:
    """Domain composition: reuse single-angle renderer and common preview adapter."""
    images = tuple(geometry_guide(project, angle, spec)
                   for angle in angles(job_for(run_root(project, spec), spec)))
    root = run_root(project, spec)
    contact_sheet(images, root / 'preview' / 'geometry.png',
                  columns=3, cell=(380, 345),
                  caption=lambda index, _path: f'{index * spec.step_angle:03d}° [3D GUIDE, NOT PHOTO]')
    return images


def audit(project: Path, spec: RunSpec) -> dict:
    """A machine-readable inventory: no preview is counted as a photograph."""
    root = run_root(project, spec)
    frames = {r['angle']: r for r in load_records(root)}
    records = []
    for angle in angles(job_for(root, spec)):
        guide = root / 'hd' / 'guides' / f'{angle:03d}.png'
        frame = frames.get(angle)
        records.append({
            'angle': angle,
            'geometry_guide': str(guide.relative_to(root)) if guide.exists() else None,
            'geometry_sha256': sha256(guide) if guide.exists() else None,
            'native_photograph': frame.get('path') if frame else None,
            'image_sha256': frame.get('sha256') if frame else None,
            'photographic_review': frame.get('visual_review') if frame else 'missing',
            'camera_registration': 'unverified',
        })
    document = {'run': spec.version, 'source_sha256': sha256(root / 'source.png'),
                'model_sha256': sha256(root / 'proxy.glb'), 'checkpoints': records,
                'photo_complete': all(x['photographic_review'] in ('accepted','anchor') for x in records),
                'model_fitted_to_source': False}
    _write_json_if_changed(root / 'report.json', document)
    return document


def next_request(project: Path, spec: RunSpec) -> dict:
    root = run_root(project, spec)
    job = job_for(root, spec)
    history = load_records(root)
    deps = dependencies(job)
    request = task_request(job, history, source_digest=deps['source_sha256'], model_digest=deps['model_sha256'])
    request.update(native_min_width=spec.native_min_width,
                   native_min_height=spec.native_min_height,
                   source_coordinate_angle=0,
                   geometry_guide_quality='unregistered coarse ellipsoid proxy; geometric conditioning only',
                   full_resolution='No crop, no synthetic upscale, independent render')
    return request


def _write_json_if_changed(path: Path, document: dict) -> None:
    content = json.dumps(document, indent=2, sort_keys=True) + '\n'
    if not path.exists() or path.read_text() != content:
        path.write_text(content)


def progress(project: Path, spec: RunSpec) -> dict:
    root = run_root(project, spec)
    st = status(root, job_for(root, spec))
    st['version'] = spec.version
    st['geometry_guide_count'] = len(tuple((root / 'hd' / 'guides').glob('*.png'))) if (root / 'hd' / 'guides').exists() else 0
    st['photographic_result_count'] = len(st['registered'])
    return st
