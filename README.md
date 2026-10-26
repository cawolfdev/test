# wildlife-bodybuilder

Create **nine independent photographic views** at 0°, 15°, 30°, 45°, 60°, 75°, 90°, 105° and 120° around **one stationary subject**. The input portrait is a **character and pose reference**, not the generated 0° frame. New image-generation results require visual review before advancing. HD means **both dimensions strictly exceed 1000 pixels**. The proxy model is an anatomical approximation, not a fitted human scan; its geometry guides do not count as photos.

## Root directory: file paths and ownership

| Path | Meaning |
| --- | --- |
| `reference/character.png` | **Single canonical character/pose reference**. Never counted as a generated angle. |
| `model/subject.glb` | Reusable **coarse** 3D anatomical proxy shared by all viewpoints. |
| `output/frames/000.png` ... `120.png` | **Only accepted** independently generated photos, one for each 15° checkpoint. `000.png` is generated, not copied from the reference. |
| `output/guides/000.png` ... `120.png` | Reusable reused native 1920×1755 3D camera guides. Distinct from photos. |
| `output/state.json` | **Only current run**: schedule, accepted frames, SHA provenance, current rejection and next angle. No per-run archives. |
| `generatedat.txt` | UTC ISO-8601 timestamp when the current run was initialized. |
| `src/wolf_orbit/` | Reusable core geometry, storage, rendering, and orbit workflow. |
| `tools/production.py` | Thin CLI adapter, no duplicated core logic. |
| `tests/` | Behavioral/unit tests. No concrete image comparisons, pixel-equality or source immutability assertions. |
| `docs/architecture.md` | Architecture, quality gates, and outstanding fidelity limitations. |

Everything under `output/` belongs to the latest run. Use `prepare --reset` to discard it and initialize a new run. **Git commits retain history**. No versioned run directories, duplicated references, atlas crops or per-attempt files.

## Process

```bash
PYTHONPATH=src python tools/production.py prepare
PYTHONPATH=src python tools/production.py guides
PYTHONPATH=src python tools/production.py next
# After independently generating and visually reviewing the requested 0° image:
PYTHONPATH=src python tools/production.py accept --angle 0 --image /path/to/generated-photo.png --reviewed
PYTHONPATH=src python tools/production.py next  # now requests 15°
PYTHONPATH=src python -m unittest discover -s tests -v
```

For rejected images, use `reject --angle N --reason "..."`. This records only the current failure explanation in `output/state.json`. Never advance from unreviewed frames, or mistake a 3D geometric guide for a photo. Always commit the current project state and **binary outputs**, and sync the branch `wildlife_anthrowolf` on `cawolfdev/test` after an accepted step. The project does not silently discard large assets.
