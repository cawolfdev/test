"""Thin adapter for reusable HD orbit domain operations."""
import argparse
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from wolf_orbit.hd_orbit import OrbitJob,register_frame,render_guides,status


def main():
    parser=argparse.ArgumentParser(description='Native-HD independently generated image checkpoint chain')
    parser.add_argument('action', choices=['status','guides','register'])
    parser.add_argument('--source',type=Path,default=ROOT/'references'/'00_front_reference.png')
    parser.add_argument('--angle',type=int)
    parser.add_argument('--image',type=Path)
    parser.add_argument('--reviewed',action='store_true')
    parser.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args()
    job=OrbitJob(args.source)
    if args.action=='guides':
        print('\n'.join(map(str,render_guides(args.root,job))))
    elif args.action=='register':
        if args.image is None or args.angle is None:parser.error('register needs --angle and --image')
        print(register_frame(args.root,job,args.angle,args.image,
                             'anchor' if args.angle==0 else 'independent_generation',reviewed=args.reviewed))
    else:
        print(status(args.root,job))
if __name__=='__main__':main()
