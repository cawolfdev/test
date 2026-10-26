"""Orbit application service: compose generic storage, geometric rendering and domain policy.

One working state under output/. Git, not per-run directories, retains revisions.
The source character photograph is a REFERENCE, never copied as frame 000.
"""
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
from .assets import copy_file, image_size, read_json, sha256, write_json
from .hd_orbit import OrbitSpec, angles, camera_request, next_angle, validate_candidate
from .render import render_geometry
from .surface import View, cast_visible_surface


DEFAULT_SPEC = OrbitSpec()


def paths(root: Path) -> dict[str, Path]:
    base = Path(root)
    return {
        'reference': base / 'reference' / 'character.png',
        'model': base / 'model' / 'subject.glb',
        'state': base / 'output' / 'state.json',
        'frames': base / 'output' / 'frames',
        'guides': base / 'output' / 'guides',
        'generatedat': base / 'generatedat.txt',
    }


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def state_for(root: Path, spec: OrbitSpec = DEFAULT_SPEC) -> dict:
    p = paths(root)
    if not p['reference'].is_file() or not p['model'].is_file():
        raise FileNotFoundError('Provide reference/character.png and model/subject.glb')
    return {
        'reference_sha256': sha256(p['reference']),
        'model_sha256': sha256(p['model']),
        'angles': list(angles(spec)), 'frames': [], 'rejection': None,
    }


def prepare(root: Path, spec: OrbitSpec = DEFAULT_SPEC, *, reset: bool = False) -> dict:
    p = paths(root)
    expected = state_for(root, spec)
    if reset and p['state'].exists():
        import shutil
        shutil.rmtree(p['state'].parent)
    current = read_json(p['state'])
    if current and any(current.get(k) != expected[k]
                       for k in ('reference_sha256', 'model_sha256', 'angles')):
        raise ValueError('Reference/model or orbit spec changed; use prepare --reset')
    if not current:
        write_json(p['state'], expected)
        p['generatedat'].write_text(timestamp() + '\n', encoding='utf-8')
        current = expected
    return current


def render_guide(root: Path, angle: int, spec: OrbitSpec = DEFAULT_SPEC) -> Path:
    p = paths(root)
    if angle not in angles(spec):
        raise ValueError('Angle outside configured schedule')
    target = p['guides'] / f'{angle:03d}.png'
    if target.exists():
        return target
    frame = cast_visible_surface(angle, View(width=spec.guide_size[0], height=spec.guide_size[1]))
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(render_geometry(frame)).save(target)
    return target


def guides(root: Path, spec: OrbitSpec = DEFAULT_SPEC) -> tuple[Path, ...]:
    prepare(root, spec)
    return tuple(render_guide(root, angle, spec) for angle in angles(spec))


def next_request(root: Path, spec: OrbitSpec = DEFAULT_SPEC) -> dict:
    data = prepare(root, spec)
    return camera_request(spec, data['frames'])


def accept(root: Path, angle: int, image: Path, *, reviewed: bool,
           spec: OrbitSpec = DEFAULT_SPEC, origin: str = 'independent_generation') -> dict:
    data = prepare(root, spec)
    size = image_size(image)
    validate_candidate(spec, data['frames'], angle, size, origin, reviewed)
    target = paths(root)['frames'] / f'{angle:03d}.png'
    if target.exists():
        raise FileExistsError(f'Already accepted: {target}')
    copy_file(image, target)
    record = {'angle': angle, 'path': str(target.relative_to(root)),
              'size': list(size), 'sha256': sha256(target),
              'review': 'accepted', 'origin': origin}
    data['frames'].append(record)
    data['rejection'] = None
    write_json(paths(root)['state'], data)
    return record


def reject(root: Path, angle: int, reason: str, spec: OrbitSpec = DEFAULT_SPEC) -> dict:
    data = prepare(root, spec)
    if angle != next_angle(spec, data['frames']):
        raise ValueError('Can only reject the currently requested angle')
    data['rejection'] = {'angle': angle, 'reason': reason}
    write_json(paths(root)['state'], data)
    return data['rejection']


def status(root: Path, spec: OrbitSpec = DEFAULT_SPEC) -> dict:
    data = prepare(root, spec)
    next_item = camera_request(spec, data['frames'])
    return {'accepted_angles': [frame['angle'] for frame in data['frames']],
            'next': next_item, 'complete': next_item.get('complete', False),
            'last_rejection': data['rejection'],
            'geometry_is_proxy_only': True}
