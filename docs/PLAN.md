# Goal-first roadmap and acceptance criteria

## Ultimate user-visible goal

A recognizable individual, one coherent hands-behind-head body and fixed skull, and an independently generated **native >=1080×1920 photographic image at every 15°** from 0° to 120°. No tiling, collage extraction, disguised enhancement, mesh reposing, head-turning or unverifiable photo provenance.

## Why the previous approach failed

The first image-generation series independently hallucinated every viewpoint; the next 3D proxy was reconstructed from a partial torso photograph and possesses incomplete lower limbs, inaccurate head/arms and open boundaries. More photorealistic texture cannot correct geometry.

## Stage 1: lock shared geometry and measure deviations [implemented diagnostics, model failing]

- One immutable 92,930-vertex test mesh; camera-only orbit from 0° to 120°.
- Native 1080×1920 geometry frame and z-buffer at each angle.
- Extract source masks with deterministic, documented color-seeded GrabCut (estimates, *not human-reviewed labels*).
- Align projection only by uniform camera framing scale and image translation: no subject deformation.
- Report silhouette IoU and overlay disagreements at both available source perspectives.
- Explicit gate: IoU >=0.82 at both 0°/60° **plus manual review**. IoU is diagnostic, not a guarantee of identical identities or 3D correspondence.

## Stage 2: build anatomically complete, riggable replacement mesh [blocked]

- Obtain and legally source a rigged anatomical human model or reconstruct full topology accurately.
- Correct head, face, shoulder joints, hands clasped behind head, muscle fiber masses and complete legs.
- Fit one mesh to original frontal and 60° references *without using the photo view to modify pose*.
- Preserve landmark geometry across all viewpoints, audit watertightness/open boundaries and rig consistency.

## Stage 3: native photographic image synthesis [blocked]

- An engine must accept a specific native-HD rendered reference image (not a text-only angle caption) for each stage.
- Generate precisely one >=1080×1920 independent photographic image per angle.
- Compare silhouette and fixed-pose landmarks to that stage's 3D reference before accepting it.
- Store rejected outputs byte-for-byte with reason and process record; never pass an unaccepted image to the next stage.

## Stage 4: delivery / repeatability [implemented]

- Stable `wildlife-bodybuilder-<role>-vNNNN.<ext>` external artifact names.
- Embed overview, current and versioned machine-readable reports **inside the repository** and publish them separately.
- Deliver a complete evidence archive of every available historical rejected generation and all nine visibility renders, registration masks and failure views.
- Commit independent improvements to local Git before constructing release bundles. Preserve rejected attempts rather than purging provenance when cleaning files.

## GitHub publication and source validity (current)
The destination is `cawolfdev/test` branch `wildlife-bodybuilder-portrait`. Git history is the version record; update existing overview and report documents instead of emitting duplicate version-suffixed copies into the repository. Original 0° and 60° photographic source images are only approximate and must be replaced by independent full-frame, native-resolution generated photographs that are registered to a fixed 3D model. Four new montage attempts were rejected and preserved under `evidence/attempts`. Publication success requires remote tree checks, including hashes for binaries.
