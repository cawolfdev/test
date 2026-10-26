"""Full-resolution camera-orbit use case built from shared plumbing.

Planning and validation are pure. File I/O occurs in register_frame and render_guides.
A registered image is NOT claimed to be metrically calibrated by these checks.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import json
import shutil
from PIL import Image
from .assets import sha256
from .surface import View, cast_visible_surface, human_faced_proxy
from .texture_orbit import render_geometry

Provenance = Literal['anchor', 'independent_generation']


@dataclass(frozen=True)
class OrbitJob:
    source: Path
    target_angle: int = 120
    step_angle: int = 15
    min_edge: int = 1024
    model: Path | None = None
    min_generated_width: int = 0
    min_generated_height: int = 0


def angles(job: OrbitJob) -> tuple[int, ...]:
    """Pure validated clockwise schedule; rejects any skipped final increment."""
    if job.step_angle <= 0 or job.target_angle < 0 or job.target_angle > 180:
        raise ValueError('Expected step > 0 and a target between 0 and 180')
    if job.target_angle % job.step_angle:
        raise ValueError('Target must be divisible by step: final segment must not drift')
    return tuple(range(0, job.target_angle + 1, job.step_angle))


def frame_requirements(path: Path, minimum: int) -> dict:
    """Pure in spirit: describe one already-existing image; no modification."""
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        width, height = im.size
    if min(width, height) < minimum:
        raise ValueError(f'Native input image {width}x{height} is below minimum edge {minimum}')
    return {'width': width, 'height': height, 'sha256': sha256(path)}


def check_stage(records: tuple[dict, ...], angle: int, metadata: dict, job: OrbitJob) -> None:
    """Pure domain validation, independent of file storage and rendering adapter."""
    schedule = angles(job)
    if angle not in schedule or angle != schedule[len(records)]:
        raise ValueError('Angle must be the next consecutive checkpoint')
    if metadata['provenance'] != ('anchor' if angle == 0 else 'independent_generation'):
        raise ValueError('Each nonzero angle requires an independently generated full-frame image')
    if metadata.get('derived_from_crop', False):
        raise ValueError('Atlas crops and thumbnails cannot serve as orbit frames')
    if min(metadata['width'], metadata['height']) < job.min_edge:
        raise ValueError('Image is below minimum native pixel edge')
    if angle > 0 and (metadata['width'] < job.min_generated_width or
                      metadata['height'] < job.min_generated_height):
        raise ValueError('Independent image is below requested full-HD dimensions')
    if records:
        if metadata['previous_sha256'] != records[-1]['sha256']:
            raise ValueError('Checkpoint must depend on immediate predecessor')
        if metadata['sha256'] in {r['sha256'] for r in records}:
            raise ValueError('Duplicate pixels cannot pass as a new angle')
    elif metadata['previous_sha256'] is not None:
        raise ValueError('First checkpoint cannot have a predecessor')


def task_request(job: OrbitJob, records: tuple[dict, ...], *,
                 source_digest: str, model_digest: str | None = None) -> dict:
    """Pure business-case request. Never invent a finished image or skip an angle.

    Rendering is an injected external operation; this task only states the evidence
    required for the next native-resolution image. The immutable previous frame is
    referenced by content digest, not mutable filename or atlas index.
    """
    schedule = angles(job)
    if len(records) >= len(schedule):
        raise ValueError('All checkpoints are already registered')
    if records and records[-1]['visual_review'] not in ('accepted', 'anchor'):
        raise ValueError('Previous frame lacks positive visual review')
    if any(record.get('source_sha256') not in (None, source_digest) or
           record.get('model_sha256') not in (None, model_digest) for record in records):
        raise ValueError('Immutable source/model changed during this orbit')
    angle = schedule[len(records)]
    return {'angle': angle, 'step': job.step_angle,
            'previous_angle': schedule[len(records)-1] if records else None,
            'previous_sha256': records[-1]['sha256'] if records else None,
            'source_sha256': source_digest, 'model_sha256': model_digest,
            'min_native_edge': job.min_edge, 'required_origin':
            'anchor' if not records else 'independent_generation',
            'geometry_guide': f'hd/guides/{angle:03d}.png',
            'candidate_state': 'awaiting_independent_render'}


def dependencies(job: OrbitJob) -> dict:
    """Read hashes only at I/O boundary and pass immutable values to domain logic."""
    return {'source_sha256': sha256(job.source),
            'model_sha256': sha256(job.model) if job.model is not None else None}


def verify_dependencies(records: tuple[dict, ...], deps: dict) -> None:
    """Keep the whole sequence on the original scene and model revision."""
    for r in records:
        for key, value in deps.items():
            if r.get(key) != value:
                raise ValueError(f'Run dependency mismatch for {key}; create a new version')


def load_records(root: Path) -> tuple[dict, ...]:
    index = root / 'hd' / 'sequence.json'
    return tuple(json.loads(index.read_text())) if index.exists() else ()


def register_frame(root: Path, job: OrbitJob, angle: int, image: Path,
                   provenance: Provenance, *, reviewed: bool = False,
                   derived_from_crop: bool = False) -> dict:
    """Accept one audited full-sized frame, copy it unchanged, checkpoint its hash.

    An independently generated image still requires **external visual review** for
    angle, pose, character identity and unseen-surface correctness.
    """
    root, image = Path(root), Path(image)
    current = load_records(root)
    frame = frame_requirements(image, job.min_edge)
    deps = dependencies(job)
    verify_dependencies(current, deps)
    metadata = {
        'angle': angle, 'provenance': provenance,
        'previous_sha256': current[-1]['sha256'] if current else None,
        'derived_from_crop': derived_from_crop,
        'visual_review': 'anchor' if angle == 0 else ('accepted' if reviewed else 'unverified'),
        **deps, **frame,
    }
    check_stage(current, angle, metadata, job)
    dest = root/'hd'/'frames'/f'{angle:03d}.png'
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Do not resample, change image dimensions, or overwrite a preexisting frame.
    if dest.exists():
        raise FileExistsError(f'Frame already exists: {dest}')
    shutil.copyfile(image, dest)
    if sha256(dest) != frame['sha256']:
        dest.unlink()
        raise IOError('Frame changed during copy')
    metadata['path'] = str(dest.relative_to(root))
    records = (*current, metadata)
    (root/'hd'/'sequence.json').write_text(json.dumps(records, indent=2)+'\n')
    return metadata


def render_guides(root: Path, job: OrbitJob, view: View = View(width=1152,height=1152)) -> tuple[Path,...]:
    """Reuse the single existing raycaster for HD *geometry guides*, not photos."""
    dest = root/'hd'/'guides'
    dest.mkdir(parents=True, exist_ok=True)
    parts = human_faced_proxy()
    paths = []
    for angle in angles(job):
        path = dest/f'{angle:03d}.png'
        if not path.exists():
            frame = cast_visible_surface(angle, view, parts)
            Image.fromarray(render_geometry(frame, parts)).save(path)
        paths.append(path)
    return tuple(paths)


def status(root: Path, job: OrbitJob) -> dict:
    """Pure task-level progress summary: missing steps never implicitly pass."""
    current=load_records(root)
    schedule=angles(job)
    deps=dependencies(job)
    verify_dependencies(current, deps)
    ready=not current or current[-1]['visual_review'] in ('accepted', 'anchor')
    return {'requested_angles':schedule,
            'registered':tuple(r['angle'] for r in current),
            'next_angle':schedule[len(current)] if len(current)<len(schedule) else None,
            'ready_to_generate':ready,
            'complete':len(current)==len(schedule) and all(r['visual_review'] in ('accepted','anchor') for r in current),
            'reviewed_count':sum(r['visual_review']=='accepted' for r in current)}
