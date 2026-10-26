"""Quality checks for diagnostic silhouettes, alignment, and evidence provenance."""
import numpy as np
from pathlib import Path
from PIL import Image
from src.orbit.registration import fit_camera_only, mask_metrics, warp_mask
from src.orbit.segmentation import letterbox_rgb, geometry_silhouette
from src.orbit.mesh_quality import measure_mesh_quality
from src.orbit.evidence import inspect_evidence

REPO=Path(__file__).resolve().parents[1]

def test_letterbox_keeps_source_aspect_and_no_crop():
    img=np.full((100,200,3),123,dtype=np.uint8)
    out=letterbox_rgb(img,480,720)
    assert out.shape==(720,480,3)
    assert np.array_equal(out[360,240],[123,123,123])
    assert not np.array_equal(out[0,0],[123,123,123])

def test_geometry_background_extraction():
    a=np.full((20,30,3),200,dtype=np.uint8)
    a[3:10,11:25]=[60,70,80]
    mask=geometry_silhouette(a)
    assert mask.sum()==98
    assert not mask[0,0]

def test_fit_camera_recovers_translation_without_mesh_change():
    a=np.zeros((130,120),dtype=bool)
    a[20:80,25:55]=True
    b=warp_mask(a,scale=1,shift_x=11,shift_y=8)
    fit=fit_camera_only(a,b)
    assert fit.iou>.99,(fit.scale,fit.shift_x,fit.shift_y,fit.iou)
    assert np.isclose(fit.shift_x,11,atol=1)
    assert np.isclose(fit.shift_y,8,atol=1)

def test_fit_bounds_and_rejects_unrelated_mask():
    a=np.zeros((120,120),dtype=bool);a[10:25,15:30]=True
    b=np.zeros_like(a);b[85:110,85:110]=True
    fit=fit_camera_only(a,b)
    assert fit.iou<.82
    assert .75<=fit.scale<=1.25

def test_validation_keeps_explicit_unready_mesh_status():
    m=measure_mesh_quality(REPO/'assets/geometry/fixed_pose_proxy.glb')
    assert m['vertices']>1000
    assert not m['watertight']
    assert m['boundary_edges']>0
    assert not m['photo_ready']

def test_full_evidence_manifest_and_rejected_generation_bytes_exist():
    report=inspect_evidence(REPO)
    assert report['historical_attempts']==len(__import__('json').loads((REPO/'evidence/rejected.json').read_text())['attempts'])
    assert report['historical_attempts']>=14
    assert report['visibility_diagnostics']==9
    assert report['registration_diagnostics']==2


def test_report_embedded_and_quality_gates_truthful():
    from src.orbit.release import generate_report
    from src.orbit.core import read_json
    report=generate_report(REPO,'v0002')
    assert report['quality_gates']['nine_geometry_checkpoints_verified']
    assert report['quality_gates']['accepted_native_hd_photographic_checkpoints']==0
    assert not report['quality_gates']['silhouette_gate_000_passed']
    assert not report['quality_gates']['silhouette_gate_060_passed']
    # Reporting is pure: calculating diagnostics must not overwrite human-reviewed status.
    assert read_json(REPO/'reports/current.json')['github_sync']['status']=='PARTIAL'
    assert report['hd_definition']['native_width_gt']==1000
    assert report['photo_orbit_angles']==[0,30,60,90,120]
    assert report['last_generation']['status']=='REJECTED'
    assert not (REPO/'reports/report-v0002.json').exists()
