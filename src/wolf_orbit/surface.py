"""Reusable geometry-backed rasterizer: one stationary subject; camera-only orbit.

Reuses the audited anatomical primitive specification of proxy.py. The primitives
are a *coarse proxy*, not a human scan or calibrated anatomical mesh.
"""
from dataclasses import dataclass
from math import pi
import numpy as np
from .proxy import scene_parts
from .geometry import Orbit

@dataclass(frozen=True)
class View:
    width: int = 640
    height: int = 576
    center_x: float = 0.0
    high_z: float = 2.90
    low_z: float = .80
    radius: float = 5.0

@dataclass(frozen=True)
class SurfaceFrame:
    part_id: np.ndarray
    surface_xyz: np.ndarray
    surface_uv: np.ndarray
    normal_xyz: np.ndarray
    hit_distance: np.ndarray


def camera_axes(degrees):
    """Reuse the domain-independent camera convention from geometry.Orbit."""
    orbit = Orbit(degrees)
    x, y, _height = orbit.position
    toward = np.asarray((x / orbit.radius, y / orbit.radius, 0.), dtype=np.float32)
    right = np.asarray((toward[1], -toward[0], 0.), dtype=np.float32)
    return toward, right


def cast_visible_surface(degrees, view=View(), parts=None):
    """Trace near intersections against unchanged 3-D parts, return world positions.

    Output positions and UVs are actual geometry intersections, not hallucinated 2D
    rotations. All camera views share the same part centers and dimensions.
    """
    if parts is None: parts=scene_parts()
    w,h=view.width,view.height
    toward,right=camera_axes(degrees)
    # Orthographic screen extent with world-unit aspect ratio enforced.
    zspan=view.high_z-view.low_z
    xspan=zspan*w/h
    x=np.linspace(-xspan/2+view.center_x,xspan/2+view.center_x,w,dtype=np.float32)[None,:]
    z=np.linspace(view.high_z,view.low_z,h,dtype=np.float32)[:,None]
    origin=np.empty((h,w,3),dtype=np.float32)
    origin[:,:,0]=view.radius*toward[0]+right[0]*x
    origin[:,:,1]=view.radius*toward[1]+right[1]*x
    origin[:,:,2]=z
    direction=-toward
    closest=np.full((h,w),np.inf,np.float32)
    ids=np.full((h,w),-1,np.int16)
    normals=np.zeros((h,w,3),np.float32)
    hitpoints=np.zeros((h,w,3),np.float32)
    for idx,(center,axes,_kind) in enumerate(parts):
        c=np.asarray(center,dtype=np.float32)
        inv=np.asarray(axes,dtype=np.float32)**-2
        relative=origin-c
        a=(direction*direction*inv).sum()
        b=2*(relative*direction*inv).sum(axis=-1)
        cterm=(relative*relative*inv).sum(axis=-1)-1
        discriminant=b*b-4*a*cterm
        t=(-b-np.sqrt(np.maximum(discriminant,0)))/(2*a)
        closer=(discriminant>=0)&(t>0)&(t<closest)
        if not closer.any(): continue
        p=origin[closer]+t[closer,None]*direction
        n=(p-np.asarray(center))*inv
        n/=np.maximum(np.linalg.norm(n,axis=-1,keepdims=True),1e-8)
        hitpoints[closer]=p
        normals[closer]=n
        closest[closer]=t[closer]
        ids[closer]=idx
    uv=np.zeros((h,w,2),dtype=np.float32)
    for i,(center,axes,_kind) in enumerate(parts):
        mask=ids==i
        if not mask.any(): continue
        unit=(hitpoints[mask]-np.asarray(center,dtype=np.float32))/np.asarray(axes,dtype=np.float32)
        uv[mask,0]=(np.arctan2(unit[:,0],unit[:,1])/(2*pi)+.5)%1.
        uv[mask,1]=np.arccos(np.clip(unit[:,2],-1,1))/pi
    return SurfaceFrame(ids,hitpoints,uv,normals,closest)


def build_mesh(parts=None, subdivisions=3):
    """Exportable 3-D model assembled from the immutable existing anatomy proxy."""
    import trimesh
    if parts is None: parts=scene_parts()
    scene=trimesh.Scene()
    for i,(center,axes,kind) in enumerate(parts):
        sphere=trimesh.creation.icosphere(subdivisions=subdivisions)
        sphere.apply_scale(axes)
        sphere.apply_translation(center)
        scene.add_geometry(sphere, node_name=f'{i:02d}_{kind}', geom_name=f'{i:02d}_{kind}')
    return scene
