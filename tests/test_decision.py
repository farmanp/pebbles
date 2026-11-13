import copy
import unittest
from pebbles.decision import decide
from pebbles.analysis import analyze
import test_analysis as primary_tests
report = primary_tests.report

class Decision(unittest.TestCase):
    def fixture(self, tx=20):
        p=primary_tests.Analysis().plan()
        p.update(guardrails=[{'id':'refund','name':'Refunds','version':'v1','definition':'User had at least one refund within the declared window.','direction':'lower','max_harm_pp':2}],guardrails_predeclared=True,guardrails_complete=True,guardrails_set_complete=True,business_review_complete=True,business_review_notes='Reviewed implementation rollback and expected operating cost.')
        r=report();r['analysis']=analyze(r,p)
        cfg={'experiment_id':'e','revision':1,'window_start':'s','window_end':'e'}
        assignments=[({'user_id':f'{a}{i}','variant_id':a},i+1) for a in ['control','treatment'] for i in range(2000)]
        ev=dict(schema_version='1.0.0',**cfg,metrics=[{'id':'refund','version':'v1','definition':'User had at least one refund within the declared window.','rows':[{'user_id':f'{a}{i}','value':i<(20 if a=='control' else tx)} for a in ['control','treatment'] for i in range(2000)]}])
        return r,p,ev,assignments,cfg
    def test_support_harm_and_uncertainty(self):
        for tx,state,gs in [(20,'supported','within_limit'),(200,'do_not_ship','harm'),(55,'blocked','uncertain')]:
            r,p,e,a,c=self.fixture(tx);d=decide(r,p,e,a,c)
            self.assertEqual(d['status'],state);self.assertEqual(d['guardrails'][0]['status'],gs)
            self.assertTrue(d['supporting']);self.assertEqual(bool(d['blockers']),state!='supported')
    def test_missing_review_or_evidence_never_supports(self):
        for key in ['guardrails_predeclared','guardrails_complete','guardrails_set_complete','business_review_complete','business_review_notes']:
            r,p,e,a,c=self.fixture();p.pop(key);self.assertEqual(decide(r,p,e,a,c)['status'],'blocked',key)
        r,p,e,a,c=self.fixture();self.assertEqual(decide(r,p,None,a,c)['status'],'blocked')
        p['guardrails']=[];self.assertEqual(decide(r,p,e,a,c)['status'],'blocked')
    def test_bad_rows_scope_and_plan_fail_closed(self):
        for change in ['missing','duplicate','extra','nonboolean','scope','direction','margin','duplicate_metric']:
            r,p,e,a,c=self.fixture()
            if change=='missing':e['metrics'][0]['rows'].pop()
            if change=='duplicate':e['metrics'][0]['rows'].append(e['metrics'][0]['rows'][0])
            if change=='extra':e['metrics'][0]['rows'][0]['user_id']='outsider'
            if change=='nonboolean':e['metrics'][0]['rows'][0]['value']=1
            if change=='scope':e['revision']=2
            if change=='direction':p['guardrails'][0]['direction']='anything'
            if change=='margin':p['guardrails'][0]['max_harm_pp']=float('nan')
            if change=='duplicate_metric':p['guardrails']*=2
            self.assertEqual(decide(r,p,e,a,c)['status'],'blocked',change)
    def test_primary_gate_and_higher_direction(self):
        r,p,e,a,c=self.fixture();r['analysis']['status']='blocked'
        d=decide(r,p,e,a,c);self.assertEqual(d['status'],'blocked');self.assertIsNone(d['guardrails'][0].get('comparison'))
        r,p,e,a,c=self.fixture(200);p['guardrails'][0]['direction']='higher'
        self.assertEqual(decide(r,p,e,a,c)['status'],'supported')
    def test_multiple_guardrails_widen_interval(self):
        r,p,e,a,c=self.fixture();one=decide(r,p,e,a,c)['guardrails'][0]['comparison']
        p['guardrails'].append(dict(p['guardrails'][0],id='error'))
        e['metrics'].append(dict(e['metrics'][0],id='error'))
        two=decide(r,p,e,a,c)['guardrails'][0]['comparison']
        self.assertGreater(two['confidence_level'],one['confidence_level'])
        self.assertGreater(two['difference_ci'][1],one['difference_ci'][1])

    def test_integrated_examples_and_evidence_hash(self):
        import tempfile, shutil, json
        from pathlib import Path
        from pebbles.core import investigate
        root=Path(__file__).resolve().parents[1]
        for name,status in [('ship-supported','supported'),('ship-harm','do_not_ship'),('ship-uncertain','blocked')]:
            r=investigate(root/'examples/analysis'/name)
            self.assertEqual(r['decision']['status'],status)
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'packet';shutil.copytree(root/'examples/analysis/ship-supported',folder)
            with (folder/'guardrails.json').open('a') as f:f.write(' ')
            self.assertEqual(investigate(folder)['decision']['status'],'blocked')
