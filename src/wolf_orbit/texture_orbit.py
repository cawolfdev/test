"""Sequential first-observation UV painting on fixed 3D geometry.

Every step loads the *previous saved* material state. It paints only visible
surface texels that have never been observed in an earlier step, using existing
photographic candidate frames as evidence. Saves both rendered image and state.
"""
import json
import hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageColor
from scipy.ndimage import distance_transform_edt
from .assets import sha256
from .geometry import ANGLES
from .surface import View, cast_visible_surface, human_faced_proxy, build_mesh
from .proxy import MATERIAL

TEXTURE_W=512
TEXTURE_H=256

def initial_state(parts=None):
    if parts is None: parts=human_faced_proxy()
    return (np.zeros((len(parts),TEXTURE_H,TEXTURE_W,3),np.uint8),
            np.zeros((len(parts),TEXTURE_H,TEXTURE_W),np.bool_))


def uv_texel(frame):
    """Quantize actual model surface coordinates to persistent per-part UV texels."""
    u=np.minimum((frame.surface_uv[:,:,0]*TEXTURE_W).astype(np.int32),TEXTURE_W-1)
    v=np.minimum((frame.surface_uv[:,:,1]*TEXTURE_H).astype(np.int32),TEXTURE_H-1)
    valid=frame.part_id>=0
    return (frame.part_id[valid].astype(np.int32),v[valid],u[valid],valid)


def image_samples(path,width,height):
    with Image.open(path) as im:
        im=im.convert('RGB').resize((width,height),Image.Resampling.LANCZOS)
        return np.asarray(im).copy()


def paint_novel_surface(frame, photo, color, observed):
    """Paint only unseen surface texels, do not repaint earlier observations."""
    part,v,u,visible=uv_texel(frame)
    source=photo[visible]
    packed=(part*TEXTURE_H+v)*TEXTURE_W+u
    _unique, first=np.unique(packed,return_index=True)
    p0,v0,u0=part[first],v[first],u[first]
    unseen=~observed[p0,v0,u0]
    p1,v1,u1=p0[unseen],v0[unseen],u0[unseen]
    color[p1,v1,u1]=source[first[unseen]]
    observed[p1,v1,u1]=True
    return {'new_texels':int(unseen.sum()),'visible_pixels':int(visible.sum()),
            'total_texels':int(observed.sum())}


def render_surface(frame,color,observed,background=None):
    """Render the accumulated UV appearance at the *new* camera angle.

    Incomplete pixel samples use the closest already observed texel on the same
    anatomical part for preview only; the saved material state is not invented.
    """
    h,w=frame.part_id.shape
    if background is None:
        picture=np.full((h,w,3),(205,211,216),np.uint8)
    else:
        picture=background.copy()
    p,v,u,visible=uv_texel(frame)
    result=color[p,v,u].copy()
    missing=~observed[p,v,u]
    if missing.any():
        # Fill display holes from same part texture, but never mutate its state.
        for component in np.unique(p[missing]):
            tex_mask=observed[component]
            if tex_mask.any():
                nearest=distance_transform_edt(~tex_mask,return_distances=False,return_indices=True)
                idx=np.where((p==component)&missing)[0]
                result[idx]=color[component,nearest[0,v[idx],u[idx]],nearest[1,v[idx],u[idx]]]
    picture[visible]=result
    return picture



def render_geometry(frame,parts=None):
    """Anatomy-color 3D reference with fixed world-space lighting.

    Unlike photograph projections, this independently checks camera visibility
    and occlusion, without facial duplication or image-background artifacts.
    """
    if parts is None: parts=human_faced_proxy()
    h,w=frame.part_id.shape
    out=np.full((h,w,3),(220,225,229),np.uint8)
    light=np.array((.45,.65,.62),dtype=np.float32)
    light/=np.linalg.norm(light)
    illumination=np.clip(np.sum(frame.normal_xyz*light,axis=-1),0,1)
    factor=.62+.35*illumination
    for i,(_c,_a,kind) in enumerate(parts):
        mask=frame.part_id==i
        if mask.any():
            rgb=np.asarray(ImageColor.getrgb(MATERIAL[kind]),np.float32)
            out[mask]=np.clip(rgb*factor[mask,None],0,255).astype(np.uint8)
    return out


def paint_novel_pixels_image(frame, old_observed):
    """Diagnostic: mark the surfaces not present in previous checkpoint state."""
    out=render_geometry(frame)
    p,v,u,visible=uv_texel(frame)
    novel=~old_observed[p,v,u]
    mask=np.zeros(frame.part_id.shape,dtype=np.bool_)
    mask[visible]=novel
    out[mask]=(235,137,61)
    return out


def checkpoint_paths(root,angle):
    folder=Path(root)/'sequential'
    return (folder/'checkpoints'/f'{angle:03d}.npz',folder/'renders'/f'{angle:03d}.png',folder/'checkpoints'/f'{angle:03d}.json')


def provenance(root,angle,model_sha,prior_sha):
    return {'degree':angle,'photo_sha256':sha256(Path(root)/'images'/f'{angle:03d}_clockwise.png'),
            'model_sha256':model_sha,'previous_checkpoint_sha256':prior_sha,
            'photographic_evidence':'existing source photo at this nominal angle, uncalibrated',
            'geometric_evidence':'fixed 3D proxy ray intersections',
            'completion_method':'UV paint previously unseen surface texels only'}


def execute(root,view=View(),force=False):
    """Run strictly ordered 0, 15 ... 120, never skip predecessor state."""
    root=Path(root)
    parts=human_faced_proxy()
    geometry_model=root/'model'/'fixed_human_faced_bodybuilder_proxy.glb'
    geometry_model.parent.mkdir(parents=True,exist_ok=True)
    if force or not geometry_model.exists():
        build_mesh(parts).export(geometry_model)
    model_hash=sha256(geometry_model)
    color,observed=initial_state(parts)
    previous_hash=None
    records=[]
    geom_dir=root/'sequential'/'geometry'
    novelty_dir=root/'sequential'/'newly_exposed'
    geom_dir.mkdir(parents=True,exist_ok=True)
    novelty_dir.mkdir(parents=True,exist_ok=True)
    for angle in ANGLES:
        state_path,render_path,meta_path=checkpoint_paths(root,angle)
        state_path.parent.mkdir(parents=True,exist_ok=True)
        render_path.parent.mkdir(parents=True,exist_ok=True)
        photo_path=root/'images'/f'{angle:03d}_clockwise.png'
        expected=provenance(root,angle,model_hash,previous_hash)
        if state_path.exists() and render_path.exists() and meta_path.exists() and (geom_dir/f'{angle:03d}.png').exists() and (novelty_dir/f'{angle:03d}.png').exists() and not force:
            metadata=json.loads(meta_path.read_text())
            if all(metadata.get(k)==v for k,v in expected.items()):
                with np.load(state_path) as arrays:
                    color=arrays['colors'].copy()
                    observed=arrays['observed'].copy()
                previous_hash=sha256(state_path)
                records.append({**metadata,'cache':'reused'})
                continue
        frame=cast_visible_surface(angle,view,parts)
        photo=image_samples(photo_path,view.width,view.height)
        geo_path=geom_dir/f'{angle:03d}.png'
        novel_path=novelty_dir/f'{angle:03d}.png'
        Image.fromarray(render_geometry(frame,parts)).save(geo_path)
        Image.fromarray(paint_novel_pixels_image(frame,observed)).save(novel_path)
        record=paint_novel_surface(frame,photo,color,observed)
        out=render_surface(frame,color,observed,photo)
        Image.fromarray(out).save(render_path)
        np.savez_compressed(state_path,colors=color,observed=observed)
        metadata={**expected,**record,'state_sha256':sha256(state_path),
                  'render_sha256':sha256(render_path),'geometry_sha256':sha256(geo_path),
                  'novelty_sha256':sha256(novel_path),'size':[view.width,view.height]}
        meta_path.write_text(json.dumps(metadata,indent=2)+'\n')
        previous_hash=sha256(state_path)
        records.append({**metadata,'cache':'computed'})
    output=root/'sequential'/'sequence_manifest.json'
    output.write_text(json.dumps(records,indent=2)+'\n')
    return records


def make_comparison(root, mode="geometry"):
    """Reusable contact sheet for geometry, texture projection or newly exposed areas."""
    if mode not in ("geometry","renders","newly_exposed"):
        raise ValueError(mode)
    from PIL import Image, ImageDraw
    root=Path(root)
    shots=[]
    for angle in ANGLES:
        with Image.open(root/'sequential'/mode/f'{angle:03d}.png') as img:
            thumb=img.convert('RGB').copy()
        thumb.thumbnail((350,315))
        shots.append((angle,thumb))
    columns=3
    cell_w=365
    cell_h=346
    sheet=Image.new('RGB',(columns*cell_w,3*cell_h),(235,238,241))
    draw=ImageDraw.Draw(sheet)
    for i,(a,img) in enumerate(shots):
        x=(i%3)*cell_w+(cell_w-img.width)//2
        y=(i//3)*cell_h+26
        sheet.paste(img,(x,y))
        draw.text(((i%3)*cell_w+13,(i//3)*cell_h+7),f'{a:03d} deg | fixed 3D, incremental surface',fill=(24,33,45))
    dest=root/'sequential'/'previews'/f'{mode}_15deg_sequence.jpg'
    dest.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(dest,quality=94)
    return dest
