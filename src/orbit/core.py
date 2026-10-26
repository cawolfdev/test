"""General-purpose functional primitives: paths, digests, durable JSON, image provenance."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from PIL import Image


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def save_json(path: Path, obj: dict) -> None:
    """Atomic checkpoint write, safe to resume after an interrupted run."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj, sort_keys=True, indent=2)+'\n', encoding='utf-8')
    tmp.replace(path)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


@dataclass(frozen=True)
class ImageEvidence:
    path: str
    source_kind: str
    width: int
    height: int
    sha256: str


ALLOWED_IMAGE_KINDS = {'independent_native_photo', 'native_3d_render'}


def inspect_image(path: Path, *, source_kind: str) -> ImageEvidence:
    with Image.open(path) as img:
        width, height = img.size
    return ImageEvidence(str(path), source_kind, width, height, sha256(path))


def validate_deliverable(evidence: ImageEvidence, *, min_width: int=1001, min_height: int=1001) -> tuple[str, ...]:
    errors = []
    if evidence.source_kind not in ALLOWED_IMAGE_KINDS:
        errors.append('Provenance is neither an independent native image nor a native 3D render')
    if evidence.width < min_width or evidence.height < min_height:
        errors.append(f'Native resolution {evidence.width}x{evidence.height} is below {min_width}x{min_height}')
    return tuple(errors)
