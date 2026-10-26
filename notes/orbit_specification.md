# Fixed-pose wolf-human bodybuilder camera orbit

Reference coordinates: the original near-frontal image is **0 degrees**, and the previously generated oblique image is the **60-degree visual anchor**. These are photographic generation references, not calibrated 3D renders. The source 60-degree image may exhibit less rotation than its label implies.

Angles: 0, 15, 30, 45, 60, 75, 90, 105, 120 degrees, measured clockwise in plan as the **camera moves around the stationary subject**. This is azimuthal orbit, not image-plane rotation or head/neck turn. Camera elevation, distance, focal length, subject pose, anterior torso heading, head-to-torso alignment, and scale must be fixed.

At 0, face and both pectorals visible. At 60, most of near-side shoulder and pectoral plus far-side partial pectoral visible. At 90, genuine lateral profile: no frontal-looking face, one pectoral largely occludes the other, side of nose/ear, deep torso silhouette. At 105, primarily back of the head and neck with small side-of-face visible if physically possible. At 120, rear three-quarter: facial features mostly or fully occluded by head anatomy, back musculature, shoulder and trapezius dominate. Body and eyes point forward in world coordinates throughout.

Source materials: see references/00_front_reference.png and references/60_intermediate_reference.png. Front and 60 are copied originals and are *not* recomputed frames.

Generated files are approximations because an image generation model does not have a source 3D mesh or camera calibration. Strict pose preservation and exact 15-degree increments are targets, not physically verified.
