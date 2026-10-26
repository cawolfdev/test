"""Domain contracts and pure geometry. No I/O or graphics in this module."""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Sequence
import numpy as np


@dataclass(frozen=True)
class OrbitSpec:
    start: int = 0
    stop: int = 120
    step: int = 15
    width: int = 1080
    height: int = 1920
    camera_distance: float = 8.0
    subject_center_z: float = 1.2
    framing_margin: float = 0.07

    def __post_init__(self) -> None:
        if self.step <= 0 or self.stop < self.start or (self.stop-self.start) % self.step:
            raise ValueError('Angle sequence must divide start-to-stop exactly')
        if self.width < 1080 or self.height < 1920:
            raise ValueError('Native geometric render must be at least 1080x1920')

    @property
    def angles(self) -> tuple[int, ...]:
        return tuple(range(self.start, self.stop+self.step, self.step))


def camera_position(angle_degrees: int, *, distance: float, center_z: float) -> tuple[float,float,float]:
    """0° is front (-Y), positive angles circle toward subject's +X/right."""
    radians = math.radians(angle_degrees)
    return (distance*math.sin(radians), -distance*math.cos(radians), center_z)


def screen_right(angle_degrees: int) -> np.ndarray:
    radians = math.radians(angle_degrees)
    return np.array([math.cos(radians), math.sin(radians), 0.0])


def looking_toward_camera(angle_degrees: int) -> np.ndarray:
    radians = math.radians(angle_degrees)
    return np.array([math.sin(radians), -math.cos(radians), 0.0])


def world_camera_extents(vertices: np.ndarray, spec: OrbitSpec) -> tuple[float,float]:
    """Global half-extents enforce identical scale at all viewpoints (no per-view crop)."""
    max_side = max(float(np.max(np.abs(vertices @ screen_right(a)))) for a in spec.angles)
    max_top = float(np.max(np.abs(vertices[:,2]-spec.subject_center_z)))
    return max_side, max_top


def shared_parallel_half_height(vertices: np.ndarray, spec: OrbitSpec) -> float:
    side, top = world_camera_extents(vertices, spec)
    aspect = spec.width/spec.height
    return max(top, side/aspect) / (1-spec.framing_margin)


def newly_front_facing_vertices(normals: np.ndarray, seen: np.ndarray, angle_degrees: int, threshold: float=0.09) -> np.ndarray:
    """Diagnostic only: visibility/occlusion is NOT proven by surface normals alone."""
    facing = (normals @ looking_toward_camera(angle_degrees)) > threshold
    return facing & ~seen


def photo_prompt(angle: int) -> str:
    """Domain instructions reusable by an independent photographic image-generation adapter."""
    side = 'front' if angle == 0 else 'right side' if angle == 90 else 'right rear' if angle > 90 else 'right front'
    return (
        f'ONE INDEPENDENT FULL FRAME PHOTOGRAPH at camera azimuth +{angle} degrees, {side} view; '
        'use the provided corresponding 3D camera frame as binding pose and silhouette reference, '
        'and the original front portrait for identity/appearance only. Fixed skull, neck, shoulders, '
        'hands clasped behind head, elbows spread, colossal coherent musculature, pale amber irises '
        'when eyes are visible, short-sided forward-spiked brown football-jock hair, dense natural '
        'feathered-edge stubble, dark gym shorts, cloudy lakeside overlook. '
        'Camera orbits the stationary model without the subject turning toward it. '
        'Portrait photographic realism, full frame, native >1000x1000 pixels minimum, single image only, '
        'no panel, mosaic, crop, collage, inpainting, or enlargement of an existing image.'
    )
