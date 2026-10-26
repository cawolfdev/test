"""Reusable, read-only consistency checks for a persisted, portable orbit."""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import numpy as np
from .core import inspect_image, read_json, sha256, validate_deliverable
from .domain import OrbitSpec
from .render import load_fixed_mesh, sha256_of_mesh
from .visibility import VISIBILITY_VERSION, decode_visibility, increment_visibility


def verify_orbit(repository: Path, *, spec: OrbitSpec) -> dict:
    """Fail closed if geometry, visibility history, dimensions or paths disagree."""
    root=repository/'outputs/orbit_000_120'
    state=read_json(root/'state.json')
    mesh_path=repository/'assets/geometry/fixed_pose_proxy.glb'
    mesh=load_fixed_mesh(mesh_path)
    model_hash=sha256_of_mesh(mesh)
    if state['geometry_sha256']!=model_hash or state['mesh_asset_sha256']!=sha256(mesh_path):
        raise ValueError('Model digest mismatch')
    if state['spec']!=asdict(spec):
        raise ValueError('Camera specification differs from saved orbit')
    if tuple(c['angle'] for c in state['checkpoints'])!=spec.angles:
        raise ValueError('Missing/out-of-order camera checkpoints')
    seen=np.zeros(len(mesh.vertices),dtype=bool)
    rows=[]
    for angle in spec.angles:
        folder=root/f'{angle:03d}'
        meta=read_json(folder/'checkpoint.json')
        if meta.get('angle')!=angle or meta.get('mesh_geometry_sha256')!=model_hash:
            raise ValueError(f'{angle}° geometry metadata mismatch')
        photo_status=meta.get('photo_status')
        photo=meta.get('photo',{})
        if photo_status=='ACCEPTED':
            path=folder/photo['path']
            evidence=inspect_image(path,source_kind='independent_native_photo')
            if validate_deliverable(evidence) or photo.get('sha256')!=evidence.sha256:
                raise ValueError(f'{angle}° photographic evidence invalid')
        elif photo_status!='NOT_GENERATED':
            raise ValueError(f'{angle}° unknown photographic status')
        reference=meta['reference']
        if reference['path']!='geometry_native_1080x1920.png':
            raise ValueError(f'{angle}° nonportable geometry reference')
        evidence=inspect_image(folder/reference['path'],source_kind='native_3d_render')
        if validate_deliverable(evidence) or reference['sha256']!=evidence.sha256:
            raise ValueError(f'{angle}° native geometry image failed validation')
        vis=meta.get('visibility',{})
        if vis.get('algorithm_version')!=VISIBILITY_VERSION or vis.get('mesh_geometry_sha256')!=model_hash:
            raise ValueError(f'{angle}° visibility version/hash mismatch')
        with np.load(folder/'visibility.npz',allow_pickle=False) as masks:
            visible=decode_visibility(masks['visible'],len(mesh.vertices))
            newly=decode_visibility(masks['newly'],len(mesh.vertices))
            cumulative=decode_visibility(masks['seen'],len(mesh.vertices))
        expected_newly,expected_total=increment_visibility(visible,seen)
        if not np.array_equal(newly,expected_newly) or not np.array_equal(cumulative,expected_total):
            raise ValueError(f'{angle}° previously exposed/occlusion masks disagree')
        for key,number in [('visible_vertices',int(visible.sum())),
                           ('newly_visible_vertices',int(newly.sum())),
                           ('cumulative_visible_vertices',int(cumulative.sum()))]:
            if vis.get(key)!=number:
                raise ValueError(f'{angle}° metadata {key} mismatch')
        seen=cumulative
        rows.append({'angle':angle,
                     'geometry_width':evidence.width,
                     'geometry_height':evidence.height,
                     'geometry_sha256':evidence.sha256,
                     'visible_vertices':int(visible.sum()),
                     'newly_visible_vertices':int(newly.sum()),
                     'cumulative_visible_vertices':int(cumulative.sum()),
                     'photo_status':photo_status})
    return {'project':'wildlife-bodybuilder',
            'geometry_checkpoints':len(rows),
            'independent_full_hd_photographs':sum(c['photo_status']=='ACCEPTED' for c in rows),
            'model':'historical_unfitted_proxy',
            'vertex_count':len(mesh.vertices),
            'mesh_sha256':model_hash,
            'native_image_dimensions':[spec.width,spec.height],
            'viewpoints':rows,
            'assessment':'Geometric camera and sampled visibility verified; anatomical fit and photorealistic image generation NOT verified.'}
