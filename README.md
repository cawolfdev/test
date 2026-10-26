# Fixed-pose wolf bodybuilder camera-orbit workspace

## Results

Nine **separate** files appear in `images/`, named `000_clockwise.png` to `120_clockwise.png` at 15° intervals. `000` and `060` are **byte-identical** copies of the earlier user-approved 0° frontal and 60° oblique source references. The other seven views are **crops of an existing generated atlas**, rather than independent physically calibrated renderings. The unedited atlas is in `references/generated_atlas_candidate.png`.

`previews/all_angles_contact_sheet.png` makes the photographic sequence easy to inspect. `previews/fixed_pose_geometry_proxies.png` is an independently rendered 3D proxy built from consistent geometry, used to check camera orbit conventions and pose locking. Original plan-view diagrams live in `mocks/`.

**Critical limitation:** The images are visually illustrative. The 60° reference looks closer to a shallower three-quarter view than a metrically calibrated 60°, and the atlas's nominal 90° photograph still reveals too much frontal anatomy to be a precise side profile. The 120° atlas crop is a plausible rear three-quarter composition, not a geometrically verified camera view. Identity, facial morphology, anatomy, fur direction, pose and lighting may drift. The proxy resolves the *coordinate-system* problem, not the unobserved 3D surface of the original image. A true locked-pose orbit requires a consistent 3D asset, stable rig and camera calibration.

## Repeatable, reuse-first commands

From the project root (Python 3.10+, Pillow, NumPy):

```bash
PYTHONPATH=src python -m wolf_orbit.cli validate --root .
PYTHONPATH=src python -m wolf_orbit.cli all --root .
PYTHONPATH=src python -m unittest discover -s tests -v
```

Running `all` reuses extracted source images and existing generated previews by default. It extracts from the atlas only when a view is missing. `--replace` explicitly re-extracts photographic atlas crops and recomputes geometry mocks, without regenerating images with AI. Source anchors are always copied unmodified from `references/` when necessary.

- `src/wolf_orbit/geometry.py`: camera coordinates, front-axis and fixed world pose.
- `src/wolf_orbit/assets.py`: content hashing, source reuse, atlas extraction.
- `src/wolf_orbit/proxy.py`: reusable independent ray-cast ellipsoid model with real geometric occlusion for angle-validation mocks.
- `src/wolf_orbit/preview.py`: shared gallery maker for photographs and geometry models.
- `src/wolf_orbit/validation.py`: programmatic invariants, pixel equality checks and known limitations.
- `src/wolf_orbit/manifest.py`: SHA256 inventory and validation report.
- `tests/`: unit/regression tests, including 120° back/pectorals occlusion and immutability of source photos.
- `notes/extract_frames.py`: retained legacy one-shot script, **superseded by the modular code**. Do not run it to update the project.

`manifest.json` indexes deliverable files and their hashes; `validation_report.json` separates automated test successes from unresolved photographic accuracy limitations. Git history records the baseline import, extraction/validation refactor, 3D proxy, and packaging pass.

## Provenance and data handling

`references/` includes all contributing prior model-generated images and four selfies provided for facial identity, because the request was to capture all workspace files. This archive is therefore personal and should be stored or shared accordingly. Git is initialized locally with discrete commits. No remote URL is configured and nothing is pushed to a remote repository.
