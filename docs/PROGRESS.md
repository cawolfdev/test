# Progress and decision log

## Baseline audit
- Recovered source GLB and verified it contains 92,930 vertices.
- Confirmed the prior standalone photographic images were 330×501 montage crops, followed by enlarged 1024×1536 displays.
- Kept the existing GLB and two actual independently generated photographic references.
- Found no working Python-callable image generator and no fitted rigged anatomical model.

## Iteration A: Structural refactor
- Separated general I/O, pure orbit math, 3D rendering, orchestration and tests.
- Created strict native-resolution/provenance checks, rejects historical crop/upscale category even if file dimensions happen to pass.
- Fixed world-space framing and camera-only rotation, one immutable mesh across all checkpoints.
- Retained one geometry authority; removed repeated full-mesh snapshots from active representation.

## Iteration B: Execution status
- See `output/orbit_000_120/state.json` for machine-verifiable checkpoint completion.
- Geometry checkpoints are native high definition; independent HD photographic generation remains unimplemented and is explicitly marked pending.

## Next iteration acceptance tests
1. Use a fitted articulated mesh, not the proxy.
2. Validate projected landmarks/silhouette against two independent photographic references.
3. Obtain one independently generated **native** 1080×1920-or-greater photo at 15°, with verified provenance and alignment before generating 30°.
4. Report per-checkpoint success and failure; no composite source images.

## Iteration C: Validate/photo provenance and resumption
- Added reusable checkpoint-domain functions so re-running does not regenerate unchanged views.
- Photo gate accepts only direct, native, independent output with explicit provider generation ID. It copies original bytes unchanged; cannot crop/upscale.
- Single-shot photo generation test returned a 1536×1024 labeled collage and was rejected; no angle photo marked complete.
- Earlier 3D mesh remains a rough test fixture: face and lower legs visibly unfitted.

## Iteration D: Final geometry delivery and packaging
- Nine separate native 1080×1920 VTK camera renders verified on disk, each with exact SHA-256 recorded in `output/orbit_000_120/verification.json`.
- 8 unit tests pass, including geometry-camera convention, framing, resolution, provenance rejection and checkpoint-resume behavior.
- No legacy cropped/upscaled panel is reused as a deliverable. The independently requested new image test also returned a collage and is rejected.
- Kept actual photorealistic generation pending. The existing mesh remains an unfitted proxy whose facial geometry and limbs are visibly inaccurate.
- Old extracts, nine copies of mesh state and prior montage crops are not included in this workspace's active files.

## wildlife-bodybuilder: Canonical naming and accuracy iteration (v0001)
- Copied the existing cleaned project into `wildlife-bodybuilder`, preserving Git history and all canonical reference assets.
- Fixed the stored checkpoint-path bug: previously, metadata used absolute references into a different workspace. Relative local paths now validate after relocation; existing PNG bytes reused unchanged.
- Added `visibility.py`: projects fixed-mesh vertices using global camera framing; validates each against VTK's actual raster z-buffer before counting exposure.
- For 0° through 120°, recorded new/cumulative exposed vertex masks at each 15° step. Unlike the previous normal-facing heuristic, rear occluded vertices cannot count as exposed until actually in view. Z-buffer visibility is sampled, not exact surface coverage.
- Created native 1080×1920 15° and 120° *geometry* diagnostics with amber highlighting newly exposed vertices, blue earlier-exposed visible areas. These are not photos.
- Added independent audit covering model hash, PNG hashes, native dimensions, relative paths, sequential angles and accumulated masks. All checkpoints pass.
- Camera projection math compared numerically to native VTK output; previously a subset-scaled camera helper was corrected.
- Migrated deprecated VTK cell-array implementation, keeping the same immutable mesh.
- Established fixed artifact roles and sortable versions: `wildlife-bodybuilder-<role>-v0001.*`, to increment to `v0002` next release.
- Test suite: 16 passing at this stage; no independent native-HD photo accepted. Main blocker remains fitting a genuinely articulated anatomical model and binding photographic generations to its exact geometry.

## wildlife-bodybuilder v0002: goal-first reconstruction quality and complete evidence

- Implemented deterministic reference silhouette segmentation, restrained camera-only silhouette registration, overlaid 1080×1920 diagnostic images, and numeric results from both existing photo views.
- 0° IoU 0.715; 60° IoU 0.760. Both fail the provisional 0.82 gate; model remains unfitted. Reference masks are estimated and need manual verification.
- Measured model topology and full-body coverage; explicitly blocked ready-for-photo status for incomplete head/legs and open mesh boundaries.
- Copied **all 10** currently available, non-reference historical unaccepted image generations to `evidence/rejected/` losslessly, SHA-256 recording each original source filename and failure/limitation reason. Both actual primary reference frames remain in `assets/references/`.
- Rendered the **full set of nine** 1080×1920 visibility diagnostics, not just 15° and 120°. Stored source diagnostic masks and numeric alignment failures for 0° and 60°.
- Duplicated a progress contact sheet into chat and stored it under `evidence/progress/`. Contact sheets are diagnostics only, never passed off as individually generated photos.
- Added `docs/PLAN.md`, `docs/OVERVIEW.md`, and in-repository versioned/current JSON reports; release assembles a separate evidence archive and preserves consistent project-prefixed versioned filenames.
- The next underlying task is correcting mesh geometry, **not** tuning photo prompts or stretching low-resolution images.
