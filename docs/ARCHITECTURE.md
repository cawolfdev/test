# wildlife-bodybuilder: Architecture and design goals

## Goal and nonnegotiable invariants

Reconstruct one fixed identity-preserving human subject from the existing frontal/60° photographs. Rotate **only the camera** through 0, 15, 30, 45, 60, 75, 90, 105 and 120 degrees. Maintain stable human skull, hands-behind-head pose, articulated arms, torso and physique; generate **one independent native portrait-HD photograph per checkpoint**, based on the corresponding 3D view, carrying previously reconstructed appearance forward. Never use panel extraction or upscaling as photo generation.

The existing model is a **crude, unfitted proxy** with distorted facial surface and partial legs. It is suitable for testing camera projection and visibility, not for final photorealistic render. A 3D diagnostic image at 1080 × 1920 is NOT an HD photograph.

## Architecture: reusable primitives, then domain operations

1. `src/orbit/core.py` provides atomic JSON, SHA-256 and image provenance/dimension checks. Independent from VTK and bodybuilder domain.
2. `src/orbit/domain.py` specifies fixed orbit/camera math and single-view photographic intent. Pure calculations only.
3. `src/orbit/visibility.py` projects 3D vertices against a *shared whole-body camera scale*, tests front-facing geometry against the renderer's **actual z-buffer**, and records new/cumulative exposure as packed masks. Pure NumPy.
4. `src/orbit/render.py` adapts the fixed GLB to VTK native-HD frames, offscreen z-buffer and optional full-HD color-coded diagnostics. Never changes geometry.
5. `src/orbit/checkpoints.py` reuses verified geometry, stores portable **relative** checkpoint paths, per-angle exposure masks and separately validated native photographs. All changes are resume-safe.
6. `src/orbit/pipeline.py` sequences reusable checkpoint functions, persisting output after every step; no per-angle special cases.
7. `src/orbit/audit.py` independently verifies every angle, original mesh/PNG digests, dimensions, relative paths and cumulative visibility consistency.
8. `src/orbit/release.py` packages an audited run under consistent project-prefixed filenames and sortable `v0001`-style version suffixes.
9. `cli.py` and `build_release.py` are thin terminal adapters.

Dataflow: stable mesh and orbit spec → **native 3D render** → renderer z-buffer → visible mask → newly exposed mask → portable checkpoint → independent full-HD *photographic generator, not connected* → native photo provenance and silhouette/landmark checks, *not implemented* → accepted photograph → next step.

## Measured improvement this version

Prior visibility was estimated from outward-facing normals alone, and could count **occluded back surfaces** as newly exposed. Now measured visibility is the intersection of the frame, facing normal and sampled z-buffer depth. This directly tests what the 3D camera renders. The pure camera projector has a regression test against VTK's native camera projection. The viewpoint is camera-only and the source geometry hash never changes.

Caveat: Visibility is sampled **at mesh vertices**, rounded to the nearest raster pixel with a small depth tolerance. It is not a full-triangle visibility atlas or texel-level UV unwrapping. Values are diagnostic, not percentage of surface area or texture completeness.

## Valid expectations

- Nine separate, native 1080 × 1920 geometric renders. No collage, crop or resize.
- One immutable 92,930-vertex mesh for the entire orbit.
- Portable checkpoint state, expected native dimensions, image hash and newly visible mask per camera angle.
- Re-runs reuse image bytes, recheck visibility, and reject missing/altered data.
- A model's inaccessible surfaces will not be mistaken for visible just because their normals face the camera.

## Unmet requirements and next priorities

1. **Fitted anatomy**: replace the crude proxy with a fitted articulated mesh matching the user's face, massive physique, hair and two independent pose photographs. Preserve topology/rig and prove landmarks and silhouette alignment at 0° and 60°.
2. **True surface correspondence**: map visible pixels from source photography to specific model UV texels and keep uncertainty on unseen regions. The current vertex mask is insufficient for texture transfer.
3. **Native independent photographic synthesis**: secure an accessible generator that accepts the specific checkpoint geometry and yields a single frame at least 1080 × 1920, with trustworthy source provenance. Current tool outputs did not satisfy these requirements.
4. **Photo acceptance beyond provenance**: compare silhouette, anatomical landmarks, viewpoint and identity against projected geometry; reject/redo invalid angles without propagating errors.
5. Only then extend 15° → 120° as an independently generated photo sequence.

## Delivery/quality policy

Every downloadable filename begins `wildlife-bodybuilder-`, uses a stable semantic stem and sortable version suffix before the extension: e.g. `wildlife-bodybuilder-project-v0001.zip`. Internal files are arranged by purpose and angle; checkpoint references are relative to their own folder, not absolute system paths. The project release retains Git history and source tests. Diagnostic preview colors: **blue = visible from previous steps, amber = newly exposed at current step, slate = not currently visible**. Colors mark sampled vertices on a fixed mesh; they are not new photographic texture.

## v0002 diagnostic gate and full evidence retention

- `segmentation.py`: source-specific but reusable color-seeded GrabCut extraction; masks are estimated and recorded as unreviewed.
- `registration.py`: constrained, camera-only silhouette overlap and full-HD red/cyan outline diagnostics at 0° and 60°. No mesh deformation. IoU below 0.82 blocks progression; this threshold is provisional and does not replace landmark/identity validation.
- `mesh_quality.py`: objective mesh topology measurements, with manually reviewed anatomical coverage warnings. The current incomplete/open mesh is never considered photo-ready.
- `evidence.py`: SHA-verified lossless historical attempt ingestion; all nine true native-HD visibility diagnostics and manifests; end-to-end evidence integrity audit.
- `release.py`: writes canonical report into `reports/` before packaging. Exports `docs/OVERVIEW.md` from within repository, delivers a separate complete evidence zip. Source and all diagnostics stay reproducible.

Key honesty constraint: reference masks and overlaid registration *diagnostics* can be resized for clear review; **no such derivative is called an independently generated photo**. The photo-generation acceptance gate remains unopened pending a substantially better rigged model.
