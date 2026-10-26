import tempfile
import unittest
from pathlib import Path
from PIL import Image
from wolf_orbit.hd_orbit import OrbitJob,angles,check_stage,register_frame,load_records,status
from wolf_orbit.assets import sha256

class OrbitHDTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.source=self.root/'input.png'
        Image.new('RGB',(1024,1024),(22,33,44)).save(self.source)
        self.second=self.root/'second.png'
        Image.new('RGB',(1024,1024),(55,66,77)).save(self.second)
        self.job=OrbitJob(self.source)

    def test_minimal_inputs_and_divisibility(self):
        self.assertEqual(angles(self.job),tuple(range(0,121,15)))
        with self.assertRaises(ValueError):angles(OrbitJob(self.source,119,15))

    def test_anchor_preserved_and_chained(self):
        old_sha=sha256(self.source)
        p=register_frame(self.root,self.job,0,self.source,'anchor')
        self.assertEqual(old_sha,p['sha256'])
        q=register_frame(self.root,self.job,15,self.second,'independent_generation')
        self.assertEqual(q['previous_sha256'],p['sha256'])
        self.assertEqual(status(self.root,self.job)['next_angle'],30)
        self.assertEqual(sha256(self.source),old_sha)
        self.assertEqual(len(load_records(self.root)),2)

    def test_atlas_and_lowres_rejected(self):
        register_frame(self.root,self.job,0,self.source,'anchor')
        small=self.root/'small.png'
        Image.new('RGB',(700,700)).save(small)
        with self.assertRaises(ValueError):register_frame(self.root,self.job,15,small,'independent_generation')
        with self.assertRaises(ValueError):register_frame(self.root,self.job,15,self.second,'independent_generation',derived_from_crop=True)
        with self.assertRaises(ValueError):register_frame(self.root,self.job,15,self.second,'anchor')
        self.assertEqual(len(load_records(self.root)),1)

    def test_duplicate_or_jump_rejected(self):
        register_frame(self.root,self.job,0,self.source,'anchor')
        with self.assertRaises(ValueError):register_frame(self.root,self.job,30,self.second,'independent_generation')
        with self.assertRaises(ValueError):register_frame(self.root,self.job,15,self.source,'independent_generation')

if __name__=='__main__':unittest.main()
