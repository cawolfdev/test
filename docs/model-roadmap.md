# Model fidelity: defects and evidence-based revisions

v0 proxy has independently intersected ellipsoids with coarse anatomy. It can validate angle convention and occlusion but not face identity, neck skin/fur continuity, major muscle attachments, pose fidelity, or plausible photography. A UV reprojection experiment demonstrated duplication/ghosting and is not an acceptable photorealistic renderer.

Next anatomical iteration should use a licensed existing human mesh with topology, pose/shape parameters, UV unwrap, and camera registration to the 0° photograph; retain a fixed world-space subject pose. Fit silhouette/landmarks at 0°, validate side silhouette at 60°, then re-render all views. Only then project observed material and synthesize truly unseen surfaces. Never accept the superficial success of a photo prompt as proof of calibrated camera geometry.

Each model revision: record parent model hash, defect addressed, fitted 0° silhouette measurement, independent side validation, impact on all 15° views, and whether any previously accepted photo frame is invalidated. No mid-run mutation.
