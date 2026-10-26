"""Pure domain policy: fixed-pose orbit progression and candidate acceptance.

Never equate a geometry guide with a photographic deliverable. The reference
supplies identity/pose guidance; 0 degrees is a generated output checkpoint.
"""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OrbitSpec:
    target: int = 120
    step: int = 15
    min_edge: int = 1001  # HD is strictly > 1000 px on BOTH axes.
    guide_size: tuple[int, int] = (1920, 1755)


def angles(spec: OrbitSpec) -> tuple[int, ...]:
    if spec.step <= 0 or not 0 <= spec.target <= 180 or spec.target % spec.step:
        raise ValueError('The target must lie in 0..180 and divide into whole positive steps')
    if spec.min_edge <= 1000 or min(spec.guide_size) <= 1000:
        raise ValueError('HD size must exceed 1000 on both axes')
    return tuple(range(0, spec.target + 1, spec.step))


def next_angle(spec: OrbitSpec, frames: list[dict]) -> int | None:
    schedule = angles(spec)
    if len(frames) > len(schedule):
        raise ValueError('More frames than orbit positions')
    for expected, frame in zip(schedule, frames):
        if frame['angle'] != expected:
            raise ValueError('Frames must be registered in consecutive camera order')
    if frames and frames[-1]['review'] != 'accepted':
        raise ValueError('The previous angle requires visual approval')
    return schedule[len(frames)] if len(frames) < len(schedule) else None


def validate_candidate(spec: OrbitSpec, frames: list[dict], angle: int,
                       dimensions: tuple[int, int], origin: str, reviewed: bool):
    expected = next_angle(spec, frames)
    if expected is None or angle != expected:
        raise ValueError(f'Expected next angle {expected}, got {angle}')
    if origin != 'independent_generation':
        raise ValueError('Frames must be independently rendered photographs, not guide/crop/upscale')
    if min(dimensions) < spec.min_edge:
        raise ValueError(f'HD requires both image dimensions > 1000; received {dimensions}')
    if not reviewed:
        raise ValueError('Photographic candidate needs explicit visual acceptance')


def camera_request(spec: OrbitSpec, frames: list[dict]) -> dict:
    angle = next_angle(spec, frames)
    if angle is None:
        return {'complete': True}
    return {
        'angle': angle,
        'previous_angle': frames[-1]['angle'] if frames else None,
        'reference': 'reference/character.png',
        'model': 'model/subject.glb',
        'guide': f'output/guides/{angle:03d}.png',
        'previous_frame': f'output/frames/{frames[-1]["angle"]:03d}.png' if frames else None,
        'requirements': 'Independent uncropped native photo >1000x1000, same stationary character and pose',
        'geometry_caveat': 'The existing GLB is a coarse proxy, not a fitted anatomical mesh',
    }
