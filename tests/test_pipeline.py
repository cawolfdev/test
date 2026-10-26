"""Behavior tests only; never assert concrete image pixels or unchanged sources."""
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from wolf_orbit.hd_orbit import OrbitSpec, angles, camera_request, validate_candidate
from wolf_orbit.orbit_pipeline import prepare, next_request, accept, reject, status


class OrbitTests(unittest.TestCase):
    def test_schedule_and_hd_bounds(self):
        spec = OrbitSpec()
        self.assertEqual(angles(spec), tuple(range(0, 121, 15)))
        with self.assertRaises(ValueError):
            angles(OrbitSpec(target=119))
        with self.assertRaises(ValueError):
            validate_candidate(spec, [], 0, (1000, 1200), 'independent_generation', True)
        validate_candidate(spec, [], 0, (1001, 1001), 'independent_generation', True)

    def test_zero_must_be_generated(self):
        request = camera_request(OrbitSpec(), [])
        self.assertEqual(request['angle'], 0)
        self.assertIsNone(request['previous_frame'])
        self.assertNotEqual(request['reference'], 'output/frames/000.png')
        with self.assertRaises(ValueError):
            validate_candidate(OrbitSpec(), [], 0, (1200,1200), 'anchor', True)

    def test_order_and_review(self):
        spec = OrbitSpec()
        record = [{'angle': 0, 'review': 'accepted'}]
        self.assertEqual(camera_request(spec, record)['angle'], 15)
        with self.assertRaises(ValueError):
            validate_candidate(spec, record, 30, (1200,1200), 'independent_generation', True)
        with self.assertRaises(ValueError):
            validate_candidate(spec, record, 15, (1200,1200), 'independent_generation', False)

    def test_single_run_state_and_stage(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'reference').mkdir()
            (root/'model').mkdir()
            Image.new('RGB',(1312,1199)).save(root/'reference'/'character.png')
            (root/'model'/'subject.glb').write_bytes(b'coarse 3D model')
            prepare(root)
            self.assertEqual(next_request(root)['angle'], 0)
            self.assertTrue((root/'generatedat.txt').exists())
            self.assertEqual(list(root.glob('output/**/state.json')), [root/'output'/'state.json'])
            reject(root, 0, 'Needs accurate silhouette')
            self.assertEqual(status(root)['next']['angle'], 0)
            image = root/'candidate.png'
            Image.new('RGB', (1200, 1100)).save(image)
            accept(root, 0, image, reviewed=True)
            self.assertEqual(next_request(root)['angle'], 15)
            self.assertEqual(len(status(root)['accepted_angles']), 1)


if __name__ == '__main__':
    unittest.main()
