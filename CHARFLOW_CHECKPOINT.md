# Character pipeline audit checkpoint

This branch is a **text-only remote audit record** for the independent-image pipeline. It is NOT the original local Git history and does not contain the 24 prompts, binary source PNGs, or the rejected image evidence. The authentic Git history is retained in the local repository and incremental delivery bundles. Do not merge this branch into `main` in place of the original image pipeline.

- Repository: `cawolfdev/test`
- Authentic local history target branch: `charflow/independent-images` (not yet published)
- Local previous checkpoint: `abd9a02`
- Local current commit at this remote audit: `289dde1`
- Independently generated and approved images: `image_1_1.png`, `image_1_2.png`, `image_1_3.png`
- Current state: **3 approved / 24 requested**
- Next source image: `image_1_4.png` (M4), **not approved**
- Previous M4 attempts remain separate immutable rejected PNGs in the local project.
- User-approved source images 1.1 and 1.2 and their original prompts are unchanged.
- Numeric M4 target: 20 cm face width, 260 cm shoulder span, 200 cm height.
- Synthetic geometry-only proxy requires a padded aspect ratio of at least ~1.39, so 2:3 portrait is not sufficient.
- A local heuristic mask-based visual screen reports M3 upper width ~7.30 face widths vs last rejected M4 ~6.43 face widths. These are heuristic image measurements, not physical anatomy or proof of exact volume.
- Local regression suite: **13 passing tests**.
- No full remote synchronization of PNGs or local commit objects has occurred.

## Continue locally

In the original local project directory, with local Git objects present:

```bash
python -m unittest discover -s tests -v
python render_geometry_reference.py --spec specs/image_1_4_geometry.json --svg specs/image_1_4_geometry_proxy.svg --report specs/m4_canvas_plan.json
python silhouette_audit.py --reference images/image_1_3.png --candidate /path/to/new_M4_candidate.png
python export_incremental.py --base abd9a02 --output /path/to/new/delta
```

Use only the local `charflow/independent-images` history for canonical commits. This audit branch has independent commit IDs and must not be treated as a fast-forward replacement for the original local history.
