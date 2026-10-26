"""Single shared coarse subject model used for geometric camera guidance."""

# Ellipsoid centers/axes in model-space metres (approximate, not calibrated).
# Subject faces +Y and never changes pose when the camera moves.
PARTS = (
    ((0, 0, 1.14), (.72, .45, .82), 'torso'),
    ((-.38, -.32, 1.46), (.42, .25, .54), 'back'),
    ((+.38, -.32, 1.46), (.42, .25, .54), 'back'),
    ((-.37, +.34, 1.52), (.43, .27, .39), 'chest'),
    ((+.37, +.34, 1.52), (.43, .27, .39), 'chest'),
    ((-.82, 0, 1.63), (.42, .42, .43), 'shoulder'),
    ((+.82, 0, 1.63), (.42, .42, .43), 'shoulder'),
    ((-1.01, 0, .97), (.29, .31, .50), 'arm'),
    ((+1.01, 0, .97), (.29, .31, .50), 'arm'),
    ((-.40, -.10, 1.92), (.30, .33, .25), 'back'),
    ((+.40, -.10, 1.92), (.30, .33, .25), 'back'),
    ((0, 0, 1.95), (.29, .32, .48), 'neck'),
    ((0, +.03, 2.43), (.32, .31, .34), 'head'),
    ((0, .345, 2.41), (.105, .115, .095), 'head'),
    ((-.335, .015, 2.42), (.075, .105, .135), 'head'),
    ((+.335, .015, 2.42), (.075, .105, .135), 'head'),
)

MATERIAL = {
    'torso': '#85959f', 'back': '#687987', 'chest': '#a7b5bd',
    'shoulder': '#879ba8', 'arm': '#798e9d', 'neck': '#a5a5a1',
    'head': '#b7a491',
}


def scene_parts():
    return PARTS
