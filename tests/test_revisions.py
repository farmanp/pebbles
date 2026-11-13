import copy
import tempfile
import unittest
from pathlib import Path
from pebbles.revisions import compare_runs
from pebbles.workspace import access

def run(status='Failed',state='Completed'):
    return {'input_hashes':{'a.csv':'one'},'findings':[{'check_id':'P06','question':'Mismatch?',
             'evidence_outcome':status,'execution_state':state,'explanation':'Evidence'}],
             'decision':{'status':'blocked','blockers':['Missing plan']}}

class Revisions(unittest.TestCase):
    def test_regular_analyses_keep_effect_and_interval(self):
        r=run()
        c={'difference':.02,'difference_ci':[.01,.03],
           'control':{'users':100,'retained_users':10},'treatment':{'users':100,'retained_users':12}}
        r['public_comparison']={'all_users':{'retention_7':c}}
        self.assertEqual(compare_runs(r,r)['after_result']['difference'],.02)
        del r['public_comparison']
        r['analysis']={'status':'improvement','comparison':c}
        self.assertEqual(compare_runs(r,r)['after_result']['interval'],[.01,.03])

    def test_missing_check_is_not_resolution(self):
        old=run();new=run('Verified','blocked-invalid-input')
        self.assertEqual(compare_runs(old,new)['findings'][0]['after'],'blocked-invalid-input')
        new['findings']=[]
        self.assertEqual(compare_runs(old,new)['findings'][0]['after'],'Not evaluated')
        new['input_hashes']={'b.csv':'two'}
        self.assertEqual([x['change'] for x in compare_runs(old,new)['files']],['removed','added'])

    def test_revision_recheck_then_regression_preserves_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);runs={'old':run(),'new':run('Verified'),'bad':run()}
            e=access(root,{'action':'create','name':'Experiment'})['experiment']
            def call(action,**kw):return access(root,dict(action=action,experiment_id=e['id'],**kw),runs.__getitem__)['experiment']
            call('attach',run_id='old')
            e=call('track',run_id='old',finding_id='P06',request='Correct export')
            original=copy.deepcopy(runs['old'])
            runs['new']['revision']={'experiment_id':e['id'],'parent_run_id':'old','reason':'Correction'}
            e=call('revision',run_id='new',parent_run_id='old',reason='Correction')
            f=e['followups'][0]
            self.assertEqual(f['status'],'ready to recheck')
            self.assertEqual(f['check_outcome'],'Failed')
            self.assertEqual(e['revisions'][0]['comparison']['after_decision']['status'],'blocked')
            call('update',followup_id=f['id'],revision=f['revision'],status='resolved',notes='Reviewed new evidence',request=f['request'])
            runs['bad']['revision']={'experiment_id':e['id'],'parent_run_id':'new','reason':'New discrepancy'}
            e=call('revision',run_id='bad',parent_run_id='new',reason='New discrepancy')
            self.assertEqual(e['followups'][0]['status'],'open')
            self.assertEqual(len(e['followups'][0]['rechecks']),2)
            self.assertEqual(runs['old'],original)
            self.assertEqual(access(root)['experiments'][0],e)
            with self.assertRaises(ValueError):call('revision',run_id='new',parent_run_id='old',reason='Correction')
