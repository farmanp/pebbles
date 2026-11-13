import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from pebbles.core import investigate

ROOT=Path(__file__).resolve().parents[1]

class Explanation(unittest.TestCase):
    def summary(self,report):
        js="const p=require('./pebbles/static/presentation.js');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>console.log(JSON.stringify(p.explainReport(JSON.parse(s)))));"
        r=subprocess.run(['node','-e',js],input=json.dumps(report),text=True,capture_output=True,cwd=ROOT)
        self.assertEqual(r.returncode,0,r.stderr)
        return json.loads(r.stdout)

    def test_unknown_scope_is_not_agreement(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'input';shutil.copytree(ROOT/'evaluation/packages/p-7c41',p)
            inv=json.loads((p/'inventory.json').read_text())
            next(a for a in inv['artifacts'] if a['path']=='scorecard.json')['export_timestamp']='unknown'
            (p/'inventory.json').write_text(json.dumps(inv))
            summary=self.summary(investigate(p))
            self.assertEqual(summary['type'],'unknown')
            self.assertNotIn('matches these records',summary['title'])

    def test_reported_percentage_is_not_recalculated(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'input';shutil.copytree(ROOT/'evaluation/packages/p-7c41',p)
            s=json.loads((p/'scorecard.json').read_text());s['arms']['treatment']['rate_percent']=99
            (p/'scorecard.json').write_text(json.dumps(s))
            inv=json.loads((p/'inventory.json').read_text())
            next(a for a in inv['artifacts'] if a['path']=='scorecard.json')['sha256']=hashlib.sha256((p/'scorecard.json').read_bytes()).hexdigest()
            (p/'inventory.json').write_text(json.dumps(inv))
            summary=self.summary(investigate(p))
            self.assertEqual(summary['comparison']['reportedPercent'],99)
            self.assertAlmostEqual(summary['comparison']['calculatedPercent'],66.667,places=3)

    def test_expected_example_explanation(self):
        summary=self.summary(investigate(ROOT/'evaluation/packages/p-a893'))
        self.assertEqual(summary['type'],'attention')
        self.assertEqual(summary['comparison']['reportedPercent'],50)
        self.assertIn('3 distinct users',summary['body'])

    def test_guardrail_import_never_drops_invalid_required_metrics(self):
        js="""const {guardrailPlanError}=require('./pebbles/static/presentation.js');
        const assert=require('node:assert/strict');
        assert.ok(guardrailPlanError(Array.from({length:11},(_,i)=>({id:String(i)}))));
        assert.ok(guardrailPlanError([null]));assert.ok(guardrailPlanError({}));
        assert.equal(guardrailPlanError([{id:'refund'}]),null);
        assert.equal(guardrailPlanError(undefined),null);"""
        r=subprocess.run(['node','-e',js],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)

if __name__=='__main__':unittest.main()
