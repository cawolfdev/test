"""Release entrypoint; reuses audited domain and archive adapters."""
import argparse
from pathlib import Path
from src.orbit.release import release


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--version',default='v0001')
    parser.add_argument('--out',default='/mnt/data')
    args=parser.parse_args()
    result=release(Path(__file__).resolve().parent,Path(args.out),version=args.version)
    for kind,path in sorted(result.items()):
        print(f'{kind}: {path}')


if __name__=='__main__':
    main()
