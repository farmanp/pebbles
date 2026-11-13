import copy, hashlib, io, json, tempfile, unittest, zipfile
from pathlib import Path
from pebbles.workspace import access
from pebbles.handoff import obligations, needs_renewal, bundle

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.run={'run_id':'r1','findings':[],'input_hashes':{'notes.txt':hashlib.sha256(b'evidence').hexdigest()},'not_evaluated':['Capture unverified'],'decision':{'status':'blocked','blockers':['Missing plan'],'unresolved':['Randomization assumed']}}
        self.run.update(headline='Snapshot only',scope='Test',execution_state='Completed',created_at='2026-11-13T00:00:00Z')
        self.run['decision'].update(title='Blocked',supporting=[],guardrails=[],plan=None,next_action='Obtain evidence',limitations='Not verified')
        self.runs={'r1':self.run,'r2':dict(self.run,run_id='r2')}
        self.e=access(self.root,{'action':'create','name':'Test <experiment>'})['experiment']
        self.act(action='attach',run_id='r1')
    def tearDown(self):self.tmp.cleanup()
    def act(self,**body):
        self.e=access(self.root,dict(experiment_id=self.e['id'],**body),lambda rid:self.runs[rid])['experiment'];return self.e
    def recommend(self,**overrides):
        return self.act(**(dict(action='recommend',run_id='r1',author='Analyst',recommendation='hold',rationale='Await plan',acknowledged=[x['id'] for x in obligations(self.run)])|overrides))['decisions'][-1]
    def review(self,d,**overrides):
        return self.act(**(dict(action='review',decision_id=d['id'],reviewer='Reviewer',outcome='agree',rationale='Hold until evidence is supplied',confirmed=True)|overrides))['decisions'][-1]
    def test_required_acknowledgement_and_review(self):
        original=copy.deepcopy(self.run)
        for data in [dict(acknowledged=[]),dict(author=''),dict(rationale=''),dict(recommendation='yes'),dict(run_id='r2')]:
            with self.assertRaises(ValueError):self.recommend(**data)
        d=self.recommend(recommendation='ship') # Human disagreement must not alter machine result.
        with self.assertRaises(ValueError):self.review(d,confirmed=False)
        d=self.review(d,outcome='disagree')
        self.assertEqual(d['assessment']['status'],'blocked');self.assertEqual(original,self.run)
        with self.assertRaises(ValueError):self.review(d)
        self.assertEqual(access(self.root)['experiments'][0]['decisions'][-1],d)
    def test_new_evidence_invalidates_review_without_overwrite(self):
        d=self.recommend();saved=copy.deepcopy(d);self.act(action='attach',run_id='r2')
        self.assertTrue(needs_renewal(self.e,d))
        with self.assertRaises(ValueError):self.review(d)
        self.assertEqual(self.e['decisions'][0],saved)
    def test_bundle_evidence_and_stale_status(self):
        for rid,r in self.runs.items():
            p=self.root/rid;(p/'evidence').mkdir(parents=True);(p/'evidence/notes.txt').write_bytes(b'evidence')
            (p/'report.json').write_text(json.dumps(r));(p/'report.md').write_text('Report');(p/'report.html').write_text('<p>Report</p>')
        d=self.recommend()
        with self.assertRaises(ValueError):bundle(self.e,d,lambda rid:self.root/rid)
        d=self.review(d);self.act(action='attach',run_id='r2')
        z=zipfile.ZipFile(io.BytesIO(bundle(self.e,d,lambda rid:self.root/rid)))
        self.assertTrue(json.loads(z.read('decision.json'))['needs_renewal'])
        self.assertIn(b'REVIEW NEEDS RENEWAL',z.read('README.md'))
        self.assertIn(b'&lt;experiment&gt;',z.read('index.html'))
        self.assertEqual(z.read('runs/r1/evidence/notes.txt'),b'evidence')
        self.assertIn(b'Blocked',z.read('runs/r1/report.html'))
        self.assertNotEqual(z.read('runs/r1/report.html'),b'<p>Report</p>')
        self.assertNotIn('runs/r2/report.json',z.namelist())
        for name,digest in json.loads(z.read('manifest.json')).items():self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),digest)
        (self.root/'r1/evidence/notes.txt').write_text('changed')
        with self.assertRaises(ValueError):bundle(self.e,d,lambda rid:self.root/rid)
