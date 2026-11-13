import base64
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from start import seed_demo
from webdemo.bridge import dispatch

class BrowserDemoTests(unittest.TestCase):
    def test_real_results_exports_and_isolation(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as other:
            storage=Path(tmp); seed_demo(storage)
            def get(path):
                r=dispatch(storage,'GET',path)
                self.assertEqual(r['status'],200)
                return json.loads(base64.b64decode(r['body']))
            e=get('/api/workspace')['experiments'][0]
            original,corrected=[get('/api/runs/'+rid) for rid in e['runs']]
            self.assertAlmostEqual(original['intake']['comparison']['difference'],.1)
            self.assertAlmostEqual(corrected['intake']['comparison']['difference'],-.05)
            self.assertEqual(corrected['decision']['status'],'blocked')
            d=e['decisions'][0]
            result=dispatch(storage,'GET',f"/api/handoff/{e['id']}/{d['id']}")
            self.assertEqual(result['status'],200)
            self.assertIsNone(zipfile.ZipFile(io.BytesIO(base64.b64decode(result['body']))).testzip())
            self.assertEqual(json.loads(base64.b64decode(dispatch(Path(other),'GET','/api/workspace')['body'])),{'experiments':[]})
            self.assertEqual(dispatch(Path(other),'GET','/api/runs/'+e['runs'][0])['status'],404)
    def test_intake_and_invalid_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=dispatch(Path(tmp),'POST','/api/intake/preview',json.dumps({'content':'id,arm,result\n1,A,1\n2,B,0\n'}))
            self.assertEqual(r['status'],200)
            self.assertEqual(dispatch(Path(tmp),'POST','/api/workspace','not json')['status'],400)
            self.assertEqual(dispatch(Path(tmp),'DELETE','/api/workspace')['status'],405)

class DemoBundleTests(unittest.TestCase):
    def test_only_runtime_and_synthetic_files_are_published(self):
        from scripts.build_web_demo import build
        with tempfile.TemporaryDirectory() as tmp:
            output=build(tmp)
            with zipfile.ZipFile(output/'engine.zip') as z:
                names=z.namelist()
                self.assertIn('pebbles/core.py',names)
                self.assertIn('webdemo/bridge.py',names)
                self.assertTrue(any(n.startswith('examples/analysis/') for n in names))
                self.assertFalse(any(n.startswith(('runs/','planning/','public_comparisons/','evaluation/private-oracles/')) for n in names))
                self.assertFalse(any(n.endswith(('.sqlite','.env','.ipynb')) for n in names))
            html=(output/'index.html').read_text()
            self.assertNotIn('href="/',html)
            self.assertIn('Reloading clears your demo work',html)
            self.assertNotIn('__TOKEN__',html)
            import re
            version=re.search(r'bootstrap\.js\?v=([a-f0-9]{16})',html)
            self.assertIsNotNone(version, 'published assets need a build version')
            self.assertNotIn('__DEMO_BUILD__',(output/'bootstrap.js').read_text())
            self.assertIn(version.group(1),(output/'bootstrap.js').read_text())
            self.assertRegex(html,r'analyst-workspace\.css\?v='+version.group(1))
            self.assertIn('assetURL(name)',(output/'bootstrap.js').read_text())
            self.assertIn("assetURL('worker.js')",(output/'bootstrap.js').read_text())
            self.assertIn('engineURL.search=self.location.search',(output/'worker.js').read_text())

    def test_refuses_stale_output_files(self):
        from scripts.build_web_demo import build
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'private.csv').write_text('must not publish')
            with self.assertRaisesRegex(ValueError, 'empty'):
                build(tmp)
