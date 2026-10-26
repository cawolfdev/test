# wildlife-bodybuilder

**Start here: [FILESYSTEM.md](FILESYSTEM.md) and [current geometric outputs](output/README.md).**

Geometrically consistent 0°–120° camera orbit, with 15° fixed-mesh checkpoints.

**Current state:** Nine independent, native 1080 × 1920 *3D diagnostic renders* are verified. The 3D model is still an anatomical approximation. There are **zero geometrically accepted photographic generations**. The saved frontal/60° photographic images are references only, not generated checkpoint outputs.

## Reproducible workflow

```bash
python -m pytest -q
python cli.py --through 120
python build_release.py --version v0001
```

Source code is split into abstract I/O (`core.py`), domain camera and visibility calculations (`domain.py`, `visibility.py`), rendering adapter (`render.py`), resumable checkpoints (`checkpoints.py`), audit (`audit.py`), orchestration (`pipeline.py`), and versioned releases (`release.py`).

### Deliverable names

All external deliverables use one stable stem, e.g.

- `wildlife-bodybuilder-project-v0001.zip`
- `wildlife-bodybuilder-checkpoints-v0001.zip`
- `wildlife-bodybuilder-overview-v0001.md`
- `wildlife-bodybuilder-report-v0001.json`
- `wildlife-bodybuilder-preview-v0001.png`
- `wildlife-bodybuilder-visibility-v0001.png`
- `wildlife-bodybuilder-manifest-v0001.json`

Increment the zero-padded version (`v0001` → `v0002`) for subsequent published updates. Do not invent new stems for the same deliverable roles. Each packaged project contains portable relative paths, source, Git history, model, inputs, masks, renders, documentation and tests.

**Do not confuse native geometry outputs with photographs.** The existing rough mesh, including face and leg geometry, must be fitted to the subject before an accurate photo sequence is possible. No composite/cropped/upscaled image qualifies as an independently generated HD frame.

See `docs/ARCHITECTURE.md`, `docs/FILE_MAP.md`, and `docs/PROGRESS.md` for architecture, function responsibilities, latest progress, and known blockers.

## Current working iteration

**Read `docs/OVERVIEW.md` and `docs/PLAN.md` first.** The numeric state of every model/registration/evidence check is in `reports/current.json` . Camera-only registration shows the proxy does not match the frontal and 60° photographic sources; photo synthesis remains blocked.

```bash
python analyze_references.py   # produces failures as measurable images and metrics
python collect_evidence.py     # legacy import only; keeps unaccepted source bytes
python -m pytest -q
python build_release.py --version v0003
```

The current versioned evidence archive carries **every available unaccepted historical generation**, all nine high-definition visibility diagnostics, two silhouette-mask failures and the chat progress preview. They are also kept in the full repository zip. No failed image is silently substituted for a successful independent photo.

## GitHub target and synchronization status

Target: [cawolfdev/test, wildlife-bodybuilder-portrait](https://github.com/cawolfdev/test/tree/wildlife-bodybuilder-portrait). The GitHub connector created the branch and published commit `17b7684b5d3cff577463b28925c674c80024236f`, containing updated project overview, plan, current report and README. **The remote repository is not yet a complete mirror:** the connector can transfer binary bytes through base64 Git objects, but several specific blob uploads were blocked. The source-of-truth full project and Git history are retained in this downloaded project release. The four newly generated montage attempts were rejected and added to `evidence/rejected/`; neither new 0° nor 60° true native photographic reference is accepted. A mirror is only considered complete when all tracked file digests are verified against remote Git blobs.

Use Git history for older versions of mutable documentation; keep `docs/OVERVIEW.md`, `docs/PLAN.md`, `reports/current.json` as the single current copies in each commit. Version suffixes are for **external downloaded release artifacts** only.

## Exact GitHub binary synchronization

Binary and text files are Git blobs. The transfer bridge (`tools/git_bridge.py`) packages tracked bytes into SHA-verified base64 transfer batches; the connected GitHub Git Data API creates blobs, trees, commits, and a branch update. The transfer is not complete until the remote tree matches the tracked local files. Outputs/ is now tracked, including the full-HD geometry, visibility state and registration diagnostics. Historical failed generations are retained in `evidence/rejected/`. Both new standalone photographs (attempt_015 and attempt_016) are rejected, not geometry-verified native full-HD references.
