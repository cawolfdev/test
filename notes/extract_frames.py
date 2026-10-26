from pathlib import Path
from PIL import Image
import json, shutil, hashlib
root=Path('/mnt/data/wolf_camera_orbit')
source=Path('/mnt/data/a_wide_high_resolution_composite_image_a_multi_p.png')
atlas=Image.open(source).convert('RGB')
shutil.copy2(source,root/'references'/'generated_atlas_candidate.png')
shutil.copy2('/mnt/data/a_high_resolution_grid_atlas_style_image_overall.png',root/'references'/'rejected_atlas_01.png')
for p in Path('/mnt/data').glob('*.png'):
  if p.resolve() in [source.resolve()]: continue
  name=p.name
  if name.startswith('a_') or name in ['stoic_wolf_man_in_the_alpine_wilderness.png','furry_titan_in_the_alpine_wilderness.png','outdoor_mountain_landscape_portrait_dramatic_real.png','wide_naturalistic_outdoor_portrait_scene_a_highl.png','wide_outdoor_portrait_scene_of_a_hyper_muscular_s.png']:
    d=root/'references'/'generation_history'; d.mkdir(exist_ok=True)
    shutil.copy2(p,d/name)
for p in Path('/mnt/data').glob('100003*.jpg'):
    d=root/'references'/'identity_photos'; d.mkdir(exist_ok=True)
    shutil.copy2(p,d/p.name)
frames={
  15:(300,0,549,417),30:(553,0,802,417),45:(806,0,1059,417),
  75:(0,465,328,937),90:(332,465,655,937),105:(660,465,983,937),120:(987,465,1312,937)
}
for a,rect in frames.items():
    atlas.crop(rect).save(root/'images'/f'{a:03d}_clockwise.png')
shutil.copy2(root/'references'/'00_front_reference.png',root/'images'/'000_clockwise.png')
shutil.copy2(root/'references'/'60_intermediate_reference.png',root/'images'/'060_clockwise.png')
manifest={
 'title':'Wolf bodybuilder fixed-pose orbital views',
 'source_0':'references/00_front_reference.png',
 'source_60':'references/60_intermediate_reference.png',
 'azimuth_degrees':[0,15,30,45,60,75,90,105,120],
 'coordinate_definition':'Camera clockwise in overhead plan, subject always facing 0-degree camera position in world coordinates.',
 'pose':'World-fixed front axis, no independent head/neck rotation intended.',
 'limitations':[ 'Photographs are generative approximations, not calibrated 3D renders.', 'The generated atlas was cropped into individual files; these seven views were not independently generated at full resolution.', '0 and 60 are copied earlier high-resolution references and differ subtly in anatomy/appearance from the generated atlas sequence.', 'Angles printed in the atlas are labels rather than calibrated measured camera positions.', 'Parallax and photographic consistency have not been geometrically verified.' ],
 'files':[]
}
for p in sorted(root.rglob('*')):
 if not p.is_file() or p.name=='manifest.json':continue
 manifest['files'].append({'path':str(p.relative_to(root)),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'manifest.json').write_text(json.dumps(manifest,indent=2))
(root/'README.md').write_text('''# Wolf camera orbit workspace\n\nThe **images/** directory contains 9 standalone angle PNG files. 000 and 060 are the exact preceding source anchors. 015, 030, 045, 075, 090, 105, 120 are single-view crops extracted from an AI-generated angle atlas.\n\nThe **mocks/** directory records the correct camera coordinate system at 15° increments. **references/** stores the anchor images, prior generated candidate frames, four user-supplied selfie references, and a rejected earlier atlas. **notes/** stores the orbit specification and extraction script. **manifest.json** lists file hashes for reproducibility.\n\n## Important limitations\nThis is *not* an exact 3D camera orbit. The camera angles are illustrative rather than calibrated, and the identity and muscular proportions may drift between views. Some intermediate crops are lower resolution than the anchor images. The source camera cannot be recovered exactly from 2D photographs. A true locked-pose 120° orbit needs a consistent 3D model and matched camera rig.\n''')
print('Generated output files:')
for p in sorted((root/'images').iterdir()):
 im=Image.open(p); print(p.name, im.size, f'{p.stat().st_size/1000:.1f} KB')
