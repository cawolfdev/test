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
        raise ValueError('Image is not native HD size')
    if records:
        if metadata['previous_sha256'] != records[-1]['sha256']:
            raise ValueError('Checkpoint must depend on immediate predecessor')
        if metadata['sha256'] in {r['sha256'] for r in records}:
            raise ValueError('Duplicate pixels cannot pass as a new angle')
    elif metadata['previous_sha256'] is not None:
        raise ValueError('First checkpoint cannot have a predecessor')


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
    metadata = {
        'angle': angle, 'provenance': provenance,
        'previous_sha256': current[-1]['sha256'] if current else None,
        'derived_from_crop': derived_from_crop,
        'visual_review': 'accepted' if reviewed else 'unverified',
        **frame,
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
    return {'requested_angles':schedule,'accepted':tuple(r['angle'] for r in current),
            'next_angle':schedule[len(current)] if len(current)<len(schedule) else None,
            'complete':len(current)==len(schedule),
            'reviewed_count':sum(r['visual_review']=='accepted' for r in current)}
