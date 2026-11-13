import json
from pathlib import Path
import tempfile
import unittest
from start import seed_demo
from pebbles.workspace import access

class QuickstartTests(unittest.TestCase):
    def test_offline_seed_is_repeatable_and_preserves_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);eid=seed_demo(root)
            e=access(root)['experiments'][0]
            self.assertEqual(len(e['runs']),2)
            before={rid:(root/rid/'report.json').read_bytes() for rid in e['runs']}
            old,new=[json.loads(before[rid]) for rid in e['runs']]
            self.assertGreater(old['intake']['comparison']['difference'],0)
            self.assertLess(new['intake']['comparison']['difference'],0)
            self.assertEqual(new['decision']['status'],'blocked')
            self.assertIn('simulated',e['decisions'][0]['review']['reviewer'])
            self.assertEqual(seed_demo(root),eid)
            self.assertEqual(len(access(root)['experiments']),1)
            for rid,raw in before.items():self.assertEqual((root/rid/'report.json').read_bytes(),raw)
