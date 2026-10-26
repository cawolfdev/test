# wildlife-bodybuilder implementation plan

1. **Authority:** Construct or source a legally usable complete rigged human mesh, fit identity and skeletal landmarks against the real photographs, retain extreme anatomical hypertrophy with fixed joint topology.
2. **Calibration:** Regenerate genuinely independent 0° and 60° photographs from the *same 3D identity and pose*; compare projected masks, landmarks and occlusion, reject unstable or multi-panel image responses.
3. **Orbit:** Freeze pose and model; render one 1080 × 1920 geometry/depth/mask reference every 15° from 0° to 120°. Track newly exposed surfaces across steps.
4. **Photorealism:** Apply each exact 3D checkpoint as control/reference to one photographic synthesis job. Do not accept montage, cropping, resampling, unclear provenance, head turns or broken arm/neck topology.
5. **Verification:** Store exact native images with geometry alignment metrics and digest; save rejected image bytes, prompts/reasons and visibility diagnostics.
6. **Publication:** Update existing overview and reports/current.json, keep historical revisions in Git commits, and push all source, geometry and evidence onto wildlife-bodybuilder-portrait. Verify remote tree matches tracked local blobs before calling it synchronized.

**Current blockers:** Real rigged fitted mesh unavailable; independent photo provider keeps returning montage; GitHub connector cannot directly access local filesystem bytes and cannot yet transfer all images. Keep remote sync status explicitly PARTIAL.
