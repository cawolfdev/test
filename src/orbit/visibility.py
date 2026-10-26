"""Occlusion-aware visibility; pure NumPy projection and depth comparison.

The model remains fixed. The raster depth comes from rendering that same mesh at
one exact camera angle, so an overlapping surface cannot count as newly exposed
merely because its normal points toward the camera.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .domain import OrbitSpec, screen_right, looking_toward_camera, shared_parallel_half_height

VISIBILITY_VERSION = 1


@dataclass(frozen=True)
class VisibilityResult:
    visible: np.ndarray
    in_frame: np.ndarray
    front_facing: np.ndarray
    depth_consistent: np.ndarray


def project_orthographic(vertices: np.ndarray, angle: int, spec: OrbitSpec,
                         near: float, far: float, *, half_height: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Project world points to VTK's *bottom-origin* pixel space and 0–1 depth.

    The half-height MUST come from the *whole fixed mesh*, never a subset
    of points. Projection uses exactly the same convention as Renderer:
    fixed upright view, camera-only orbit, parallel projection, shared scale.
    """
    if not near < far:
        raise ValueError('Invalid camera clipping interval')
    h = half_height
    if h <= 0:
        raise ValueError("Invalid camera framing scale")
    aspect = spec.width / spec.height
    px = (.5 + vertices @ screen_right(angle) / (2*h*aspect)) * spec.width
    py = (.5 + (vertices[:, 2]-spec.subject_center_z) / (2*h)) * spec.height
    distance = spec.camera_distance - vertices @ looking_toward_camera(angle)
    pz = (distance-near) / (far-near)
    return px, py, pz


def depth_visible(vertices: np.ndarray, normals: np.ndarray, z_buffer: np.ndarray,
                  angle: int, spec: OrbitSpec, near: float, far: float,
                  tolerance: float = .002) -> VisibilityResult:
    """Visible if front-facing and its projected depth matches the raster surface.

    Requires actual z-buffer of the same mesh at this angle, not a normal test.
    Vertices exactly on triangle edges can be conservatively excluded by raster
    sampling; this is a *sampled* visibility map, not exact triangle visibility.
    """
    if z_buffer.shape != (spec.height, spec.width):
        raise ValueError(f'Expected {spec.height}x{spec.width} z-buffer, got {z_buffer.shape}')
    if vertices.shape != normals.shape or vertices.shape[1] != 3:
        raise ValueError('Vertices and normals must both be Nx3')
    x, y, z = project_orthographic(vertices, angle, spec, near, far,
                                  half_height=shared_parallel_half_height(vertices, spec))
    ix = np.rint(x).astype(int)
    iy = np.rint(y).astype(int)
    inside = (ix >= 0) & (ix < spec.width) & (iy >= 0) & (iy < spec.height) & (z >= 0) & (z <= 1)
    front = (normals @ looking_toward_camera(angle)) > .09
    depth = np.zeros(len(vertices), dtype=bool)
    ids = np.flatnonzero(inside & front)
    if ids.size:
        surface = z_buffer[iy[ids], ix[ids]]
        depth[ids] = (surface < 1) & (np.abs(z[ids]-surface) <= tolerance)
    return VisibilityResult(visible=inside & front & depth, in_frame=inside,
                            front_facing=front, depth_consistent=depth)


def increment_visibility(current: np.ndarray, seen: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (first-time-observed vertices, accumulated observations)."""
    if current.shape != seen.shape or current.dtype != bool or seen.dtype != bool:
        raise ValueError('Visibility masks must be matching boolean arrays')
    return current & ~seen, current | seen


def encode_visibility(mask: np.ndarray) -> np.ndarray:
    """Compact deterministic bit-packed representation of one vertex mask."""
    return np.packbits(mask.astype(np.uint8), bitorder='big')


def decode_visibility(packed: np.ndarray, length: int) -> np.ndarray:
    return np.unpackbits(packed, count=length, bitorder='big').astype(bool)


def visibility_vertex_colors(visible: np.ndarray, newly: np.ndarray) -> np.ndarray:
    """Semantic diagnostic RGB: hidden=slate, seen=blue, newly exposed=amber.

    This is a native 3D diagnostic, never a photographic deliverable.
    """
    if visible.shape!=newly.shape or np.any(newly & ~visible):
        raise ValueError('Newly exposed vertices must be a subset of visible vertices')
    result=np.empty((len(visible),3),dtype=np.uint8)
    result[:]=[87,103,116]
    result[visible]=[142,185,212]
    result[newly]=[246,182,91]
    return result
