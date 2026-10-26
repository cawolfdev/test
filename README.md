# Wolf camera orbit workspace

The **images/** directory contains 9 standalone angle PNG files. 000 and 060 are the exact preceding source anchors. 015, 030, 045, 075, 090, 105, 120 are single-view crops extracted from an AI-generated angle atlas.

The **mocks/** directory records the correct camera coordinate system at 15° increments. **references/** stores the anchor images, prior generated candidate frames, four user-supplied selfie references, and a rejected earlier atlas. **notes/** stores the orbit specification and extraction script. **manifest.json** lists file hashes for reproducibility.

## Important limitations
This is *not* an exact 3D camera orbit. The camera angles are illustrative rather than calibrated, and the identity and muscular proportions may drift between views. Some intermediate crops are lower resolution than the anchor images. The source camera cannot be recovered exactly from 2D photographs. A true locked-pose 120° orbit needs a consistent 3D model and matched camera rig.
