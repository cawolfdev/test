# wildlife-bodybuilder: project overview | v0002

## Mission and acceptance

Reconstruct the *same* adult subject in one stationary anatomically connected hands-behind-head pose, then produce nine individually generated, **native full-HD portrait photos**, 0° to 120° at 15° intervals. The camera moves; face, head, limbs and muscular anatomy never turn to follow it. Personal likeness, amber eyes, short-sided textured forward-spiked hair and dense naturally feathered stubble come from the original references and user brief.

The observable outcome takes precedence over polished but inconsistent samples. **Currently 0/9 independent full-HD photographs have passed acceptance.**

## Achieved and measured

- Nine native 1080×1920 3D *geometry diagnostics* persist with digests, 15° orbit states, and depth-checked surface visibility samples.
- Both available photographic source views have estimated subject masks and independent geometry overlays; neither passes the provisional 0.82 silhouette IoU threshold.
- 0° source-versus-proxy mask IoU **0.715**, 60° **0.760** (estimated, unreviewed masks; compare `reports/current.json` for exact values).
- The old mesh is non-watertight with incomplete lower legs, rough facial geometry and nonmatching pose. It remains a **test fixture**, not a fitted person.
- All available historical generation outputs that are not the two accepted source references are retained unchanged as **10 unaccepted checkpoint attempts**, including montage and wrong-head-turn examples.
- All nine visibility diagnostic images and both registration comparisons/masks are archived in the repository and standalone evidence zip.
- A repeatable camera-only fitting metric now exposes geometric mismatch prior to using expensive image generation. This does not itself correct anatomy.

## What is failing and why

The current proxy does not encode the specific identity, skeleton and full-body structure. Even the best camera-only fitting cannot make the incomplete shape match both source views. Generating pretty photos directly simply invents the missing parts inconsistently.

## Next significant decision

Secure or construct a geometrically coherent, rigged whole-body mesh with correct head and hands-behind-head articulations, then re-fit against the two estimated silhouettes with manual mask/landmark review. **Only** after both views pass geometric validation should the 15° independent native photographic generation resume.

## Project structure

- `src/orbit/`: reusable I/O, camera/rendering, mask extraction, alignment, mesh audit, evidence and release modules.
- `output/orbit_000_120/`: native-resolution fixed-mesh camera checkpoints and visibility masks.
- `output/registration/`: source masks, overlaid failures and per-view numerical fit results.
- `evidence/rejected/`: historical unaccepted generation **original bytes**, with `evidence/rejected.json` reasons and hashes.
- `evidence/visibility/`: **all nine** 1080×1920 visibility diagnostics plus manifest.
- `evidence/progress/`: preview copied to chat for monitoring; a display-only composite, **not** an image-generation checkpoint.
- `reports/`: machine-readable *in-repository* current and versioned reports.
- `docs/PLAN.md`, `docs/ARCHITECTURE.md`, `docs/FILE_MAP.md`, `docs/PROGRESS.md`: goals, design, functionality, and change log.
- `tests/`: regression tests; runnable via `python -m pytest -q`.

## Release and evidence policy

All external files start `wildlife-bodybuilder-` and end with sortable `-vNNNN` before their extension. The `project` zip contains overview, report, sources, original reference assets, evidence, tests, Git history and 3D checkpoints. The `evidence` zip separately contains every available rejected generation and every diagnostic; the `checkpoints` zip contains camera geometry and visibility state. Keep incomplete work labeled incomplete.

## GitHub publication and source validity (current)
The destination is `cawolfdev/test` branch `wildlife-bodybuilder-portrait`. Git history is the version record; update existing overview and report documents instead of emitting duplicate version-suffixed copies into the repository. Original 0° and 60° photographic source images are only approximate and must be replaced by independent full-frame, native-resolution generated photographs that are registered to a fixed 3D model. Four new montage attempts were rejected and preserved under `evidence/attempts`. Publication success requires remote tree checks, including hashes for binaries.

## Single-current-report policy
Only `reports/current.json` is checked into the working tree. Older reports remain available via Git history. Source candidates need independent native 1080×1920 photography, one image per generation. As of the latest audit, four newly generated montages have failed the gate; 0°/60° replacements are still outstanding.

## Current synchronization and generation update

The old claim that GitHub cannot transfer binary blobs was incorrect. Binary bytes are encoded as base64 and uploaded via the Git Data blob API, then compared by Git object SHA. The repository now tracks native geometric outputs and registration records. Photo candidates 015 and 016 are independent 1024×1536 images, but fail native full-HD requirement; 016 also fails the required 60-degree pose. Their original bytes remain in the failed-evidence registry.

## Connector transfer status

Using the supported GitHub Git Data blob API, base64-encoded file bytes were uploaded and validated by exact Git SHA. Three paths have no remotely accepted blobs: `assets/geometry/fixed_pose_proxy.glb` (transport-size failure), `evidence/rejected/attempt_009.png`, and `output/orbit_000_120/075/visibility.npz` (safety checks). No proxy or substituted bytes may be used to claim a complete mirror. New 60° attempts also failed orientation; three independent 1024×1536 images are preserved in the rejected evidence, none accepted as native 1080×1920.

## v0004 measured release

The remote GitHub branch was inspected and compared to the local SHA-1 Git blob hashes: **94/98 tracked paths match exactly**, with no mismatches or extra files. The four absent blobs are the prior three paths plus `evidence/rejected/attempt_017.png`, blocked during connector upload. Local ZIP retains all files and full Git history; remote history and files are incomplete. Two new standalone 0-degree-like photographs and another 0-degree result (17 total attempts) are retained without approval; all are native 1024×1536 below project 1080×1920 native photo gate and none constitutes a fixed 60-degree viewpoint.
