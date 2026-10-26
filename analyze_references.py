"""Reproducible camera-only photographic reference registration diagnostics."""
from pathlib import Path
from src.orbit.registration import compare_reference


def main():
    r=Path(__file__).resolve().parent
    for angle,source in ((0,'front_original.png'),(60,'angle_060_original.png')):
        result=compare_reference(r/'assets/references'/source,
            r/f'outputs/orbit_000_120/{angle:03d}/geometry_native_1080x1920.png',
            angle=angle,outdir=r/'outputs/registration')
        print(f'{angle:03d}° IoU={result["alignment"]["iou"]:.3f} '+
              f'gate={"PASS" if result["quality_gate"]["passed"] else "FAIL"}')

if __name__=='__main__':main()
