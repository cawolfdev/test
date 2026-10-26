# Architecture and engineering priorities

- **Generic plumbing:** `assets.py` for filesystem/image I/O and hashing; `geometry.py`, `surface.py`, `proxy.py`, `render.py` for fixed-pose camera and geometric guide generation. One anatomical proxy specification, one raycaster, one guide renderer.
- **Domain policy:** `hd_orbit.py` has only schedule, next-stage request and acceptance rules. No I/O or image generation code.
- **Process composition:** `orbit_pipeline.py` owns the single `output/state.json`, prepares/checks inputs, invokes lower-level functions, and accepts/rejects externally generated photographic views.
- **Thin entry point:** `tools/production.py` translates CLI arguments to the domain service.
- **Quality:** tests cover scheduling, interface behavior, sequential approval and HD dimensional requirements. They do **not** test pixels, assert reference-file immutability, or hard-code expected photographic outputs.
- **Geometry limitation:** Existing `model/subject.glb` is a rough ellipsoid proxy; it is **not** a registered 3D likeness. Guides at exact camera coordinates cannot guarantee that an independent image-generation result matches that angle or reveals the correct back anatomy.
- **Human visual review:** each photo must maintain identity, pose, orientation, costume, fur, chest, neck and background. Reject if those drift, even if dimensions and other structural checks pass.
- **State and Git:** only one active `output/` directory; do not duplicate binaries for audit. Use committed versions and Git history for lineage. Sync all project artifacts, including binaries, to the remote branch. No duplicate release archives in Git.
