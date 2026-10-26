"""Generic filesystem and image metadata; no orbit-specific policy."""
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        return image.size


def copy_file(source: Path, destination: Path) -> Path:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def write_json(path: Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    temp.replace(path)


def read_json(path: Path, default: dict | None = None) -> dict:
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else (default or {})
