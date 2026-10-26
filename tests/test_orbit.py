from pathlib import Path
import unittest
from wolf_orbit.geometry import Orbit, ANGLES
from wolf_orbit.validation import validate
from wolf_orbit.assets import pixel_equal

ROOT=Path(__file__).resolve().parents[1]
class CameraTests(unittest.TestCase):
    def test_uniform_angles(self):
        self.assertEqual(ANGLES,tuple(range(0,121,15)))
    def test_pose_stays_world_fixed(self):
        self.assertEqual({o.subject_facing for o in [Orbit(a) for a in ANGLES]}, {(0.,1.,0.)})
    def test_clockwise_right_hand_camera(self):
        self.assertAlmostEqual(Orbit(0).position[0],0,places=5)
        self.assertAlmostEqual(Orbit(90).position[1],0,places=5)
        self.assertGreater(Orbit(90).position[0],0)
        self.assertLess(Orbit(120).position[1],0)
    def test_source_reuse(self):
        for a,src in [(0,'00_front_reference.png'),(60,'60_intermediate_reference.png')]:
            self.assertTrue(pixel_equal(ROOT/'images'/f'{a:03d}_clockwise.png', ROOT/'references'/src))
    def test_deliverable(self):
        self.assertTrue(validate(ROOT)['passed'])
if __name__=='__main__':unittest.main()
