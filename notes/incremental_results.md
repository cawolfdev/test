# Incremental 3D Surface-Reconstruction Experiment

## Verified execution (2026-10-25)

Reused the pre-existing Git workspace, prior 0°/60° photographs, previously cropped 15-degree photo atlas and fixed-pose 3D ellipsoid raycaster. No photograph was synthesized unnecessarily.

- Exported **one static 3D anatomical proxy** as `model/fixed_human_faced_bodybuilder_proxy.glb`.
- Applied color samples from the existing 0° photograph onto the geometrically visible UV texels.
- For each successive 15° camera rotation, raycast the **same 3D geometry**, inherited the material state from the previous checkpoint, and populated only previously unobserved UV texels using the pre-existing view candidate for that angle.
- Wrote **nine** checkpoint texture states (`sequential/checkpoints/*.npz`) and metadata files; each metadata file records the SHA-256 of its exact predecessor state.
- Wrote independent 3D geometry, novel surface, and photo-projected preview images at every angle.
- Reused stored state on repeated execution rather than recalculating unchanged checkpoints.

| Camera | Newly observed texture cells | Cumulative observed | Checkpoint SHA-256 prefix |
|---|---:|---:|---|
| 000° | 177,750 | 177,750 | 6409637d2414 |
| 015° | 40,410 | 218,160 | 86f434250cc9 |
| 030° | 24,733 | 242,893 | 8a0486dba609 |
| 045° | 15,583 | 258,476 | 6d9742d0bc95 |
| 060° | 14,004 | 272,480 | c88cfb7eb732 |
| 075° | 16,791 | 289,271 | 76c18323ff74 |
| 090° | 22,075 | 311,346 | 4f6f152c2301 |
| 105° | 36,874 | 348,220 | a2c84e3e4612 |
| 120° | 39,404 | 387,624 | 1c98ca550c69 |

## Visual inspection and accuracy assessment

**Camera/pose geometry**: Verified. Numerically fixed camera azimuths from 0° to 120° clockwise. All anatomically labeled proxy parts remain at identical world-space positions and dimensions, with no per-step torso/head rotation. At 120°, front chest parts become occluded and rear muscles visible.

**Incremental geometry and state**: Verified. All 15° increments load predecessor material state and paint previously unseen UV locations. Tests verify the checkpoint hash chain and monotonic texture coverage.

**Photographic fidelity**: **FAILED**. Visual inspection of `sequential/previews/renders_15deg_sequence.jpg` shows ghosted or repeated facial features, stretched/duplicated textures, and contamination with photographic background. Reasons: the existing primitive proxy does **not** match the specific character's true 3D anatomy, and the prior AI-generated 2D photos are **not calibrated images of one measured subject**. Reprojecting these photos onto an approximate 3D surface cannot fix their geometry and identity inconsistencies.

**True 3D human-body mesh**: **NOT AVAILABLE**. The pre-existing workspace contains a raycast ellipsoid proxy, not an existing rigged/posed human scan. We reused and exported this proxy instead of falsely asserting a mesh existed. It is genuine 3D geometry but only a coarse approximation; the `.glb` is not a reconstructed human model.

**120° photographic candidate**: `images/120_clockwise.png` is reused from the earlier atlas. It is visually plausible but **not geometrically verified** and **not produced by the new sequential 3D pipeline**.

**120° geometry-locked output**: `sequential/geometry/120.png` is a genuine raycast of the immutable proxy. **120° projected texture output**: `sequential/renders/120.png` comes from the cumulative texture state, but has obvious image artifacts and must not be passed off as a photorealistic final.

## Reuse-first commands

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
python tools/run_sequential.py
PYTHONPATH=src python -m wolf_orbit.cli archive --root .
```

## Next technical prerequisite for an accurate photograph

Obtain and fit a detailed existing human head-and-body mesh (or independently reconstruct one) to the original 0° image, fix a single UV material and rig, and obtain surface-consistent reference views. Real multi-view photos and calibrated lenses would materially improve the ability to recover occluded geometry. Until then, no exact 120° photorealistic reconstruction can be certified from the available 2D imagery.
