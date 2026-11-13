import copy
import unittest

from pebbles.analysis import compare_proportions, analyze, DEFAULT_PLAN


def report(cn=400,cd=2000,tn=520,td=2000):
    values={'control':{'numerator':cn,'denominator':cd,'assigned':cd},'treatment':{'numerator':tn,'denominator':td,'assigned':td}}
    fs=[{'check_id':f'C{i:02d}','evidence_outcome':'Verified','execution_state':'Completed','values':None} for i in range(1,9)]
    fs[1]['values']=values
    fs[7]['values']={'excluded':[],'conflicts':[],'identical_replays':0,'repeat_encounters':0}
    return {'execution_state':'Completed','metric_version':'v2','findings':fs}

class Analysis(unittest.TestCase):
    def plan(self):
        return dict(DEFAULT_PLAN,control='control',treatment='treatment',minimum_effect_pp=1.0,expected_treatment_share=0.5,predeclared=True,randomized_independent=True,window_complete=True,complete_assigned_outcomes=True)

    def test_positive_harm_and_inconclusive(self):
        self.assertEqual(analyze(report(),self.plan())['status'],'improvement')
        self.assertEqual(analyze(report(tn=280),self.plan())['status'],'harm')
        self.assertEqual(analyze(report(tn=412),self.plan())['status'],'inconclusive')

    def test_not_worthwhile_is_distinct_from_no_effect(self):
        p=self.plan();p['minimum_effect_pp']=10
        a=analyze(report(),p)
        self.assertEqual(a['status'],'below_threshold')
        self.assertGreater(a['comparison']['difference_ci'][0],0)

    def test_actual_investigation_to_analysis_and_sparse_extremes(self):
        from pathlib import Path
        from pebbles.core import investigate
        root=Path(__file__).resolve().parents[1]
        for name,status in [('benefit','improvement'),('uncertain','inconclusive'),('harm','harm')]:
            r=investigate(root/'examples/analysis'/name)
            self.assertEqual(r['metric_version'],'v2')
            self.assertEqual(r['analysis']['status'],status)
            self.assertIsNotNone(r['analysis']['srm'])
        self.assertEqual(analyze(report(cn=1,cd=4,tn=2,td=4),self.plan())['status'],'blocked')
        for counts in [(100,100,100,100),(0,100,100,100),(100,100,0,100)]:
            c=compare_proportions(*counts)
            self.assertTrue(-1<=c['difference_ci'][0]<=c['difference_ci'][1]<=1)

    def test_unsupported_ancillary_sql_intentionally_blocks(self):
        r=report();r['findings'][2].update(evidence_outcome=None,execution_state='blocked-unsupported-operation')
        self.assertEqual(analyze(r,self.plan())['status'],'blocked')

    def test_interval_reference_and_symmetry(self):
        a=compare_proportions(400,2000,520,2000)
        self.assertAlmostEqual(a['difference'],.06)
        self.assertAlmostEqual(a['relative_lift'],.3)
        self.assertTrue(.033<a['difference_ci'][0]<.035)
        self.assertTrue(.085<a['difference_ci'][1]<.087)
        b=compare_proportions(520,2000,400,2000)
        self.assertAlmostEqual(a['difference_ci'][0],-b['difference_ci'][1])
        self.assertAlmostEqual(a['difference_ci'][1],-b['difference_ci'][0])

    def test_missing_plan_exposure_population_and_failed_integrity_block(self):
        self.assertEqual(analyze(report(),None)['status'],'blocked')
        r=report();r['metric_version']='v1'
        self.assertEqual(analyze(r,self.plan())['status'],'blocked')
        r=report();r['findings'][4]['evidence_outcome']='Failed'
        a=analyze(r,self.plan());self.assertEqual(a['status'],'blocked');self.assertIsNone(a['comparison'].get('difference_ci'))

    def test_unknown_assumptions_do_not_get_silent_defaults(self):
        for field in ('predeclared','randomized_independent','window_complete','complete_assigned_outcomes'):
            p=self.plan();p[field]=False
            self.assertEqual(analyze(report(),p)['status'],'blocked')
            p[field]='true'
            self.assertEqual(analyze(report(),p)['status'],'blocked')

    def test_srm_blocks_and_zero_baseline_has_no_relative_lift(self):
        a=analyze(report(cn=160,cd=800,tn=40,td=200),self.plan())
        self.assertEqual(a['status'],'blocked');self.assertLess(a['srm']['p_value'],.001)
        self.assertIsNone(compare_proportions(0,100,10,100)['relative_lift'])
        a=compare_proportions(0,100,0,100)
        self.assertLess(a['difference_ci'][0],0);self.assertGreater(a['difference_ci'][1],0)

    def test_invalid_counts_plan_and_arm_selection_fail_closed(self):
        for p in [dict(self.plan(),minimum_effect_pp=-1),dict(self.plan(),minimum_effect_pp=float('nan')),dict(self.plan(),expected_treatment_share=1),dict(self.plan(),control='treatment')]:
            self.assertEqual(analyze(report(),p)['status'],'blocked')
        r=report();r['findings'][1]['values']['control']['numerator']=2001
        self.assertEqual(analyze(r,self.plan())['status'],'blocked')
        self.assertEqual(analyze(report(cd=0,cn=0),self.plan())['status'],'blocked')

    def test_invalid_assignment_counts_and_huge_plan_numbers_block(self):
        r=report()
        for v in r['findings'][1]['values'].values():v['assigned']=2000.0
        self.assertEqual(analyze(r,self.plan())['status'],'blocked')
        for key in ('minimum_effect_pp','expected_treatment_share'):
            p=self.plan();p[key]=10**1000
            self.assertEqual(analyze(report(),p)['status'],'blocked')

    def test_unresolved_exclusions_block_but_repeat_encounter_does_not(self):
        r=report();r['findings'][7]['values']['excluded']=[{'reason':'orphan'}]
        self.assertEqual(analyze(r,self.plan())['status'],'blocked')
        r=report();r['findings'][7]['values']['repeat_encounters']=20
        self.assertEqual(analyze(r,self.plan())['status'],'improvement')

if __name__=='__main__':unittest.main()
