"""Deterministically render all 24 context-free image prompts; run during setup."""
from pathlib import Path

ROOT = Path(__file__).parent
BASE = '''Create exactly ONE independent photorealistic full-body studio photograph of ONE fictional adult male hypermasculine character. ONE person only; absolutely no multiple figures, comparison lineup, duplicate views, captions, labels, panels, typography, or collage. Vertical 1024x1536 composition, entire body from hair to soles visible with generous margins, frontal three-quarter-neutral view, camera aligned at torso height and fixed distance, figure occupying about 78% image height. 200 cm character height; do not use photographic wide-angle distortion. Neutral pale-gray seamless studio backdrop, soft flat diffuse daylight, realistic tones without blown highlights or crushed shadows. Natural-looking pores, skin, body hair, subtle surface variation and realistic skin translucency; never plasticky, waxy, CGI, illustration, artificial shine, or leathery. Dark matte fitted mid-thigh athletic shorts, barefoot, shirtless, nonsexual presentation. Same identity in the entire project: adult approximately 35-year-old rugged Californian man, short sandy-blond hair, gray-green eyes, neat coarse stubble, fair lightly sun-weathered skin, distinctive slight scar above left eyebrow, identical face identity and styling unless the requested morphology attribute changes. All body parts complete and anatomically coherent: two arms, two hands each with five correctly formed fingers, two legs, two feet, no stray limbs or fusion. No cropping of head, fingers or feet.

THIS IS A SINGLE CHARACTER GENERATION FROM SCRATCH: no input images; no reference to any prior outputs; do not scale, crop, edit, clone or transform earlier pictures. Render ONLY the stated level. This request stands alone and contains all context.

Absolute locked baseline for all NONVARYING attributes:
M=1: already 400% of an elite professional bodybuilder's overall muscular bulk, absurdly colossal projecting thick pectorals, spherical deltoids, heavy traps, peaked biceps and triceps, titanically thick forearms, huge quadriceps, hamstrings and calves, deeply carved muscle separations; far beyond human physiology but every muscle recognizable. This is the STARTING value, NEVER a normal or ordinary athlete.
A=1: extreme adult masculine visual authority and assured, grounded relaxed confidence, rugged styling and presence, not aggressive or angry.
F=1: monumentally square broad jaw and chin, projecting brow, heavy cheekbones, wide robust nose, thick neck, exceptional skeletal shoulder breadth and deep rib cage, robust pelvis, large hands, thick wrists and ankles. Already physically impossible idealized male structure.
T=1: extreme stylized androgen-associated visual markers, dense coarse adult stubble, heavy eyebrows, substantial adult body hair distribution, rugged realistic skin texture. T is NOT an actual hormone measurement.
'''

M = [
('1','Exactly baseline M=1, already 400% elite-bodybuilder total muscle bulk: physically impossible, monstrously muscular at the START. Every muscle group colossal and sharply recognizable.'),
('2','M=2: twice the M=1 overall muscle volume. Colossal muscle bellies project farther in 3D; massive thick forearms and calves remain proportional to already enormous arms and legs.'),
('3','M=3: triple M=1 total muscle bulk, thicker deeper pectorals, deltoids and thighs, enormous forearms and calves; anatomical contours remain distinct.'),
('4','M=4: four times M=1 overall muscular bulk; shoulders, pecs, arms and legs become exceptionally broad and deep, distinct sharp valleys.'),
('5','M=5: five times M=1 total muscle bulk, impossibly mountain-like projected muscle mass; forearms and calves not neglected.'),
('6','M=6: six times M=1 total muscle bulk, overwhelming deltoid spheres, hanging thick pectoral slabs, tremendous traps and massive lower limbs.'),
('7','M=7: seven times M=1 muscle bulk, anatomy stretched to wildly impossible colossal volume while retaining separations and coherent attachments.'),
('8','M=8: eight times the already impossible M=1 overall muscle bulk, tremendous recognizable muscle forms dominate silhouette; do not enlarge bone geometry or facial structure, keep all eight groups distinctly formed.'),
]
A = [
('1','A=1: already extreme masculine visual presence; a very grounded relaxed posture, calm confident neutral expression, subtle gaze directly ahead. No extra exaggerated pose.'),
('2','A=2: more commanding stance and grounded foot placement, calm chin-forward composure, minimally stronger physical authority; no anatomy alterations.'),
('3','A=3: striking assured masculine presence through chest bearing and gaze, not bigger chest or skeleton; natural face, no sneer.'),
('4','A=4: imposing but relaxed confidence, broad measured stance and settled shoulders; extraordinary presence without aggression.'),
('5','A=5: profoundly confident adult bearing, statuesque silhouette via posture only, steady intense yet welcoming expression.'),
('6','A=6: nearly mythic self-assurance and serene authority; slightly chin-raised, relaxed powerful stance, hands at sides, no enlarged anatomy.'),
('7','A=7: overwhelming masculine gravitas in gaze and grounded posture, still natural candid appearance, no flexing or angry expression.'),
('8','A=8: maximum impossible masculine presence, utterly assured calm adult confidence and commanding posture; still no body, face geometry, or hair changes.'),
]
F = [
('1','F=1: already massively exaggerated square jaw, brow and skeletal shoulder structure at baseline 400% conceptual masculine-feature exaggeration. Not an ordinary male face or frame.'),
('2','F=2: enlarged skeletal clavicle breadth, slightly more squared and broad mandible, heavier brow and wrists versus already impossible F=1.'),
('3','F=3: extraordinary squared craniofacial geometry, heavy cheekbones and chin, thick skeleton and hands, with muscle BULK unchanged.'),
('4','F=4: monumentally broad jaw corners, robust nasal bridge, projecting brow, deep chest cage and wider clavicles; keep muscle tissue volume unchanged.'),
('5','F=5: nearly sculptural heavy-boned giant, very broad thorax and structural shoulders, enlarged robust head and wrists, no extra muscle volume.'),
('6','F=6: dramatic extreme square jaw and skull, colossal clavicles and rib cage structure, vast skeletal frame but M remains the same in absolute total muscular bulk.'),
('7','F=7: impossible heavily squared skeletal architecture, intense jaw and brow projections, broad pelvis/ankles, still recognizable facial identity.'),
('8','F=8: peak absurd masculine skeletal morphology with granite-like squared jaw, heavy brow, huge broad bone frame and hands; no additional muscle mass or changed T and A.'),
]

for idx, title, lvls in [(1,'Muscle size (M)',M),(2,'Masculine presence (A)',A),(3,'Masculine facial and skeletal features (F)',F)]:
    for level, change in lvls:
        fixed = {1:'A=1, F=1, T=1', 2:'M=1, F=1, T=1', 3:'M=1, A=1, T=1'}[idx]
        dimension = {1:'Muscle size (M)', 2:'Masculine presence (A)', 3:'Masculine facial and skeletal features (F)'}[idx]
        lock = {
            1:'Vary ONLY muscular tissue volume, NOT facial geometry, skeleton, beard, body hair or confidence/body language.',
            2:'Vary ONLY bearing, presence, posture, and expression, NOT any skeletal dimensions, hair growth, skin, or muscle size.',
            3:'Vary ONLY underlying skeletal geometry and head/face morphology, NOT muscle volume, androgen-coded surface traits, or expression.',
        }[idx]
        prompt = BASE + f'\nOUTPUT: image_{idx}_{level}.png.\nATTRIBUTE: {dimension}. LEVEL: {level}×.\nHOLD CONSTANT: {fixed}.\n{lock}\nTARGET: {change}\nPhotorealism above all. ONE complete coherent full-body character centered. No labels or other people.\n'
        (ROOT / 'prompts' / f'image_{idx}_{level}.txt').write_text(prompt, encoding='utf-8')
print('Wrote 24 complete individual, stand-alone prompts.')
