"""Measured mesh topology and explicit limitations: no cosmetic auto-repair."""
from __future__ import annotations
from pathlib import Path
import numpy as np
from .render import load_fixed_mesh


def measure_mesh_quality(path:Path) -> dict:
    mesh=load_fixed_mesh(path)
    edge_incidence=np.bincount(mesh.edges_unique_inverse,minlength=len(mesh.edges_unique))
    boundary=int(np.count_nonzero(edge_incidence==1))
    nonmanifold=int(np.count_nonzero(edge_incidence>2))
    body_extent=(mesh.bounds[1]-mesh.bounds[0]).tolist()
    return {
        'vertices':int(len(mesh.vertices)),
        'triangles':int(len(mesh.faces)),
        'watertight':bool(mesh.is_watertight),
        'boundary_edges':boundary,
        'nonmanifold_edges':nonmanifold,
        'model_extent_units':[round(float(v),5) for v in body_extent],
        'anatomical_coverage_review':'upper thighs only; calves, ankles and feet are not modeled',
        'photo_ready':False,
        'limitations':[
            'Non-watertight geometry has open mesh boundaries' if boundary else 'No open boundary was measured',
            'Face/hair shapes are not fitted against facial identity references',
            'Incomplete legs prevent a full-body anatomically valid camera orbit',
            'Original head/arm arrangement differs from photographic reference pose',
        ]
    }
