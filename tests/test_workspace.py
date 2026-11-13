import json
import tempfile
import unittest
from pathlib import Path
from pebbles.workspace import access


class Workspace(unittest.TestCase):
    def test_resume_and_preserve_scientific_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage=Path(tmp)
            run={'findings':[{'check_id':'P06','question':'What differs?', 'evidence_outcome':'Failed'}], 'decision':{'status':'blocked'}}
            before=json.dumps(run)
            read=lambda rid:run if rid=='run-1' else (_ for _ in ()).throw(ValueError('Unknown run'))
            e=access(storage,{'action':'create','name':'Checkout','owner':'Analyst'},read)['experiment']
            def act(action,**kw):return access(storage,dict(action=action,experiment_id=e['id'],**kw),read)['experiment']
            with self.assertRaises(ValueError):act('attach',run_id='missing')
            act('attach',run_id='run-1')
            with self.assertRaises(ValueError):act('track',run_id='run-1',finding_id='missing',request='Evidence')
            e=act('track',run_id='run-1',finding_id='P06',request='Recover omitted users',owner='Data team')
            f=e['followups'][0]
            e=act('update',followup_id=f['id'],revision=1,status='waiting for evidence',owner='Data team',request=f['request'],notes='Asked for export')
            with self.assertRaises(ValueError):act('update',followup_id=f['id'],revision=1,status='open',request='Stale')
            with self.assertRaises(ValueError):act('update',followup_id=f['id'],revision=2,status='dismissed',request=f['request'])
            e=act('update',followup_id=f['id'],revision=2,status='dismissed',request=f['request'],notes='Tracked in another ticket')
            resumed=access(storage)['experiments'][0]
            self.assertEqual(resumed,e)
            self.assertEqual(resumed['followups'][0]['check_outcome'],'Failed')
            self.assertEqual(len(resumed['events']),5)
            self.assertEqual(json.dumps(run),before)
            self.assertEqual(resumed['runs'],['run-1'])
            with self.assertRaises(ValueError):act('track',run_id='run-1',finding_id='P06',request='Duplicate')

    def test_duplicate_names_have_distinct_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            ids=[access(Path(tmp),{'action':'create','name':'Same'})['experiment']['id'] for _ in range(2)]
            self.assertNotEqual(*ids)
