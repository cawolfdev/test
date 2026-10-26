# wildlife-bodybuilder: File and function map

| Path | Responsibility | Keep |
| --- | --- | --- |
| `assets/geometry/fixed_pose_proxy.glb` | Original single *unfitted* geometric proxy (immutable) | Yes |
| `assets/references/front_original.png` | Identity, frontal pose, photographic treatment | Yes |
| `assets/references/angle_060_original.png` | Secondary appearance/spatial reference | Yes |
| `src/orbit/core.py` | Atomic JSON, checksums, image dimensions and source-evidence validation | Yes |
| `src/orbit/domain.py` | OrbitSpec, fixed camera basis, global framing, one-view photo brief | Yes |
| `src/orbit/visibility.py` | Pure orthographic projection, raster-depth comparisons, bit-packed masks, exposed-surface diagnostics | Yes |
| `src/orbit/render.py` | VTK mesh import, native raster and z-buffer, diagnostic vertex-color rendering | Yes |
| `src/orbit/checkpoints.py` | Resume/reuse, portable evidence, accumulated visibility, native-photo acceptance | Yes |
| `src/orbit/pipeline.py` | Iterate 15° checkpoints, save state and print progress | Yes |
| `src/orbit/audit.py` | Independent consistency audit and release gate | Yes |
| `src/orbit/release.py` | Stable versioned filename contract, release artifact assembly | Yes |
| `cli.py` | Thin orbit execution CLI | Yes |
| `build_release.py` | Thin audited package CLI | Yes |
| `tests/test_orbit.py` | Regression tests for geometry, visibility, portability, dimensions, naming | Yes |
| `output/orbit_000_120/<angle>/geometry_native_1080x1920.png` | Native HD geometry render, unchanged between runs | Generated |
| `output/orbit_000_120/<angle>/visibility.npz` | Current, new and cumulative exposure masks (packed vertex booleans) | Generated |
| `output/orbit_000_120/<angle>/checkpoint.json` | Per-angle portable provenance and status | Generated |
| `output/orbit_000_120/{015,120}/geometry_exposure_native_1080x1920.png` | Optional native HD visibility diagnostics (not photo) | Generated |
| `output/orbit_000_120/{state,verification}.json` | Whole-orbit state and independent audit | Generated |
| `.git/` | Prior project commits and continuing incremental refactor | Yes, in project archive |

Excluded: legacy montage extraction/upscaling scripts, photo crops, per-angle mesh duplicates, temporary previews, test caches. Original archives remain outside the active project. All published artifact *basenames* use `wildlife-bodybuilder-<role>-vNNNN.<extension>`.

## v0002 additions

- `src/orbit/segmentation.py`: `letterbox_rgb`, `segment_reference_subject`, `geometry_silhouette`; bounded source extraction, no model mutations.
- `src/orbit/registration.py`: `warp_mask`, `mask_metrics`, `fit_camera_only`, `draw_comparison`, `compare_reference`; pure image-space calibration and stored failures.
- `src/orbit/mesh_quality.py`: `measure_mesh_quality`; open-boundary and anatomical coverage limits.
- `src/orbit/evidence.py`: `record_rejected_attempts`, `render_all_visibility_diagnostics`, `inspect_evidence`.
- `analyze_references.py`: thin reusable diagnostic CLI.
- `collect_evidence.py`: one-time legacy import adapter, never an inner-loop photo-generation stage.
- `docs/OVERVIEW.md`: persistent high-level state, separately exported.
- `docs/PLAN.md`: goal, phases and quality gates.
- `reports/current.json`, `reports/report-v0002.json`: in-repository summary and archived version.
- `evidence/rejected/`: all available rejected image bytes plus manifest.
- `evidence/visibility/`: complete 0–120° 15° diagnostic sequence plus manifest.
- `output/registration/`: two measured silhouette failures with masked source evidence.
