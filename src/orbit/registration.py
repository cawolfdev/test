"""Pure silhouette alignment and metrics; does not deform the subject's anatomy."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import cv2
import numpy as np
from scipy.optimize import minimize
from PIL import Image,ImageDraw
from .segmentation import SegmentationSpec,segment_reference_subject,letterbox_rgb,geometry_silhouette
from .core import save_json

@dataclass(frozen=True)
class Alignment:
    scale:float
    shift_x:float
    shift_y:float
    iou:float
    geometry_coverage:float
    reference_coverage:float


def warp_mask(mask:np.ndarray, *, scale:float,shift_x:float,shift_y:float)->np.ndarray:
    h,w=mask.shape
    m=np.array([[scale,0,shift_x+(1-scale)*w/2],[0,scale,shift_y+(1-scale)*h/2]],dtype=np.float32)
    return cv2.warpAffine(mask.astype('uint8'),m,(w,h),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT)>0


def mask_metrics(model:np.ndarray, reference:np.ndarray)->tuple[float,float,float]:
    if model.shape!=reference.shape or model.dtype!=bool or reference.dtype!=bool:
        raise ValueError('Expected matching boolean masks')
    shared=np.count_nonzero(model&reference)
    total=np.count_nonzero(model|reference)
    return (float(shared/total) if total else 1.0,
            float(shared/max(1,np.count_nonzero(model))),
            float(shared/max(1,np.count_nonzero(reference))))


def fit_camera_only(model:np.ndarray,reference:np.ndarray)->Alignment:
    """Register projection scale+translation only. Restrained so pose mismatch stays visible.

    This is NOT a mesh fit or evidence of 3D correspondence.
    """
    h,w=model.shape
    if model.shape!=reference.shape: raise ValueError('Need same-size model and reference masks')
    def objective(v):
        warped=warp_mask(model,scale=float(v[0]),shift_x=float(v[1]),shift_y=float(v[2]))
        iou,_,_=mask_metrics(warped,reference)
        return 1-iou
    best=None
    # Optimize within bounded view calibration: max +/-25% scale, +/-12.5% shift.
    bounds=[(.75,1.25),(-.125*w,.125*w),(-.125*h,.125*h)]
    for scale in (.85,1.,1.15):
        result=minimize(objective,[scale,0.,0.],method='Powell',bounds=bounds,
                        options={'xtol':.005,'ftol':.001,'maxiter':55})
        if best is None or result.fun<best.fun: best=result
    scale,dx,dy=[float(x) for x in best.x]
    iou,mc,rc=mask_metrics(warp_mask(model,scale=scale,shift_x=dx,shift_y=dy),reference)
    return Alignment(scale,dx,dy,iou,mc,rc)


def draw_comparison(rgb:np.ndarray,reference:np.ndarray,model:np.ndarray,
                    alignment:Alignment,angle:int, *, output_width=1080,output_height=1920)->Image.Image:
    """Full-HD diagnostic (not a generated photograph); red=reference and cyan=model."""
    aligned=warp_mask(model,scale=alignment.scale,shift_x=alignment.shift_x,shift_y=alignment.shift_y)
    rgb=rgb.copy()
    # Darken outside reference lightly; preserve anatomical features.
    rgb[~reference]=(rgb[~reference].astype('float32')*.65).astype('uint8')
    contour_ref,_=cv2.findContours(reference.astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contour_model,_=cv2.findContours(aligned.astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    bgr=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
    cv2.drawContours(bgr,contour_ref,-1,(55,65,255),2,cv2.LINE_AA)
    cv2.drawContours(bgr,contour_model,-1,(255,220,40),2,cv2.LINE_AA)
    out=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).resize((output_width,output_height),Image.Resampling.LANCZOS)
    d=ImageDraw.Draw(out)
    d.rectangle((0,0,output_width,86),fill=(19,26,33))
    d.text((24,15),f'{angle:03d} deg / estimated source silhouette (red) vs camera-calibrated proxy (cyan)',fill='white')
    d.text((24,42),f'IoU {alignment.iou:.3f}  |  scale {alignment.scale:.3f}  |  pose and anatomy NOT fitted',fill='white')
    return out


def compare_reference(reference_path:Path,geometry_path:Path,*,angle:int,outdir:Path)->dict:
    """Persist visual and numerical evidence for one source view, including bad alignment."""
    from .core import sha256
    outdir.mkdir(parents=True,exist_ok=True)
    rgb=np.array(Image.open(reference_path).convert('RGB'))
    rendered=np.array(Image.open(geometry_path).convert('RGB'))
    working,ref_mask,seg=segment_reference_subject(rgb)
    model=letterbox_rgb(rendered,working.shape[1],working.shape[0])
    model_mask=geometry_silhouette(model)
    alignment=fit_camera_only(model_mask,ref_mask)
    Image.fromarray((ref_mask*255).astype('uint8')).save(outdir/f'reference_mask_{angle:03d}.png')
    preview=outdir/f'registration_{angle:03d}_1080x1920.png'
    draw_comparison(working,ref_mask,model_mask,alignment,angle).save(preview)
    record={'angle':angle,'alignment':asdict(alignment),'source_sha256':sha256(reference_path),
            'geometry_sha256':sha256(geometry_path), 'segmentation':seg,
            'quality_gate':{'minimum_iou':.82,'passed':alignment.iou>=.82,
                            'interpretation':'Diagnostic only; passing a silhouette IoU alone cannot prove anatomical identity or pose'},
            'image':preview.name}
    save_json(outdir/f'registration_{angle:03d}.json',record)
    return record
