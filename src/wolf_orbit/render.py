"""Generic rendering of geometric visibility results, distinct from photo synthesis."""
import numpy as np
from PIL import ImageColor
from .proxy import MATERIAL, scene_parts


def render_geometry(frame, parts=None):
    if parts is None:
        parts = scene_parts()
    height, width = frame.part_id.shape
    pixels = np.full((height, width, 3), (220, 225, 229), dtype=np.uint8)
    light = np.array((.45, .65, .62), dtype=np.float32)
    light /= np.linalg.norm(light)
    factor = .62 + .35 * np.clip(np.sum(frame.normal_xyz * light, axis=-1), 0, 1)
    for index, (_center, _axes, material) in enumerate(parts):
        mask = frame.part_id == index
        if mask.any():
            color = np.asarray(ImageColor.getrgb(MATERIAL[material]), dtype=np.float32)
            pixels[mask] = np.clip(color * factor[mask, None], 0, 255).astype(np.uint8)
    return pixels
