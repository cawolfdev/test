# Repository filesystem usage: wildlife-bodybuilder

**Current best outputs:** Start in [`output/`](output/README.md). Geometry is *independently rendered* and is **not photographic**. Accepted photographic views are not yet available.

| Path | Purpose |
|---|---|
| `output/` | Current 3D renders, camera checkpoints, registration images and state; replaces former `outputs/` |
| `assets/` | Original approximate photographic references and one reusable fixed-pose mesh |
| `evidence/rejected/montage/` | Original multi-view images rejected for not being standalone frames |
| `evidence/rejected/viewpoint/` | Original single images with a wrong/unchecked angle or head pose |
| `evidence/rejected/unverified/` | Other photographic explorations without a matching geometric proof |
| `evidence/rejected.json` | One registry of all rejected images, hashes, and reasons |
| `evidence/visibility/` | Nine independent full-size camera-occlusion diagnostic views |
| `src/orbit/` | Reusable domain geometry, rendering, image acceptance, I/O and validation |
| `tools/` | Interoperability including byte-identical GitHub Git blob bridge |
| `tests/` | Geometry, byte provenance, evidence and organizational tests |
| `docs/` | Current architecture, decisions, overview and plan |
| `reports/current.json` | One current machine-readable report; older states live in Git history |

## Running

`python -m pytest -q` validates invariants without comparing exact pixels.

`python cli.py --through 120` resumes the fixed 3D view sequence and saves outputs in `output/orbit_000_120/`.

All execution and generation outputs intended as project artifacts must be committed. **Commit, immediately push and verify before proceeding to another commit.** A failed push is a blocker, not a successful checkpoint.

## Image acceptance

Native independent single-frame PNG with width **>1000** and height **>1000**; no panel extraction, crops or artificial enlargement. Additionally, photographic checkpoints need fixed-pose geometric alignment. A 1024×1536 image can pass resolution yet fail the geometry gate. Do not present geometric diagnostic images as photographs.
