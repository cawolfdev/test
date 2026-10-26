"""CLI orchestration only: reusable business operations live in orbit_pipeline."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from wolf_orbit.orbit_pipeline import RunSpec, geometry_guide, geometry_sequence, audit, next_request, prepare, progress, record_rejection


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('prepare', 'guide', 'all-guides', 'audit', 'next', 'reject', 'status'))
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--source', type=Path)
    parser.add_argument('--model', type=Path)
    parser.add_argument('--image', type=Path)
    parser.add_argument('--angle', type=int, default=15)
    args = parser.parse_args()
    spec = RunSpec()
    if args.command == 'prepare':
        if args.source is None or args.model is None:
            parser.error('prepare needs --source and --model')
        result = prepare(args.project, args.source, args.model, spec)
    elif args.command == 'guide':
        result = str(geometry_guide(args.project, args.angle, spec))
    elif args.command == 'all-guides':
        result = tuple(map(str, geometry_sequence(args.project, spec)))
    elif args.command == 'reject':
        if args.image is None: parser.error('reject needs --image')
        result = record_rejection(args.project, args.angle, args.image,
                    ('native width below 1920px', 'view rotates too far relative to specified 15-degree step'), spec)
    elif args.command == 'audit':
        result = audit(args.project, spec)
    elif args.command == 'next':
        result = next_request(args.project, spec)
    else:
        result = progress(args.project, spec)
    print(result)


if __name__ == '__main__':
    main()
