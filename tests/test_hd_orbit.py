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

class PipelineEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/'source.png'
        self.model=self.root/'model.glb'
        self.source.write_bytes(b'original image evidence')
        self.model.write_bytes(b'locked model revision')
        self.job=OrbitJob(self.source, model=self.model)

    def test_pure_next_task_is_model_and_parent_locked(self):
        from wolf_orbit.hd_orbit import task_request,dependencies
        deps=dependencies(self.job)
        first=task_request(self.job,(),**{'source_digest':deps['source_sha256'],'model_digest':deps['model_sha256']})
        self.assertEqual(first['angle'],0)
        self.assertEqual(first['required_origin'],'anchor')
        anchor={**deps,'sha256':'abc','angle':0,'visual_review':'anchor'}
        second=task_request(self.job,(anchor,),source_digest=deps['source_sha256'],model_digest=deps['model_sha256'])
        self.assertEqual(second['angle'],15)
        self.assertEqual(second['previous_sha256'],'abc')
        with self.assertRaises(ValueError):
            task_request(self.job,(anchor,),source_digest='modified',model_digest=deps['model_sha256'])
        with self.assertRaises(ValueError):
            task_request(self.job,({**anchor,'visual_review':'unverified'},),source_digest=deps['source_sha256'],model_digest=deps['model_sha256'])

    def test_change_of_fixed_model_rejected_at_registration(self):
        from wolf_orbit.hd_orbit import verify_dependencies,dependencies
        deps=dependencies(self.job)
        records=({'angle':0,**deps},)
        verify_dependencies(records,deps)
        self.model.write_bytes(b'secret model change')
        with self.assertRaisesRegex(ValueError,'model_sha256'):
            verify_dependencies(records,dependencies(self.job))

    def test_unreviewed_end_does_not_count_complete(self):
        from wolf_orbit.hd_orbit import task_request,dependencies
        deps=dependencies(self.job)
        states=tuple({**deps,'sha256':str(a),'visual_review':'anchor' if a==0 else 'unverified'}
                     for a in range(0,121,15))
        with self.assertRaises(ValueError):task_request(self.job,states[:-1],source_digest=deps['source_sha256'],model_digest=deps['model_sha256'])
