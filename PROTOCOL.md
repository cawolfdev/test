# Production protocol and acceptance gates

The prior three eight-figure charts were **invalid outputs**. This project does not import, crop, or reuse those composites as source characters. They are *not* a completed production step.

For each `image_attribute_level`, strictly sequentially:

1. **Prepare:** Show entire self-contained prompt, create a request manifest with exact model, API parameters, input prompt SHA-256, anticipated output filename, and a per-character attempt number. Commit before the request.
2. **Submit:** No multi-image requests (`n=1`); no batches, no previous image attachments, no image-to-image, no hidden context. Log the submission and commit it before making an API request.
3. **Capture:** Save new PNG intact, verify PNG structure and store SHA-256 and request ID/model. Commit the artifact and metadata before doing anything else. If generation fails, record the failure and stop.
4. **Review:** Inspect figure count, complete head-to-toe framing, attribute isolation, M=1 extreme baseline, anatomical coherence, visually consistent identity, background and textures. Commit approval or rejection. No automatic level advancement on failure or before approval.
5. **Advance:** Only after approval may the next individual be prepared. The next prompt does not read the previous image or previous prompt, and it never relies on previous generation context.
6. **Composite:** Only after all eight for an attribute are separately generated and approved may a full-sheet composite be assembled. Tile scaling is allowed only in the derived composite and does not mutate source images. No composite before the eight inputs exist.

Independent calls provide procedural independence, **not guaranteed** perfect numerical muscular-volume scaling or identical facial identity. Reviewers must inspect visual consistency and re-run rejected steps with recorded attempts. No model can objectively validate fictional hormone or conceptual masculinity multipliers.

GitHub state is acknowledged only after authenticated remote create/push; local commits and zip/bundle are distinct from GitHub persistence. No personal tokens are printed, committed or transmitted by the scripts except in the authenticated HTTP header to the official API endpoint.

**GitHub destination:** cawolfdev/test, dedicated branch `charflow/independent-images`. Per-commit remote replication must be confirmed; `CHARFLOW_PUSH=1` enforces fail-closed pushing when authenticated Git access is available.
