"""Contract tests for true incremental geometric checkpoints (not photo fidelity)."""
import json
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
from wolf_orbit.geometry import ANGLES
from wolf_orbit.surface import View, cast_visible_surface, human_faced_proxy
from wolf_orbit.texture_orbit import checkpoint_paths, execute, TEXTURE_H, TEXTURE_W
from wolf_orbit.assets import sha256

ROOT=Path(__file__).resolve().parents[1]

class SequentialGeometryTests(unittest.TestCase):
    def test_angles_and_progressive_chaining(self):
        records=json.loads((ROOT/'sequential'/'sequence_manifest.json').read_text())
        self.assertEqual([r['degree'] for r in records],list(ANGLES))
        previous=None
        previous_texels=0
        for rec in records:
            angle=rec['degree']
            state,render,meta=checkpoint_paths(ROOT,angle)
            self.assertEqual(rec['previous_checkpoint_sha256'],previous)
            self.assertEqual(sha256(state),rec['state_sha256'])
            self.assertEqual(sha256(render),rec['render_sha256'])
            self.assertGreater(rec['new_texels'],0)
            self.assertEqual(rec['total_texels']-previous_texels,rec['new_texels'])
            with np.load(state) as arr:
                self.assertEqual(arr['observed'].shape[1:],(TEXTURE_H,TEXTURE_W))
                self.assertEqual(int(arr['observed'].sum()),rec['total_texels'])
            previous=rec['state_sha256']
            previous_texels=rec['total_texels']

    def test_anatomy_not_rotated(self):
        p=human_faced_proxy()
        self.assertEqual(p,human_faced_proxy())
        for angle in ANGLES:
            f=cast_visible_surface(angle,View(96,88))
            self.assertTrue(np.isfinite(f.hit_distance[f.part_id>=0]).all())
            self.assertTrue((f.part_id>=0).any())
        self.assertEqual(p,human_faced_proxy())

    def test_120_shows_rear_and_hides_chest(self):
        front=cast_visible_surface(0,View(256,230)).part_id
        rear=cast_visible_surface(120,View(256,230)).part_id
        chest=lambda ids: np.isin(ids,(3,4)).sum()
        back=lambda ids: np.isin(ids,(1,2)).sum()
        self.assertGreater(chest(front),5*max(1,chest(rear)))
        self.assertGreater(back(rear),5*max(1,back(front)))

    def test_existing_assets_not_overwritten(self):
        refs={a:sha256(ROOT/'references'/n) for a,n in [(0,'00_front_reference.png'),(60,'60_intermediate_reference.png')]}
        first=execute(ROOT)
        second=execute(ROOT)
        self.assertTrue(all(r['cache']=='reused' for r in first+second))
        for angle,reference in [(0,'00_front_reference.png'),(60,'60_intermediate_reference.png')]:
            self.assertEqual(refs[angle],sha256(ROOT/'references'/reference))

if __name__=='__main__':unittest.main()
