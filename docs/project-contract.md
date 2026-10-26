# wildlife_anthrowolf | v0.2 task contract

## User-visible outcome
Produce an orbit of **one** stationary, immense human-faced anthro-wolf bodybuilder in 15° camera increments from a fixed 0° reference to 120°. Every accepted photographic view is a **native full-resolution independently rendered image**, not an atlas crop, rotated pixels, or an upscaled preview. The 3D model is geometric evidence, not evidence of photorealism. Distinguish these artifacts.

## The simplest task-level interface

`prepare(source, model, target=120, step=15)` -> immutable job, camera plan and per-angle 3D guides.

`next(job, accepted_frames)` -> exactly one request for the immediately next angle, with immutable subject / model hash, previous accepted image hash, camera guide and expected scene information.

`accept(job, candidate, provenance, review)` -> either a validated full-size immutable checkpoint, or a clearly failed candidate. Only accepted checkpoints advance the sequence.

`report(job)` -> completeness and quality limitations; never infer pose or identity correctness solely from hashes or pixel dimensions.

## Architectural separation

**Core (pure first):** `geometry` for camera definitions, `surface` for fixed-model ray intersections, `assets` for hashing/preservation; generic `frame_requirements` for source dimensions. All functions deterministic for the same numeric and binary input. Image rendering and filesystem copying are adapters at the boundary.

**Domain (pure first):** `hd_orbit` for angle schedule, next-task planning, materialized-evidence invariants, stage acceptance and progress. A rendering adapter produces a candidate; the domain never silently substitutes geometry guides, atlas tiles, UV projections or synthetic upscaling for photographic evidence.

**Adapters:** `tools/hd_orbit.py` is a thin CLI. `render_guides` produces full-size geometric conditioning only. Existing `texture_orbit` survives solely for historical surface-coverage experiments.

## Integration sequence and failure gates

1. Audit available files and functions before change; reuse existing `surface.cast_visible_surface`/`hd_orbit`.
2. Identify uncalibrated reference 0° and record its native dimensions and hash. Lock one model hash for a run.
3. Generate and review all fixed-model 3D guides at requested angles; verify 120° correctly occludes chest.
4. Register the unmodified 0° anchor. For each subsequent step request native-HD generation conditioned by prior accepted frame, **and fixed 3D guide**.
5. Reject a candidate if not native HD, if crop/upscale/atlas provenance, if no predecessor dependency, if camera angle is wrong, or if visually inconsistent; never propagate a rejected candidate.
6. Record individual image and frame hashes. Store validation status distinctly from visual review. Resume from last accepted stage.
7. Refine the model between **versions** only, rerender guides, rerun silhouette validation and preserve earlier version evidence.

## Valid and invalid expectations

Valid: repeatable 3D guides, deterministic angle schedule, native 1024+px output requirement, source preservation, hash-linked checkpoints, visual-review workflow, and resumable pipeline.

Invalid: assume coarse primitive ellipsoids are a detailed fitted human model; assume image-generator output is angle-calibrated because prompt says 15°; invent newly revealed rear anatomy by remapping frontal pixels; claim a generator was automatically driven through the 3D assets without an API accepting those assets; claim successful 120° photographic result if there is only a 3D guide.

## Explicit scope of this version

*Keep* the existing reusable high-level orbit and intersection functions. Improve domain provenance to catch **source/model changes**, and add a sequence-of-tasks manifest for the full run. Produce and package 1152px geometry guides, not counterfeit photo frames. Independently generated photo frames, if any, must be registered and separately reviewed.
