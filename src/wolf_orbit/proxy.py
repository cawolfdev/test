"""Constrained geometry proxy: proves camera coordinate conventions, not photo anatomy.

All anatomical parts live in one immutable world-space scene. Every view changes
only the camera azimuth. No per-view object or facial pose is modified.
"""
from pathlib import Path
import numpy as np
from .geometry import ANGLES

# center_xyz, semi_axes_xyz, grayscale material family. The muzzle points +Y.
PARTS=(
 ((0,0,1.14),(.72,.45,.82),'torso'),
 ((-.38,-.32,1.46),(.42,.25,.54),'back'),
 ((+.38,-.32,1.46),(.42,.25,.54),'back'),
 ((-.37,+.34,1.52),(.43,.27,.39),'chest'),
 ((+.37,+.34,1.52),(.43,.27,.39),'chest'),
 ((-.82,0,1.63),(.42,.42,.43),'shoulder'),
 ((+.82,0,1.63),(.42,.42,.43),'shoulder'),
 ((-1.01,0,.97),(.29,.31,.50),'arm'),
 ((+1.01,0,.97),(.29,.31,.50),'arm'),
 ((-.40,-.10,1.92),(.30,.33,.25),'back'),
 ((+.40,-.10,1.92),(.30,.33,.25),'back'),
 ((0,0,1.95),(.29,.32,.48),'neck'),
 ((0,+.03,2.43),(.32,.31,.34),'head'),
 ((0,+.37,2.39),(.135,.26,.12),'muzzle'),
 ((-.22,+.015,2.75),(.105,.115,.19),'head'),
 ((+.22,+.015,2.75),(.105,.115,.19),'head'),
)
MATERIAL={'torso':'#85959f','back':'#687987','chest':'#a7b5bd','shoulder':'#879ba8','arm':'#798e9d','neck':'#a5a5a1','head':'#b7a491','muzzle':'#765f50'}

def scene_parts():
    """Return one immutable specification for all angles."""
    return PARTS

def raycast_proxy(angle, resolution=(480,540)):
    """Orthographic rays against fixed ellipsoids, with actual nearest-surface occlusion.

    This is deliberately a geometry test, *not* a substitute photo or 3D scan.
    Returns RGB pixels and visible part indices for regression tests.
    """
    from math import radians, sin, cos
    w,h=resolution
    theta=radians(angle)
    cam=np.array([sin(theta),cos(theta),0.0],dtype=np.float64)
    right=np.array([cos(theta),-sin(theta),0.0],dtype=np.float64)
    # Every camera remains level and at a constant subject-relative height.
    xx=np.linspace(-1.45,1.45,w)[None,:]
    zz=np.linspace(2.98,0.10,h)[:,None]
    origins=np.stack(np.broadcast_arrays(
        5*cam[0]+right[0]*xx,
        5*cam[1]+right[1]*xx,
        zz),axis=-1)
    direction=-cam
    closest=np.full((h,w),np.inf)
    ids=np.full((h,w),-1,dtype=np.int16)
    normals=np.zeros((h,w,3),dtype=np.float32)
    for i,(center,semi_axes,kind) in enumerate(PARTS):
        c=np.asarray(center); inv=1/np.square(semi_axes)
        d=origins-c
        qa=(direction*direction*inv).sum()
        qb=2*(d*direction*inv).sum(axis=-1)
        qc=(d*d*inv).sum(axis=-1)-1
        disc=qb*qb-4*qa*qc
        safe=np.maximum(disc,0)
        t=(-qb-np.sqrt(safe))/(2*qa)
        selection=(disc>=0)&(t>0)&(t<closest)
        closest[selection]=t[selection]
        ids[selection]=i
        if np.any(selection):
            hit=origins[selection]+t[selection,None]*direction
            n=(hit-c)*inv
            n=n/np.maximum(np.linalg.norm(n,axis=-1,keepdims=True),1e-9)
            normals[selection]=n
    palette={
        'torso':(135,149,159),'back':(95,109,121),'chest':(176,188,195),
        'shoulder':(135,155,168),'arm':(121,142,157),'neck':(174,173,167),
        'head':(179,160,141),'muzzle':(115,91,77)
    }
    rgb=np.empty((h,w,3),dtype=np.uint8)
    rgb[:]=(243,244,245)
    light=np.array([.35,.55,.76]);light=light/np.linalg.norm(light)
    intensity=.66+.31*np.clip((normals*light).sum(axis=-1),0,1)
    for idx,(_,_,kind) in enumerate(PARTS):
        sel=(ids==idx)
        if np.any(sel):
            base=np.asarray(palette[kind])
            rgb[sel]=np.uint8(np.clip(base*intensity[sel,None],0,255))
    return rgb,ids


def render_proxy(root, angles=ANGLES, force=False):
    from PIL import Image, ImageDraw, ImageFont
    root=Path(root)
    target=root/'mocks'/'proxy_3d'
    target.mkdir(parents=True,exist_ok=True)
    outputs=[]
    for a in angles:
        path=target/f'{a:03d}_pose_proxy.png'
        if path.exists() and not force:
            outputs.append(path)
            continue
        rgb,_=raycast_proxy(a)
        output=Image.new('RGB',(480,584),'#f3f4f5')
        output.paste(Image.fromarray(rgb),(0,44))
        draw=ImageDraw.Draw(output)
        draw.text((15,16),f'{a:03d}° CAMERA  •  FIXED HEAD/BODY',fill=(24,31,39))
        output.save(path)
        outputs.append(path)
    return outputs
