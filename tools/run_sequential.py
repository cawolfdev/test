"""Thin entry point. All functionality is in reusable wolf_orbit modules."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from wolf_orbit.texture_orbit import execute,make_comparison
if __name__=='__main__':
    results=execute(ROOT)
    print('Angles:', [r['degree'] for r in results])
    print('Novel texels:', [r['new_texels'] for r in results])
    print('Rendered:',make_comparison(ROOT))
