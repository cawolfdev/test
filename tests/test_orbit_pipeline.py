"""Regression checks for immutable source, resumable domain orchestration and HD intent."""
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from wolf_orbit.orbit_pipeline import RunSpec, prepare, progress, next_request
from wolf_orbit.assets import sha256


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.source = self.project / 'source_input.png'
        self.model = self.project / 'model_input.glb'
        Image.new('RGB', (1312,1199), (22,31,44)).save(self.source)
        self.model.write_bytes(b'fixed proxy model')
        self.spec = RunSpec()

    def test_prepare_only_registers_original(self):
        plan = prepare(self.project, self.source, self.model, self.spec)
        self.assertEqual(plan['angles'], tuple(range(0,121,15)))
        st = progress(self.project,self.spec)
        self.assertEqual(st['registered'], (0,))
        self.assertEqual(st['next_angle'],15)
        self.assertFalse(st['complete'])
        self.assertEqual(sha256(self.source),sha256(self.project/'runs'/'v0002'/'hd'/'frames'/'000.png'))
        req = next_request(self.project,self.spec)
        self.assertEqual(req['native_min_width'],1920)
        self.assertEqual(req['native_min_height'],1080)
        self.assertEqual(req['angle'],15)

    def test_native_full_hd_is_enforced_on_generated_angles(self):
        from wolf_orbit.hd_orbit import register_frame
        prepare(self.project, self.source, self.model, self.spec)
        with self.assertRaisesRegex(ValueError, 'full-HD'):
            register_frame(self.project / 'runs' / 'v0002',
                __import__('wolf_orbit.orbit_pipeline',fromlist=['job_for']).job_for(self.project / 'runs' / 'v0002',self.spec),
                15, self.source, 'independent_generation')

    def test_mutated_source_is_rejected(self):
        prepare(self.project,self.source,self.model,self.spec)
        Image.new('RGB',(1312,1199),(55,66,77)).save(self.source)
        with self.assertRaisesRegex(ValueError,'Immutable'):
            prepare(self.project,self.source,self.model,self.spec)

    def test_prepare_is_idempotent(self):
        prepare(self.project,self.source,self.model,self.spec)
        before=sha256(self.project/'runs'/'v0002'/'plan.json')
        prepare(self.project,self.source,self.model,self.spec)
        self.assertEqual(sha256(self.project/'runs'/'v0002'/'plan.json'),before)


if __name__ == '__main__': unittest.main()
