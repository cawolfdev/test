"""Camera coordinates with an immutable, forward-facing subject."""
from dataclasses import dataclass
from math import radians, sin, cos

FRONT = (0.0, 1.0, 0.0)

@dataclass(frozen=True)
class Orbit:
    angle: int
    radius: float = 5.0
    camera_height: float = 1.5
    def __post_init__(self):
        if not 0 <= self.angle <= 180:
            raise ValueError('Expected azimuth between 0 and 180 degrees')
        if self.radius <= 0:
            raise ValueError('Camera radius must be positive')
    @property
    def position(self):
        theta = radians(self.angle)
        return (self.radius*sin(theta), self.radius*cos(theta), self.camera_height)
    @property
    def subject_facing(self):
        return FRONT
    @property
    def azimuth_for_mpl(self):
        # Matplotlib azimuth zero looks along +x and 90 along +y.
        return 90 - self.angle

