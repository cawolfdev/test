# wildlife-bodybuilder v0002 progress and source-of-truth gap

Canonical newly uploaded 0-degree source: 1312x1199 pixels, SHA-256 cf3eec368ccccde1ddd1063a1d4d81a054c7776493eed0e48526b5bce2c1a371. Original source is preserved at runs/v0002/source.png locally. It is not equal to the previous atlas anchor.

Target: 0 to 120 degrees at 15-degree increments, nine native full-resolution independent photographic views. Native generated frames must have dimensions at least 1920x1080; the user-provided 0-degree image is preserved unchanged at native resolution.

Local progress: nine independent 1920x1755 raycast guides from one fixed model, 22 passing tests, two new local commits d81879c and a5327b9. Photo evidence: source only (0 degrees). A failed 15-degree model generation was rejected and retained (1312x1199, wrong azimuth) rather than allowed to contaminate 30 degrees.

The only available geometry is a 16-ellipsoid proxy, not a fitted photorealistic head/body scan. Therefore the geometric guides prove only angle-coordinate consistency, not photographic fidelity. Human identity selfie photographs must not be sent to this public repository without an explicit privacy decision.

Outstanding sync: GitHub connector supports create_blob/tree/commit/ref, but not uploading a local Git bundle or direct git push, and local git network DNS is unavailable. Hence the exact original Git commit hashes and binary project history have NOT been pushed. The local portable bundle retains the true original full commit graph. This file is a status synchronization, not proof that the binary files or full history are on GitHub.
