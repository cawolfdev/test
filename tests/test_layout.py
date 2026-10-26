from pathlib import Path
import json
from PIL import Image
from src.orbit.core import sha256

REPO=Path(__file__).resolve().parents[1]


def test_current_file_structure_and_rejected_evidence():
    assert (REPO/'FILESYSTEM.md').is_file()
    assert (REPO/'output/README.md').is_file()
    assert not (REPO/'outputs').exists()
    assert not (REPO/'evidence/attempts').exists()
    manifest=json.loads((REPO/'evidence/rejected.json').read_text())
    assert len(manifest['attempts'])>=17
    for entry in manifest['attempts']:
        p=REPO/'evidence'/entry['evidence_path']
        assert p.exists()
        assert p.parts[-2] in {'montage','viewpoint','unverified'}
        assert sha256(p)==entry['sha256']


def test_five_individual_hd_geometric_checkpoints():
    for a in (0,30,60,90,120):
        p=REPO/'output/orbit_000_120'/f'{a:03d}'/'geometry_native_1080x1920.png'
        with Image.open(p) as img:
            assert img.width>1000 and img.height>1000
