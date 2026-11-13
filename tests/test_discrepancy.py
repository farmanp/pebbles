import unittest
from pebbles.discrepancy import investigate_discrepancy
from pebbles.public_comparison import parse_csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Discrepancy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rows=parse_csv((ROOT/'public_comparisons/cookie_cats/source/cookie_cats.csv').read_text())
    def spec(self):return {'schema_version':'1.0.0','controlled_exercise':True,'metric':'retention_7','reported':{'control':{'retained_users':8502,'users':44700},'treatment':{'retained_users':8279,'users':45489}}}
    def test_clean_and_denominator(self):
        s=self.spec();d=investigate_discrepancy(self.rows,self.rows,s)
        self.assertEqual(d['diagnosis'],'agreement');self.assertFalse(d['conclusion_changed'])
        s['reported']['control']['users']=60000
        d=investigate_discrepancy(self.rows,self.rows,s)
        self.assertEqual(d['diagnosis'],'denominator_mismatch');self.assertTrue(d['conclusion_changed'])
    def test_wrong_metric(self):
        s=self.spec();s['reported']['control']['retained_users']=20034;s['reported']['treatment']['retained_users']=20119
        d=investigate_discrepancy(self.rows,self.rows,s)
        self.assertEqual(d['diagnosis'],'metric_mismatch');self.assertEqual(d['reported_conclusion'],'inconclusive')
    def test_missing_subset(self):
        gone={r['userid'] for r in [r for r in self.rows if r['version']=='gate_40' and not r['retention_7']][:5000]}
        supplied=[r for r in self.rows if r['userid'] not in gone]
        s=self.spec();s['reported']['treatment']['users']-=5000
        d=investigate_discrepancy(supplied,self.rows,s)
        self.assertEqual(d['diagnosis'],'population_mismatch');self.assertEqual(d['population']['missing_count'],5000);self.assertTrue(d['conclusion_changed'])
    def test_unknown_is_not_forced_into_known_case(self):
        s=self.spec();s['reported']['control']['retained_users']=100
        d=investigate_discrepancy(self.rows,self.rows,s)
        self.assertEqual(d['diagnosis'],'unexplained_counts')
    def test_packets_diagnosed_without_recipe_or_case_labels(self):
        import json, tempfile, shutil, hashlib
        from pebbles.core import investigate
        expected=json.loads((ROOT/'evaluation/discrepancy/expected.json').read_text())
        for name,want in expected.items():
            with tempfile.TemporaryDirectory() as tmp:
                folder=Path(tmp)/'anonymous';shutil.copytree(ROOT/'public_comparisons/cookie_cats/cases'/name,folder)
                (folder/'notes.txt').write_text('No case labels or diagnosis hints.')
                inv=json.loads((folder/'inventory.json').read_text())
                next(x for x in inv['artifacts'] if x['path']=='notes.txt')['sha256']=hashlib.sha256((folder/'notes.txt').read_bytes()).hexdigest()
                (folder/'inventory.json').write_text(json.dumps(inv))
                r=investigate(folder)
                self.assertEqual(r['discrepancy']['diagnosis'],want['diagnosis'])
                self.assertEqual(r['discrepancy']['conclusion_changed'],want['conclusion_changed'])
                self.assertEqual(r['decision']['status'],'blocked')
                self.assertTrue(r['controlled_exercise'])
    def test_missing_reference_and_invalid_claim_fail_closed(self):
        import tempfile, shutil, json, hashlib
        from pebbles.core import investigate
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'p';shutil.copytree(ROOT/'public_comparisons/cookie_cats/cases/clean',folder)
            (folder/'reference.csv').unlink()
            inv=json.loads((folder/'inventory.json').read_text());inv['artifacts']=[e for e in inv['artifacts'] if e['path']!='reference.csv']
            (folder/'inventory.json').write_text(json.dumps(inv))
            r=investigate(folder);self.assertIsNone(r['discrepancy']);self.assertEqual(r['execution_state'],'partial')
        s=self.spec();s['reported']['control']['label']='Gate 30'
        with self.assertRaises(ValueError):investigate_discrepancy(self.rows,self.rows,s)
        s=self.spec();s['reported']['control']['users']=False
        with self.assertRaises(ValueError):investigate_discrepancy(self.rows,self.rows,s)
