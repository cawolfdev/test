# Existing architecture and function audit (2026-10-25)

Read alongside `architecture.md` before making code changes. Reuse and consolidate first.

| Module | Public functionality | Layer | Role and status |
|---|---|---|---|
| `geometry.py` | `Orbit`, `all_orbits` | core | Single clockwise-azimuth convention; reuse |
| `surface.py` | `View`, `SurfaceFrame`, `cast_visible_surface`, `build_mesh` | core | Fixed-model geometric guides; reuse; coarse proxy limitation |
| `proxy.py` | `scene_parts`, `raycast_proxy`, `render_proxy` | core/legacy | Duplicate rendering of geometry; migrate callers to `surface`, avoid expanding this |
| `assets.py` | `sha256`, `copy_if_different`, `pixel_equal`, `extract_atlas` | core/legacy | Reuse hash/copy; **extract_atlas is disallowed for the new HD use case** |
| `texture_orbit.py` | `paint_novel_surface`, `render_surface`, `execute`, checkpoint functions | experimental domain | Retain as experiment; its photo reprojection failed and must not supply HD finals |
| `preview.py` | `contact_sheet` and wrappers | core | Reuse display, but not as an output frame source |
| `validation.py`, `manifest.py` | project validation, complete index | core + legacy domain | Existing historical asset checks; new pipeline validates HD evidence separately |
| `archive.py` | `package_workspace` | core | Reuse packaging helper |
| `cli.py` | legacy `all`, `validate`, `archive` | adapters | Preserve compatibility; add new command only if needed |
| `tools/run_sequential.py` | old UV experiment runner | legacy adapter | Keep as reproducible experiment, not final result |
| `tests/` | proxy tests and state-chain tests | tests | Keep and extend with HD provenance/invalid-case tests |

## Minimal new surface

- `hd_orbit.py`: orbit **business use-case**, immutable stage record, pure plan and acceptance checks, simple file-backed registration driver. Reuses `Orbit`, `sha256`, and existing `contact_sheet`.
- `tools/hd_orbit.py`: thin CLI adapter; no geometric math, image processing, or standalone utility implementations.
- `tests/test_hd_orbit.py`: contract tests of reuse, source immutability, provenance, checkpoint chaining, image size, and crop rejection.

No new rendering engine is proposed. Full-HD images are produced by the image generator or a future source-aware image-renderer adapter, not by pretending UV-painted ellipsoids are photoreal.
