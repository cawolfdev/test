"""Machine-checkable invariants; not an invented claim of 3D fidelity."""
from pathlib import Path
from PIL import Image
from .geometry import ANGLES, Orbit
from .assets import sha256, pixel_equal


def validate(root):
    root = Path(root)
    findings=[]
    def check(name, condition, critical=True):
        findings.append({'check': name, 'passed': bool(condition), 'critical': critical})
    files=[]
    for angle in ANGLES:
        p=root/'images'/f'{angle:03d}_clockwise.png'
        check(f'image_exists_{angle:03d}', p.is_file())
        if p.is_file():
            with Image.open(p) as im:
                w,h=im.size
                check(f'image_dimensions_{angle:03d}', w>150 and h>300)
                check(f'nonempty_file_{angle:03d}', p.stat().st_size>20000)
                files.append((angle,p,w,h))
    check('nine_step_sequence', len(files)==9)
    check('anchor_0_pixel_identity',pixel_equal(root/'images'/'000_clockwise.png',root/'references'/'00_front_reference.png'))
    check('anchor_60_pixel_identity',pixel_equal(root/'images'/'060_clockwise.png',root/'references'/'60_intermediate_reference.png'))
    check('fixed_subject_heading', all(Orbit(a).subject_facing==(0.,1.,0.) for a in ANGLES))
    check('camera_0_front', abs(Orbit(0).position[0])<1e-8 and Orbit(0).position[1]>0)
    check('camera_90_right', Orbit(90).position[0]>0 and abs(Orbit(90).position[1])<1e-8)
    check('camera_120_rear_quadrant', Orbit(120).position[0]>0 and Orbit(120).position[1]<0)
    # Resolution discrepancies are quality warnings, not fabricated geometric proof.
    lowres=[a for a,p,w,h in files if w<500]
    check('uniform_full_resolution',not bool(lowres),critical=False)
    return {'passed':all(f['passed'] for f in findings if f['critical']),
            'source_anchors':{'0':sha256(root/'references'/'00_front_reference.png'),'60':sha256(root/'references'/'60_intermediate_reference.png')},
            'warnings':(['Seven atlas extracts have lower spatial resolution than the anchors.'] if lowres else []) + [
            'Visual azimuth cannot be calibrated from an AI image atlas. A real 3D model is required for physically accurate camera rotation.',
            'Identity, exact anatomy and pose cannot be verified across generated photographic views.'
            ], 'checks': findings}
