from dataclasses import replace
import numpy as np
import pytest
from src.orbit.core import ImageEvidence,validate_deliverable
from src.orbit.domain import OrbitSpec,camera_position,screen_right,shared_parallel_half_height,newly_front_facing_vertices,photo_prompt


def test_nine_exact_angles():
    assert OrbitSpec().angles==(0,15,30,45,60,75,90,105,120)
    with pytest.raises(ValueError):
        OrbitSpec(step=16)


def test_camera_orbits_fixed_target():
    p0=camera_position(0,distance=8,center_z=1.2)
    p90=camera_position(90,distance=8,center_z=1.2)
    p120=camera_position(120,distance=8,center_z=1.2)
    assert np.allclose(p0,(0,-8,1.2))
    assert np.allclose(p90,(8,0,1.2))
    assert np.allclose(p120,(8*np.sin(np.deg2rad(120)),4,1.2))


def test_full_orbit_framing_not_cropped():
    verts=np.array([[-2,0,-1],[2,0,-1],[-2,0,3],[2,0,3]])
    s=OrbitSpec()
    half=shared_parallel_half_height(verts,s)
    for angle in s.angles:
        x=verts@screen_right(angle)
        assert np.max(np.abs(x)) < half*s.width/s.height
        assert np.max(np.abs(verts[:,2]-s.subject_center_z)) < half


def test_rejects_crops_and_upscales_even_when_large():
    a=ImageEvidence('montage_crop.png','cropped_panel',2048,3072,'hash')
    b=ImageEvidence('upscaled.png','upscaled',2048,3072,'hash')
    assert validate_deliverable(a)
    assert validate_deliverable(b)
    assert validate_deliverable(ImageEvidence('native.png','independent_native_photo',1024,1536,'hash'))
    assert validate_deliverable(ImageEvidence('native.png','independent_native_photo',1080,1920,'hash'))==()


def test_normal_gate_is_an_explicit_approximation():
    normals=np.array([[0,-1,0],[0,1,0]],dtype=float)
    seen=np.array([False,False])
    assert newly_front_facing_vertices(normals,seen,0).tolist()==[True,False]


def test_prompt_is_independent_single_view():
    assert 'ONE INDEPENDENT FULL FRAME' in photo_prompt(15)
    assert '+120 degrees' in photo_prompt(120)


def test_photo_gate_requires_single_native_provider_image(tmp_path):
    from src.orbit.checkpoints import accept_native_photo
    folder=tmp_path/'015'
    folder.mkdir()
    (folder/'checkpoint.json').write_text('{}')
    (folder/'geometry_native_1080x1920.png').touch()
    with pytest.raises(ValueError,match='provenance'):
        accept_native_photo(root=tmp_path,angle=15,source=tmp_path/'missing.png',
                            generation_id='x',generated_images_in_job=9,origin='cropped_collage')


def test_resume_reuses_checkpoint_without_regenerating(tmp_path):
    from PIL import Image
    from src.orbit.checkpoints import existing_geometry_is_valid
    from src.orbit.core import save_json,inspect_image
    from dataclasses import asdict
    path=tmp_path/'geometry_native_1080x1920.png'
    Image.new('RGB',(1080,1920)).save(path)
    save_json(tmp_path/'cp.json',{'mesh_geometry_sha256':'known',
                                'reference':asdict(inspect_image(path,source_kind='native_3d_render'))})
    assert existing_geometry_is_valid(tmp_path/'cp.json','known')
    assert not existing_geometry_is_valid(tmp_path/'cp.json','another model')


def test_real_occlusion_rejects_hidden_near_facing_surface():
    from src.orbit.visibility import depth_visible
    spec=OrbitSpec()
    # Two points project to the exact same pixel. The farther point's surface
    # normal is toward the camera, yet it is occluded by the front point.
    points=np.array([[0.,-.3,1.2],[0.,+.3,1.2]])
    normals=np.array([[0.,-1.,0.],[0.,-1.,0.]])
    from src.orbit.visibility import project_orthographic
    _,_,z=project_orthographic(points,0,spec,6.5,9.5,half_height=1.0)
    raster=np.ones((spec.height,spec.width),dtype=np.float32)
    raster[spec.height//2,spec.width//2]=z[0]
    result=depth_visible(points,normals,raster,0,spec,6.5,9.5)
    assert result.front_facing.tolist()==[True,True]
    assert result.visible.tolist()==[True,False]


def test_visibility_packing_and_increment():
    from src.orbit.visibility import increment_visibility,encode_visibility,decode_visibility
    past=np.array([True,False,False,True,False],dtype=bool)
    current=np.array([True,True,False,False,True],dtype=bool)
    new, seen=increment_visibility(current,past)
    assert new.tolist()==[False,True,False,False,True]
    assert seen.tolist()==[True,True,False,True,True]
    assert np.array_equal(decode_visibility(encode_visibility(seen),len(seen)),seen)


def test_projection_matches_vtk_native_camera(tmp_path):
    from src.orbit.render import load_fixed_mesh, Renderer
    from src.orbit.visibility import project_orthographic
    from pathlib import Path
    mesh=load_fixed_mesh(Path(__file__).resolve().parents[1]/'assets/geometry/fixed_pose_proxy.glb')
    spec=OrbitSpec()
    renderer=Renderer(mesh,spec)
    renderer._render_at(60)
    near,far=renderer._camera.GetClippingRange()
    pts=np.array([[0.,0.,1.2],[.4,-.2,1.8],[-.3,.15,.6]])
    x,y,z=project_orthographic(pts,60,spec,near,far,
        half_height=shared_parallel_half_height(mesh.vertices,spec))
    for i,point in enumerate(pts):
        renderer._renderer.SetWorldPoint(*point,1)
        renderer._renderer.WorldToDisplay()
        vtk_xyz=renderer._renderer.GetDisplayPoint()
        assert np.allclose([x[i],y[i],z[i]],vtk_xyz,atol=1.e-4)


def test_visibility_record_validates_cumulative_state(tmp_path):
    from src.orbit.core import save_json
    from src.orbit.checkpoints import save_or_reuse_visibility
    f=tmp_path/'015'; f.mkdir(); save_json(f/'checkpoint.json',{'photo_status':'NOT_GENERATED'})
    current=np.array([True,False,True,False],dtype=bool)
    past=np.array([False,False,True,False],dtype=bool)
    total, meta, reused=save_or_reuse_visibility(root=tmp_path,angle=15,
                       geometry_hash='known',visible=current,previous_seen=past)
    assert not reused and meta['newly_visible_vertices']==1
    assert total.tolist()==[True,False,True,False]
    _, _, reused=save_or_reuse_visibility(root=tmp_path,angle=15,
                       geometry_hash='known',visible=current,previous_seen=past)
    assert reused


def test_checkpoint_is_portable_and_ignores_external_path(tmp_path):
    from PIL import Image
    from src.orbit.core import inspect_image, save_json
    from dataclasses import asdict
    from src.orbit.checkpoints import existing_geometry_is_valid
    image=tmp_path/'geometry_native_1080x1920.png'
    Image.new('RGB',(1080,1920)).save(image)
    evidence=asdict(inspect_image(image,source_kind='native_3d_render'))
    evidence['path']='/not/a/valid/workspace/old_geometry.png'
    meta=tmp_path/'checkpoint.json'
    save_json(meta,{'mesh_geometry_sha256':'model', 'reference':evidence})
    assert existing_geometry_is_valid(meta,'model')
    image.unlink()
    assert not existing_geometry_is_valid(meta,'model')


def test_stable_project_versioned_filenames():
    from src.orbit.release import deliverable_name
    assert deliverable_name('project','v0001','zip')=='wildlife-bodybuilder-project-v0001.zip'
    assert deliverable_name('project','v0002','zip')=='wildlife-bodybuilder-project-v0002.zip'
    with pytest.raises(ValueError):
        deliverable_name('project','version2','zip')


def test_audit_detects_real_vertex_occlusion_record_tampering(tmp_path):
    from src.orbit.audit import verify_orbit
    # The auditor is a separate, stricter validation layer than image dimensions.
    # A missing orbit manifest is an error, not a silent empty report.
    with pytest.raises(FileNotFoundError):
        verify_orbit(tmp_path,spec=OrbitSpec())


def test_diagnostic_mask_colors_mean_what_they_claim():
    from src.orbit.visibility import visibility_vertex_colors
    seen=np.array([False,True,True],dtype=bool)
    new=np.array([False,False,True],dtype=bool)
    colors=visibility_vertex_colors(seen,new)
    assert colors.shape==(3,3) and colors.dtype==np.uint8
    assert (colors[0]!=colors[1]).any() and (colors[1]!=colors[2]).any()
    with pytest.raises(ValueError):
        visibility_vertex_colors(seen,np.array([True,False,False]))
