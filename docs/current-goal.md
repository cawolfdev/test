# wildlife-bodybuilder: live goal and evidence, v0002

## Contract

The user-provided `wildlife-anthrowolf--source-character-image.png` is the new **canonical 0°** anchor. The uploaded source is 1312x1199, so it must not be falsely labeled as native 1920x1080. Every generated image accepted at 15° increments must be individually synthesized natively at >=1920x1080 (not upscaled or cropped), reviewed for anatomical continuity, and supported by camera registration to the unchanging model and prior frame. A geometric guide is never a photograph.

## Current blockers

1. The previous `00_front_reference.png` differs in SHA from the new uploaded source. Old photographic atlas tiles therefore cannot be reused as accepted v0002 frames.
2. The only recovered 3D asset is a mesh of ellipsoids (16 parts); it proves azimuth and relative occlusion, **not** identity or the detailed body silhouette.
3. Chat image generation does not expose a 3D-mesh-conditioned rendering interface in this workflow. An attempted independent 15° photograph rotated much further and was delivered at 1312x1199, below the native width requirement. Retain it as rejected evidence and do not propagate it to 30°.
4. GitHub is a public repository. Original user identity photographs in `references/identity_photos` are not suitable to upload without a deliberate privacy decision. GitHub connector Git object creation cannot ingest a local `.bundle` directly; a mapped commit chain is not identical to `git push` preserving existing SHA.

## Existing reusable components

- `src/wolf_orbit/assets.py`: byte hashes and source-preserving copy.
- `src/wolf_orbit/surface.py`: geometric raycast with immutable parts.
- `src/wolf_orbit/hd_orbit.py`: chain validation and frame registration.
- `src/wolf_orbit/orbit_pipeline.py`: run-level pure domain composition; no novel low-level render code.
- `src/wolf_orbit/preview.py`: reusable generic contact sheet.
- `tools/production.py`: CLI adapter, not business logic.
- `runs/v0002/plan.json`: canonical source/model hashes and frame requirements.
- `runs/v0002/report.json`: all checkpoints, missing photograph status, rejected attempts and guide hashes.

## Next work required before photographic sequence

Obtain or construct a genuinely pose-fitted, textured 3D body/head mesh and verify its 0° silhouette against uploaded source. Acquire a render/synthesis adapter that accepts that geometry and source images as actual conditions. Only then synthesize 15°, independently verify pose and angle, register as immutable native-HD checkpoint, and proceed to 30°.
