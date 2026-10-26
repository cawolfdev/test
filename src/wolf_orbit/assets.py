"""Reuse source material before writing or re-encoding anything."""
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image, ImageChops
from .geometry import ANGLES


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def pixel_equal(left, right):
    with Image.open(left) as a, Image.open(right) as b:
        if a.size != b.size:
            return False
        return ImageChops.difference(a.convert('RGB'), b.convert('RGB')).getbbox() is None


def copy_if_different(src, dst):
    src, dst = Path(src), Path(dst)
    if dst.exists() and sha256(src) == sha256(dst):
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def extract_atlas(root, replace=False):
    """Non-generative crop operation; won't overwrite reusable files by default."""
    root = Path(root)
    cfg = json.loads((root/'atlas_layout.json').read_text())
    source = root / cfg['source']
    if not source.exists():
        raise FileNotFoundError(source)
    done = []
    with Image.open(source) as atlas:
        for label, coordinates in cfg['crops'].items():
            angle = int(label)
            if angle not in ANGLES or angle in (0,60):
                raise ValueError('Atlas crops cannot replace an anchor')
            dst = root/'images'/f'{angle:03d}_clockwise.png'
            region = atlas.crop(tuple(coordinates))
            # Never reprocess existing files whose pixels already match.
            if dst.exists() and not replace:
                with Image.open(dst) as old:
                    if old.size == region.size and ImageChops.difference(old.convert('RGB'), region.convert('RGB')).getbbox() is None:
                        done.append((angle,'reused'))
                        continue
                done.append((angle,'kept-existing'))
                continue
            region.save(dst)
            done.append((angle,'extracted'))
    for angle, name in [(0,'00_front_reference.png'), (60,'60_intermediate_reference.png')]:
        changed = copy_if_different(root/'references'/name, root/'images'/f'{angle:03d}_clockwise.png')
        done.append((angle,'restored-anchor' if changed else 'reused-anchor'))
    return sorted(done)
