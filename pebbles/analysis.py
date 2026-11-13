"""Fixed-horizon independent-binomial analysis; no sequential or exposed-only inference."""
import math
from statistics import NormalDist

METHOD = 'newcombe-wilson-unpaired-95-v1'
DEFAULT_PLAN = {'schema_version':'1.0.0','control':'control','treatment':'treatment',
                'minimum_effect_pp':1.0,'expected_treatment_share':0.5,
                'predeclared':False,'randomized_independent':False,
                'window_complete':False,'complete_assigned_outcomes':False}
ASSUMPTIONS = {
 'predeclared':'Confirm that this single primary conversion metric, success threshold and fixed analysis time were specified before looking at results.',
 'randomized_independent':'Confirm random assignment of independent users with no interference between their outcomes.',
 'window_complete':'Confirm that the planned observation window and outcome collection are finished; repeated peeking is not supported.',
 'complete_assigned_outcomes':'Confirm that these exports cover the intended assigned population and all qualifying outcomes; this cannot be proven from these files alone.'}
LIMITS = ('This conclusion concerns the primary conversion metric under declared assumptions. '
         'It does not verify randomization implementation, production capture or rendering, '
         'and it does not assess guardrails, costs or authorize shipping.')


def valid_counts(x,n):
    return type(x) is int and type(n) is int and n>0 and 0<=x<=n


def wilson(x,n,confidence=.95):
    if not valid_counts(x,n): raise ValueError('Counts require 0 <= purchasers <= positive users.')
    z=NormalDist().inv_cdf((1+confidence)/2);p=x/n;z2=z*z;scale=1+z2/n
    center=(p+z2/(2*n))/scale
    half=z*math.sqrt(p*(1-p)/n+z2/(4*n*n))/scale
    return max(0.0,center-half),min(1.0,center+half)


def compare_proportions(control_x,control_n,treatment_x,treatment_n,confidence=.95):
    """Newcombe hybrid-score interval for treatment minus control (unpaired)."""
    cl,cu=wilson(control_x,control_n,confidence);tl,tu=wilson(treatment_x,treatment_n,confidence)
    c,t=control_x/control_n,treatment_x/treatment_n
    d=t-c
    lower=d-math.sqrt((t-tl)**2+(cu-c)**2)
    upper=d+math.sqrt((tu-t)**2+(c-cl)**2)
    return {'control_rate':c,'treatment_rate':t,'difference':d,
            'difference_ci':[max(-1.,lower),min(1.,upper)],
            'relative_lift':(t-c)/c if c else None,
            'control':{'purchasers':control_x,'users':control_n},
            'treatment':{'purchasers':treatment_x,'users':treatment_n},'confidence_level':confidence}


def numeric(value):
    try:
        return type(value) in (int,float) and math.isfinite(value)
    except OverflowError:
        return False


def analyze(report, plan, source='user-entered run settings'):
    result={'version':'1.0.0','method':METHOD,'status':'blocked','title':'We cannot assess the treatment effect yet.',
            'explanation':'','next_action':'Resolve the listed prerequisites and run a new investigation.',
            'blockers':[],'comparison':None,'srm':None,'plan':plan if isinstance(plan,dict) else None,
            'plan_source':source,'limitations':LIMITS,'guardrails':'Not evaluated',
            'problem_tree':{'branch':'OP-5','checkpoint':'CP-3 / G3','supporting':['OP-2','OP-3','OP-6','OP-7']}}
    blockers=result['blockers']
    findings={f['check_id']:f for f in report.get('findings',[])}
    values=findings.get('C02',{}).get('values')
    if not isinstance(plan,dict):
        blockers.append('Specify the analysis plan and confirm its study assumptions.')
        result['explanation']=blockers[0];return result
    if plan.get('schema_version','1.0.0')!='1.0.0': blockers.append('Unsupported analysis-plan version.')
    control,treatment=plan.get('control'),plan.get('treatment')
    if not isinstance(control,str) or not isinstance(treatment,str) or control==treatment:
        blockers.append('Choose two different control and treatment variants.')
    goal=plan.get('minimum_effect_pp');share=plan.get('expected_treatment_share')
    if not numeric(goal) or not 0<=goal<=100: blockers.append('Minimum worthwhile improvement must be between 0 and 100 percentage points.')
    if not numeric(share) or not 0<share<1: blockers.append('Expected treatment allocation must be strictly between 0% and 100%.')
    for key,message in ASSUMPTIONS.items():
        if plan.get(key) is not True: blockers.append(message)
    if report.get('metric_version')!='v2':
        blockers.append('This analysis requires the declared assigned-user v2 metric. Exposed-user conversion can condition on behavior affected by treatment; it is not substituted for an assigned-user effect.')
    for cid in ('C02','C05','C07','C08'):
        f=findings.get(cid,{})
        if f.get('evidence_outcome')!='Verified' or f.get('execution_state')!='Completed':
            blockers.append(f'{cid}: calculation, scorecard agreement, source scope and record integrity must be resolved before inference.')
    for f in findings.values():
        if f.get('evidence_outcome')=='Failed' or f.get('execution_state')!='Completed':
            blockers.append(f"{f['check_id']}: resolve the flagged measurement or input problem.")
    integrity=findings.get('C08',{}).get('values')
    if not isinstance(integrity,dict) or integrity.get('conflicts') or integrity.get('excluded'):
        blockers.append('Resolve record conflicts or exclusions before analyzing the complete assigned population.')
    usable=isinstance(values,dict) and isinstance(control,str) and isinstance(treatment,str) and control!=treatment and set(values)=={control,treatment}
    if not usable:
        blockers.append('Supported counts for the selected two variants are unavailable.')
    else:
        c,t=values[control],values[treatment]
        usable=all(isinstance(v,dict) and valid_counts(v.get('numerator'),v.get('denominator')) for v in (c,t))
        if not usable: blockers.append('Each arm needs valid binary counts and a positive denominator.')
        else:
            cr,tr=c['numerator']/c['denominator'],t['numerator']/t['denominator']
            result['comparison']={'control_rate':cr,'treatment_rate':tr,'difference':tr-cr,'difference_ci':None,
                                 'relative_lift':(tr-cr)/cr if cr else None,
                                 'control':{'purchasers':c['numerator'],'users':c['denominator']},
                                 'treatment':{'purchasers':t['numerator'],'users':t['denominator']},'confidence_level':None}
            if any(v.get('assigned')!=v['denominator'] for v in (c,t)):
                blockers.append('Metric denominators must equal all qualifying assigned users in each arm.')
            if any(type(v.get('assigned')) is not int or v['assigned']<=0 for v in (c,t)):
                blockers.append('Assignment counts must be positive integers for the allocation diagnostic.')
            if numeric(share) and 0<share<1 and all(type(v.get('assigned')) is int and v['assigned']>0 for v in (c,t)):
                cn,tn=c['assigned'],t['assigned'];total=cn+tn;ec,et=total*(1-share),total*share
                if min(ec,et)<5:
                    blockers.append('Too few assignments for the supported sample-ratio diagnostic (expected counts must each be at least five).')
                else:
                    chi2=(cn-ec)**2/ec+(tn-et)**2/et
                    p=math.erfc(math.sqrt(chi2/2))
                    result['srm']={'control_assigned':cn,'treatment_assigned':tn,'expected_treatment_share':share,
                                   'chi_squared':chi2,'p_value':p,'threshold':.001,'flagged':p<.001,
                                   'meaning':'Assignment-count diagnostic only; passing does not prove valid randomization.'}
                    if p<.001: blockers.append('Sample-ratio mismatch: assignment counts disagree with the declared allocation (p < 0.001). Investigate allocation or missing data before interpreting effects.')
    result['blockers']=list(dict.fromkeys(blockers))
    if result['blockers']:
        result['explanation']='The supplied evidence or study declarations do not support a reliable treatment-effect conclusion. Any displayed rates are descriptive only; no uncertainty interval or success verdict is issued.'
        return result
    comp=compare_proportions(c['numerator'],c['denominator'],t['numerator'],t['denominator'])
    result['comparison']=comp
    lo,hi=comp['difference_ci'];threshold=goal/100;delta=comp['difference']
    detail=f"Conversion was {100*comp['control_rate']:.2f}% for control and {100*comp['treatment_rate']:.2f}% for treatment: a difference of {100*delta:+.2f} percentage points. The 95% confidence interval for that difference is {100*lo:+.2f} to {100*hi:+.2f} points. Your worthwhile-improvement threshold is {goal:g} percentage points. "
    if lo>threshold:
        result.update(status='improvement',title='Evidence of a worthwhile improvement.',
                      explanation=detail+'The entire interval is above your threshold. Under the stated design and data assumptions, this supports a worthwhile improvement in the primary metric.',
                      next_action='Review guardrails, implementation risks and costs before the analyst makes a shipping recommendation.')
    elif hi<0:
        result.update(status='harm',title='Evidence that treatment reduced conversion.',
                      explanation=detail+'The entire interval is below zero. Under the stated assumptions, the evidence supports harm to this primary metric.',
                      next_action='Do not treat this primary-metric result as a success. Investigate the change and review guardrails and implementation before deciding next steps.')
    elif hi<threshold:
        result.update(status='below_threshold',title='The effect is below your worthwhile-improvement goal.',
                      explanation=detail+'The entire interval falls below your threshold. This does not mean the effect is exactly zero; it means the result does not meet the stated practical goal.',
                      next_action='Reconsider the change against the predeclared goal and costs. Do not lower the target after seeing this result to label it a success.')
    else:
        result.update(status='inconclusive',title='The evidence is inconclusive against your goal.',
                      explanation=detail+'The interval crosses the decision boundary. The observed lift alone is not enough to conclude that the improvement is worthwhile; inconclusive is not proof of no effect.',
                      next_action='Record the uncertainty. If more evidence is needed, plan a new appropriately sized experiment; do not extend or repeatedly peek at this fixed-horizon test until it wins.')
    return result
