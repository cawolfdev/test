"""Orchestrate repeatable 15-degree geometric checkpoints and occlusion records."""
from __future__ import annotations
from pathlib import Path
from dataclasses import asdict
from .domain import OrbitSpec
from .core import save_json, read_json, sha256
from .render import load_fixed_mesh, Renderer, sha256_of_mesh
from .checkpoints import create_or_reuse_checkpoint, save_or_reuse_visibility
from .visibility import depth_visible
import numpy as np


def run_orbit(repository: Path, *, spec: OrbitSpec, stop_after: int | None = None) -> Path:
    asset = repository/'assets/geometry/fixed_pose_proxy.glb'
    mesh = load_fixed_mesh(asset)
    renderer = Renderer(mesh, spec)
    target = repository/'outputs/orbit_000_120'
    target.mkdir(parents=True, exist_ok=True)
    geometry_hash = sha256_of_mesh(mesh)
    origin_hash = sha256(asset)
    record_path = target/'state.json'
    state = {
        'spec':asdict(spec),
        'asset':str(asset.relative_to(repository)),
        'mesh_asset_sha256':origin_hash,
        'geometry_sha256':geometry_hash,
        'note':'Fixed approximate 3D proxy. Native 1080x1920 renders; visibility tested against actual raster depth; photos not generated.',
        'checkpoints':[],
    }
    if record_path.exists():
        older = read_json(record_path)
        if older.get('geometry_sha256') != geometry_hash or older.get('spec') != asdict(spec):
            raise RuntimeError('Saved state belongs to a different model or camera spec')
    seen = np.zeros(len(mesh.vertices), dtype=bool)
    for angle in spec.angles:
        checkpoint,reused = create_or_reuse_checkpoint(
            renderer,root=target,angle=angle,geometry_hash=geometry_hash,
            newly_front_facing=0)
        z,near,far=renderer.depth_buffer(angle)
        samples=depth_visible(mesh.vertices,mesh.vertex_normals,z,angle,spec,near,far)
        seen,vis_record,vis_reused=save_or_reuse_visibility(
            root=target,angle=angle,geometry_hash=geometry_hash,
            visible=samples.visible,previous_seen=seen)
        state['checkpoints'].append({
            'angle':angle,
            'checkpoint':str((target/f'{angle:03d}'/'checkpoint.json').relative_to(repository)),
            'photo_status':checkpoint['photo_status'],
            'render_reused':reused,
            'visibility_reused':vis_reused,
            'newly_visible_vertices':vis_record['newly_visible_vertices'],
            'visible_vertices':vis_record['visible_vertices'],
            'cumulative_visible_vertices':vis_record['cumulative_visible_vertices'],
        })
        save_json(record_path,state)
        print(f'[checkpoint {angle:03d}°] geometry {"reused" if reused else "rendered"}; '
              f'z-buffer visibility {"reused" if vis_reused else "recorded"}: '
              f'{vis_record["newly_visible_vertices"]} newly visible vertices; '
              f'photo: {checkpoint["photo_status"]}', flush=True)
        if stop_after is not None and angle >= stop_after:
            break
    return record_path
