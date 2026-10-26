# wildlife-bodybuilder: current overview

## Acceptance contract
- Exactly one stationary anatomically coherent subject; head and arms do not turn toward orbiting camera.
- Angles: 0° through 120° in exact 15° steps.
- One independently generated full-resolution 1080 × 1920 (or higher) photographic image per angle, native provider output, unmodified and not cut from a collage.
- The original personal-photo references determine facial identity, while textured forward-spiked short-sided hair, dense diffused stubble, amber eyes and exaggerated anatomically connected musculature remain stable.
- Model fitting must precede photographic generation; record geometry-projection comparisons and reject frames with unjustified mismatch.
- Archive all failed image attempts, including image bytes and SHA-256; all geometric visibility diagnostics are retained.
- Review current files in place; use Git history rather than separate immutable versioned overview/report copies.

## Latest local measured outcomes
- 9 native 1080 × 1920 *geometric* checkpoints; 9 occlusion-aware visibility diagnostic views.
- Approximate un-fitted and non-watertight proxy: 60 boundary edges, no complete lower legs or fitted face; not photo-ready.
- Estimated silhouette intersection-over-union from approximate references: 0° = 0.715; 60° = 0.760, below provisional 0.82 gate.
- Historical rejected photographic attempts now 14, including 4 new multi-view montage failures.
- Accepted native full-resolution photographic orbit frames: 0/9.
- Both 0° and 60° reference images remain approximate, not true, verified geometric baseline views.

## Publication limitations
Remote branch `cawolfdev/test: wildlife-bodybuilder-portrait` exists. This connector-created branch contains project overview/plan/report updates; it cannot yet be claimed as a complete mirror of the local 3D model, generated binary imagery or full commit history. Verify tree and SHA-256 for every tracked file before calling synchronization complete.

## Root-cause focus
The original 3D proxy cannot represent the user's true anatomy and pose. An image generator that emits montages and bends anatomy cannot substitute for a fitted, immutable 3D model. Require single native photographic generations against the geometric checkpoint and never crop.
