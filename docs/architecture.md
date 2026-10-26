# Camera orbit: architecture contract (review before implementation)

## Goal and minimal input

Given an **existing full-resolution source portrait**, deliver a fixed-subject 120° camera orbit as **nine independent full-frame images** at 0°, 15° ... 120°. Reuse the 0° image unchanged. Preserve the same character, expression, body, camera optics and environment. Every newly exposed surface requires genuine additional evidence or explicitly identified synthesis, not enlargement of an atlas crop.

Required inputs: `source_image`, `target_angle` (default 120), `step` (default 15), `output_directory`. An optional immutable `model` and additional reference photos improve constraints; missing calibrated views reduce confidence, not input validity.

## Two layers

1. **Core plumbing**: reusable coordinate geometry, image dimensions/hashing, serializable immutable state, full-frame validation, files and comparison display. Inputs and outputs are data; calculation functions have no side effects.
2. **Orbit domain**: plan a sequence of camera poses, re-use existing source and checked checkpoints, supply fixed-model guide for each new camera pose, request **independent** HD synthesis when a new image is needed, register its image and evidence, validate acceptance, proceed to the next angle only after acceptance. The rendering/synthesis adapter is separate from planning. It must not silently substitute an atlas crop or a low-resolution proxy.

## End-to-end dependency

`primary photo + fixed subject` → `orbit plan` → `geometry guide 15°` → `new full-frame HD view 15°` → `validate + checkpoint` → ... → `geometry guide 120°` → `new full-frame HD view 120°`.

Each checkpoint references its immediate predecessor; the camera moves but the subject's world-space model stays fixed. Geometric guides are conditioning/diagnostics, **not** photographic results. A synthesized frame may be plausible yet geometrically wrong; report that separately.

## Use cases and expectations

Valid:
- Reuse a pixel-identical 0° anchor, existing code, and any independently generated HD checkpoint that passes provenance and quality gates.
- Resume an interrupted 15° chain from a valid last checkpoint.
- Diagnose occlusion and new surfaces with one fixed 3D proxy before generating a new full-sized view.
- Refine/replace the geometric model between *runs* and rerender all geometry guides for consistent comparisons.

Invalid:
- Treat crops of an atlas, resized 300px images, or upscaled thumbnails as independent HD frames.
- Treat an ellipsoid proxy as a fitted photoreal human scan.
- Assume an AI-synthesized angle is metrically accurate without registration/calibration.
- Reuse a nominal 60° image as confirmed 60° if the visible anatomy contradicts that angle.
- Change the subject pose or 3D anatomy between orbit viewpoints.
- Claim pixel-level consistency of synthesized fur/hair/details on unseen surfaces.

## Quality gates and evidence

Structural gates: unbroken 15° chain, hashes, dimensions >= 1024 each side, origin=`anchor` or `independent_generation`, image decoding, distinct new-view hashes, no crop provenance, fixed-model digest.

Visual review gates: face/hair identity, huge pectoral/shoulder mass, front/back anatomical occlusion, posture, environment, apparent camera azimuth, fur continuity. Visual review is a separate manual verdict: machine-passing files cannot self-certify anatomical accuracy.

## Failure strategy

A rejected candidate is kept as a rejected artifact with an explanation. It does **not** become the predecessor for the next stage. Reuse of any prior candidate is allowed only after the reviewer confirms its angle and fidelity. No silent substitutions.

## Model development

Keep the first shared 3D model immutable within a run. Improve the model iteratively using identifiable geometry defects, compare the 0° projection to the reference and 60° geometry to the claimed camera, then launch a new versioned run. Existing source/geometry functions should be reused; adding one-use low-level render utilities is discouraged.

## Current limits

The existing GLB is a coarse ellipsoid proxy, not a scanned human model. The chat image-generation tool cannot be called as a Python renderer or automatically consume a GLB as a conditioned 3D scene. Full-HD independently generated frames can be ingested by the domain pipeline, but 3D-conditioned photographic generation and exact identity continuity cannot currently be *enforced* by that pipeline.
