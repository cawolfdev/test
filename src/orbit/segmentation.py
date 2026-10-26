"""Reference subject extraction for diagnostic alignment, not ground-truth segmentation.

Uses conservative color seeds followed by GrabCut. The returned boundary is
an estimate and must be reviewed before it could authorize geometry fitting.
"""
from __future__ import annotations
from dataclasses import dataclass
import cv2
import numpy as np

@dataclass(frozen=True)
class SegmentationSpec:
    width: int = 480
    height: int = 720
    iterations: int = 5


def letterbox_rgb(rgb: np.ndarray, width: int, height: int, *, background=(211, 217, 228)) -> np.ndarray:
    if rgb.ndim != 3 or rgb.shape[2] != 3 or width <= 0 or height <= 0:
        raise ValueError('Expected HxWx3 RGB with positive output dimensions')
    h, w = rgb.shape[:2]
    k = min(width / w, height / h)
    nw, nh = max(1,round(w*k)), max(1,round(h*k))
    image = cv2.resize(rgb,(nw,nh),interpolation=cv2.INTER_AREA if k<1 else cv2.INTER_LINEAR)
    canvas = np.empty((height,width,3),dtype=np.uint8)
    canvas[:]=background
    ox, oy=(width-nw)//2,(height-nh)//2
    canvas[oy:oy+nh,ox:ox+nw]=image
    return canvas


def segment_reference_subject(rgb: np.ndarray, spec: SegmentationSpec=SegmentationSpec()) -> tuple[np.ndarray,np.ndarray,dict]:
    """Return (letterboxed RGB, boolean foreground estimate, extraction metadata).

    Supports the *current* outdoor skin/blue-background reference domain.
    It does not claim the mask is human-reviewed ground truth.
    """
    image=letterbox_rgb(rgb,spec.width,spec.height)
    r,g,b=image.astype('int16').transpose(2,0,1)
    skin=(r-b>38)&(r-g>11)&(r>97)&(g>55)&(g>b)
    cool=(b-r>3)&(b-g>-35)
    yy,xx=np.mgrid[:spec.height,:spec.width]
    mid=(xx>.1875*spec.width)&(xx<.8333*spec.width)
    dark=(r<105)&(g<110)&(b<110)
    shorts=mid&(yy>.61*spec.height)&(yy<.89*spec.height)&dark
    hair=mid&(yy<.30*spec.height)&(yy>.007*spec.height)&dark
    mask=np.where(skin,cv2.GC_FGD,cv2.GC_PR_BGD).astype('uint8')
    mask[cool&(~skin)]=cv2.GC_BGD
    mask[shorts|hair]=cv2.GC_PR_FGD
    if not np.any(mask==cv2.GC_FGD) or not np.any(mask==cv2.GC_BGD):
        raise ValueError('Reference lacks enough foreground/background seeds for diagnostic extraction')
    bg=np.zeros((1,65),np.float64)
    fg=np.zeros((1,65),np.float64)
    cv2.grabCut(cv2.cvtColor(image,cv2.COLOR_RGB2BGR),mask,None,bg,fg,spec.iterations,cv2.GC_INIT_WITH_MASK)
    foreground=(mask%2==1).astype('uint8')
    n,cc,stats,_=cv2.connectedComponentsWithStats(foreground,8)
    if n<2: raise ValueError('Segmentation returned no connected foreground')
    largest=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
    foreground=cc==largest
    return image,foreground,{
        'method':'color_seeds_grabcut_largest_component',
        'reviewed':False,
        'mask_scope':'estimated subject silhouette in letterboxed reference',
        'foreground_pixels':int(np.count_nonzero(foreground)),
        'foreground_fraction':round(float(foreground.mean()),6),
        'working_size':[spec.width,spec.height]
    }


def geometry_silhouette(rgb: np.ndarray, *, background_tolerance: int=22) -> np.ndarray:
    """Extract non-background rendered pixels; independent of anatomical recognition."""
    rgb=rgb.astype('int16')
    background=rgb[0,0].copy()
    return (np.max(np.abs(rgb-background),axis=2) > background_tolerance)
