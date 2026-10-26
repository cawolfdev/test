"""CLI entrypoint: rendering/validation are implemented in reusable modules."""
import argparse
from pathlib import Path
from src.orbit.domain import OrbitSpec
from src.orbit.pipeline import run_orbit


def main() -> None:
    parser = argparse.ArgumentParser(description='Fixed-body camera orbit; native geometry checkpoints')
    parser.add_argument('--through',type=int,default=120,help='last checkpoint to render')
    args=parser.parse_args()
    print(run_orbit(Path(__file__).resolve().parent,spec=OrbitSpec(),stop_after=args.through))


if __name__=='__main__':
    main()
