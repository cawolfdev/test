import argparse
import json
from pathlib import Path
from .assets import extract_atlas
from .preview import make_contact_sheet
from .manifest import write_manifest
from .validation import validate

def main():
    parser=argparse.ArgumentParser(description='Reproducible, reuse-first camera-orbit outputs')
    parser.add_argument('action',choices=['extract','preview','validate','manifest','all'])
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--replace',action='store_true',help='Re-extract atlas crops only, never regenerate photo content')
    args=parser.parse_args()
    if args.action in ('extract','all'):
        print('EXTRACTION',extract_atlas(args.root,args.replace))
    if args.action in ('preview','all'):
        print('CONTACT SHEET',make_contact_sheet(args.root))
    if args.action in ('manifest','all'):
        report=write_manifest(args.root)
        print('VALIDATION', 'PASS' if report['passed'] else 'FAIL')
    if args.action=='validate':
        print(json.dumps(validate(args.root),indent=2))
if __name__=='__main__':main()
