# Visual QC and failure boundaries

## What is verified
- The 9 output filenames follow the exact 0° to 120° inclusive 15° sequence.
- The front and 60° image anchors remain pixel-identical to their original source files.
- The mock geometry never rotates the head, neck, torso or any constituent part. The camera alone moves in an overhead clockwise orbit. All geometry angles reuse one immutable part specification.
- At 120° in the raycast proxy, visible pectoral pixels drop by >10x compared with 0° and visible back-muscle pixels increase >30x.
- Atlas crop rectangles are stored as data in `atlas_layout.json` and small boundary artifacts were trimmed.

## What is not verified, and cannot be inferred from the available 2D references
- True azimuth correspondence of the AI-generated atlas frames.
- Actual 3D surface registration, constant posture and pose, camera focal length and camera extrinsics.
- Consistent facial identity, hair distribution, muscular volume and coat markings across synthesized views.
- High-resolution detail in atlas crops (~249x417 through 325x471 pixels).

## Next technically valid step to solve the remaining issue
Reconstruct or manually model one coherent body/head mesh and material texture; align the virtual 0° camera to the source frontal photo and the 60° camera to the earlier second anchor, and render orthographic/telephoto views every 15° from a truly shared pose. The camera-calibration parameters cannot be uniquely recovered from just two separate generative 2D photos.
