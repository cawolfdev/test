"""Thin command-line adapter. Business actions live in orbit_pipeline."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from wolf_orbit import orbit_pipeline


def main():
    parser = argparse.ArgumentParser(description='wildlife-bodybuilder: one current camera orbit')
    parser.add_argument('action', choices=('prepare', 'guides', 'next', 'accept', 'reject', 'status'))
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--image', type=Path)
    parser.add_argument('--angle', type=int, default=0)
    parser.add_argument('--reason')
    parser.add_argument('--reviewed', action='store_true')
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()
    actions = {
        'prepare': lambda: orbit_pipeline.prepare(args.root, reset=args.reset),
        'guides': lambda: [str(p) for p in orbit_pipeline.guides(args.root)],
        'next': lambda: orbit_pipeline.next_request(args.root),
        'accept': lambda: orbit_pipeline.accept(args.root, args.angle, args.image, reviewed=args.reviewed),
        'reject': lambda: orbit_pipeline.reject(args.root, args.angle, args.reason),
        'status': lambda: orbit_pipeline.status(args.root),
    }
    if args.action == 'accept' and args.image is None:
        parser.error('accept requires --image')
    if args.action == 'reject' and not args.reason:
        parser.error('reject requires --reason')
    print(json.dumps(actions[args.action](), indent=2))


if __name__ == '__main__':
    main()
