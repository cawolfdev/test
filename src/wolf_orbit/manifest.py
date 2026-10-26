"""Manifest is a complete relative index and SHA256 record of deliverables."""
from pathlib import Path
import json
from .assets import sha256
from .geometry import ANGLES, Orbit
from .validation import validate

EXCLUDED={'.git', '__pycache__', '.pytest_cache'}

def build_manifest(root):
    root=Path(root)
    files=[]
    for file in sorted(root.rglob('*')):
        if not file.is_file() or any(part in EXCLUDED for part in file.relative_to(root).parts):continue
        if file.name in ('manifest.json','validation_report.json') or file.suffix=='.pyc':continue
        files.append({'path':str(file.relative_to(root)), 'size_bytes':file.stat().st_size, 'sha256':sha256(file)})
    return {'title':'Fixed-pose human-wolf camera orbit, reuse-first project',
            'camera_angles_degrees':list(ANGLES),
            'camera_positions':{str(a):[round(v,7) for v in Orbit(a).position] for a in ANGLES},
            'fixed_subject_front_vector':list(Orbit(0).subject_facing),
            'origins':{'0':'unaltered source reference', '60':'unaltered existing intermediate', 'other':'cropped views from reused generative atlas'},
            'limitations':validate(root)['warnings'],
            'files':files}

def write_manifest(root):
    root=Path(root)
    report=validate(root)
    (root/'validation_report.json').write_text(json.dumps(report,indent=2)+'\n')
    (root/'manifest.json').write_text(json.dumps(build_manifest(root),indent=2)+'\n')
    return report
