"""Reusable domain operations: make, resume, and validate one checkpoint.

No angle-specific code. The orchestration layer decides which angle to request.
"""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import shutil
import numpy as np
from .core import inspect_image, read_json, save_json, validate_deliverable, sha256
from .domain import photo_prompt
from .render import Renderer
from .visibility import VISIBILITY_VERSION, encode_visibility, increment_visibility


def checkpoint_paths(root: Path, angle: int) -> tuple[Path,Path,Path]:
    folder=root/f'{angle:03d}'
    return folder, folder/'geometry_native_1080x1920.png', folder/'checkpoint.json'


def existing_geometry_is_valid(meta: Path, expected_geometry_hash: str) -> bool:
    if not meta.exists():
        return False
    data=read_json(meta)
    reference=data.get('reference',{})
    # The checkpoint is portable: NEVER trust an absolute path from an older workspace.
    p=meta.parent/'geometry_native_1080x1920.png'
    return (
        data.get('mesh_geometry_sha256')==expected_geometry_hash
        and p.is_file()
        and reference.get('sha256')==sha256(p)
        and not validate_deliverable(inspect_image(p,source_kind='native_3d_render'))
    )


def create_or_reuse_checkpoint(renderer: Renderer, *, root: Path, angle: int,
                               geometry_hash: str, newly_front_facing: int) -> tuple[dict,bool]:
    folder, image, metadata=checkpoint_paths(root,angle)
    if existing_geometry_is_valid(metadata,geometry_hash):
        record=read_json(metadata)
        # Migrate historical absolute reference paths without touching valid image bytes.
        if record['reference']['path'] != image.name:
            record['reference']['path'] = image.name
            save_json(metadata,record)
        return record, True

    renderer.render(angle,image)
    evidence=inspect_image(image,source_kind='native_3d_render')
    errors=validate_deliverable(evidence)
    if errors:
        raise RuntimeError(f'Checkpoint {angle}: {errors}')
    record={
        'angle':angle,
        'camera_only':True,
        'mesh_geometry_sha256':geometry_hash,
        'reference':{**asdict(evidence),'path':image.name},
        'newly_front_facing_vertex_count':newly_front_facing,
        'occlusion_visibility_verified':False,
        'photo_prompt':photo_prompt(angle),
        'photo_status':'NOT_GENERATED',
        'photo_requirement':'Native independent full-frame image from one generation job; verified origin and native pixel dimensions',
    }
    save_json(metadata,record)
    return record,False


def accept_native_photo(*, root: Path,angle: int,source: Path,
                        generation_id: str,generated_images_in_job: int,
                        origin: str) -> Path:
    """Accept a provider-origin single photo, never a crop/upscale.

    Provenance must come from the generation tool; this function cannot
    independently infer provenance from pixels.
    """
    folder, reference, meta=checkpoint_paths(root,angle)
    if not meta.is_file() or not reference.is_file():
        raise ValueError('Geometry checkpoint must exist before the corresponding photograph')
    if not generation_id.strip() or generated_images_in_job!=1 or origin!='direct_native_single_image':
        raise ValueError('Missing or invalid tool provenance: require one directly generated image')
    evidence=inspect_image(source,source_kind='independent_native_photo')
    errors=validate_deliverable(evidence)
    if errors:
        raise ValueError(f'Photographic output rejected: {errors}')
    target=folder/'photo_native.png'
    shutil.copyfile(source,target)  # byte-for-byte only, no scaling or spatial operations
    data=read_json(meta)
    data['photo_status']='ACCEPTED'
    data['photo']={**asdict(inspect_image(target,source_kind='independent_native_photo')), 'path':target.name,
                   'generation_id':generation_id,'generated_images_in_job':1,
                   'source_origin':origin,'source_sha256':evidence.sha256}
    save_json(meta,data)
    return target


def save_or_reuse_visibility(*, root: Path, angle: int, geometry_hash: str,
                             visible: np.ndarray, previous_seen: np.ndarray) -> tuple[np.ndarray, dict, bool]:
    """Durably save real occlusion checks without re-rendering valid photo/geometry.

    The previous cumulative mask is an input; it must agree when resuming to
    ensure the state reflects the same ordered 15-degree sequence.
    """
    folder, _, meta_path = checkpoint_paths(root,angle)
    path = folder/'visibility.npz'
    newly, total = increment_visibility(visible, previous_seen)
    record = read_json(meta_path)
    expected = {
        'algorithm_version':VISIBILITY_VERSION,
        'mesh_geometry_sha256':geometry_hash,
        'visible_vertices':int(np.count_nonzero(visible)),
        'newly_visible_vertices':int(np.count_nonzero(newly)),
        'cumulative_visible_vertices':int(np.count_nonzero(total)),
        'vertex_count':len(visible),
        'raster_occlusion_checked':True,
        'method':'VTK z-buffer, front-facing normals, orthographic projected vertex depth',
    }
    if (path.exists() and record.get('visibility')==expected):
        try:
            with np.load(path, allow_pickle=False) as saved:
                if (np.array_equal(saved['visible'],encode_visibility(visible))
                        and np.array_equal(saved['seen'],encode_visibility(total))):
                    return total, expected, True
        except (ValueError,KeyError,OSError):
            pass
    folder.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(path,visible=encode_visibility(visible),
                        newly=encode_visibility(newly),seen=encode_visibility(total))
    record['visibility']=expected
    record.pop('newly_front_facing_vertex_count',None)
    record['occlusion_visibility_verified']=True
    save_json(meta_path, record)
    return total, expected, False
