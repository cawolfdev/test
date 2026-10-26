from pathlib import Path
import unittest
from wolf_orbit.geometry import Orbit, ANGLES
from wolf_orbit.validation import validate
from wolf_orbit.assets import pixel_equal
from wolf_orbit.proxy import scene_parts, raycast_proxy

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
    def test_occlusion_changes_with_camera_not_pose(self):
        initial=scene_parts()
        _,front=raycast_proxy(0,resolution=(120,140))
        _,rear=raycast_proxy(120,resolution=(120,140))
        # 120 degrees must expose much more back and almost no pectoral surface.
        front_chest=int(((front==3)|(front==4)).sum())
        rear_chest=int(((rear==3)|(rear==4)).sum())
        front_back=int(((front==1)|(front==2)).sum())
        rear_back=int(((rear==1)|(rear==2)).sum())
        self.assertGreater(front_chest, 10*rear_chest)
        self.assertGreater(rear_back, 30*max(1,front_back))
        self.assertEqual(initial,scene_parts())
    def test_deliverable(self):
        self.assertTrue(validate(ROOT)['passed'])
if __name__=='__main__':unittest.main()
