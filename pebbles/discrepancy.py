"""Evidence-driven discrepancy diagnosis; never reads fixture recipes or answer keys."""
from .analysis import compare_proportions, valid_counts
from .public_comparison import cohort, METRICS

def conclusion(c):
    lo,hi=c['difference_ci']
    return 'lower_retention' if hi<0 else 'higher_retention' if lo>0 else 'inconclusive'

def counts(c):return {a:c[a] for a in ('control','treatment')}

def investigate_discrepancy(rows,reference,spec):
    if not isinstance(spec,dict) or spec.get('schema_version')!='1.0.0' or spec.get('controlled_exercise') is not True or spec.get('metric') not in METRICS:
        raise ValueError('Expected a labeled controlled exercise with a supported retention metric.')
    reported=spec.get('reported');metric=spec['metric']
    if not isinstance(reported,dict) or set(reported)!={'control','treatment'}:raise ValueError('Reported counts need exactly two arms.')
    for v in reported.values():
        if not isinstance(v,dict) or set(v)!={'retained_users','users'} or not valid_counts(v.get('retained_users'),v.get('users')) or v['users']>100000:raise ValueError('Invalid reported binary counts.')
    claim=compare_proportions(reported['control']['retained_users'],reported['control']['users'],reported['treatment']['retained_users'],reported['treatment']['users'])
    for a in ('control','treatment'):claim[a]['retained_users']=claim[a].pop('purchasers')
    supplied=cohort(rows);baseline=cohort(reference)
    actual=supplied[metric];corrected=baseline[metric]
    byid={r['userid']:r for r in rows};refid={r['userid']:r for r in reference}
    missing=sorted(set(refid)-set(byid));extra=sorted(set(byid)-set(refid));changed=sorted(i for i in set(refid)&set(byid) if refid[i]!=byid[i])
    missing_groups={a:{'users':0,'retained_users':0} for a in ('gate_30','gate_40')}
    for i in missing:
        r=refid[i];missing_groups[r['version']]['users']+=1;missing_groups[r['version']]['retained_users']+=r[metric]
    population={'missing_count':len(missing),'extra_count':len(extra),'changed_count':len(changed),'missing_by_arm':missing_groups,
                'missing_ids':missing,'extra_ids':extra,'changed_ids':changed,'source':'reference.csv versus cookie_cats.csv, joined by userid'}
    reasons=[];evidence=[]
    if missing or extra or changed:
        diagnosis='population_mismatch'
        reasons.append(f'The supplied export differs from the supplied reference: {len(missing):,} missing users, {len(extra):,} extra users and {len(changed):,} changed records.')
        for arm,v in missing_groups.items():
            if v['users']:reasons.append(f"Missing {arm} records: {v['users']:,} users, including {v['retained_users']:,} retained users for {metric}.")
        evidence.append({'file':'reference.csv','locator':'userid membership and matching row fields','detail':population})
    elif reported==counts(actual):
        diagnosis='agreement';reasons.append('Reported numerators and denominators match the supplied rows for the declared metric.')
    elif any(reported==counts(supplied[m]) for m in METRICS if m!=metric):
        other=next(m for m in METRICS if m!=metric and reported==counts(supplied[m]))
        diagnosis='metric_mismatch';reasons.append(f'The reported counts exactly match {other}, but the declared metric is {metric}. This demonstrates a metric/count mismatch; the upstream reason for the substitution is not established.')
    elif all(reported[a]['retained_users']==actual[a]['retained_users'] for a in reported) and any(reported[a]['users']!=actual[a]['users'] for a in reported):
        diagnosis='denominator_mismatch';reasons.append('Retained-user counts agree, but at least one reported denominator differs from the distinct users in that arm. The source of the wrong denominator is not established.')
    else:
        diagnosis='unexplained_counts';reasons.append('Reported counts disagree with the declared metric and do not exactly match a supported alternative. The cause remains unresolved.')
    count_diffs=[]
    for arm in ('control','treatment'):
        for field in ('retained_users','users'):
            if reported[arm][field]!=actual[arm][field]:count_diffs.append({'arm':arm,'field':field,'reported':reported[arm][field],'recomputed':actual[arm][field]})
    if diagnosis=='population_mismatch' and count_diffs:reasons.append('The reported counts also disagree with the supplied export; the population mismatch alone does not explain every discrepancy. Inspect the count differences separately.')
    evidence.append({'file':'investigation.json','locator':'reported','detail':reported})
    evidence.append({'file':'cookie_cats.csv','locator':f'group by version; distinct userid; sum {metric}','detail':counts(actual)})
    next_action = 'No controlled discrepancy detected. Original study and shipping evidence are still required.'
    if diagnosis == 'denominator_mismatch':
        changes = '; '.join(f"{x['arm']} denominator: reported {x['reported']:,}, supplied {x['recomputed']:,}" for x in count_diffs if x['field']=='users')
        next_action = f'Investigate and correct the reported denominator ({changes}), then regenerate the readout. The upstream cause is not established.'
    elif diagnosis == 'population_mismatch':
        details = '; '.join(f"{arm}: {v['users']:,} missing users, {v['retained_users']:,} retained for {metric}" for arm,v in missing_groups.items() if v['users'])
        next_action = f'Investigate the export omissions or record differences ({details or "inspect extra and changed user IDs"}). Confirm the intended population, repair the export and regenerate the readout. Do not silently substitute the reference; the upstream cause is unknown.'
    elif diagnosis == 'metric_mismatch':
        next_action = f'Reconcile the metric mapping with the declared {metric} definition and regenerate its counts and readout. Investigate how the other metric was substituted.'
    elif diagnosis == 'unexplained_counts':
        next_action = 'Trace each reported count difference to its query and source records, resolve the unsupported counts, then regenerate the readout.'
    before,after=conclusion(claim),conclusion(corrected)
    return {'version':'1.0.0','controlled_exercise':True,'metric':metric,'diagnosis':diagnosis,
            'reported':claim,'supplied':actual,'reference':corrected,'reported_matches_supplied':reported==counts(actual),
            'count_differences':count_diffs,'population':population,'why':reasons,'evidence':evidence,
            'reported_conclusion':before,'reference_conclusion':after,'conclusion_changed':before!=after,
            'decision_impact':f"The retention conclusion {'changes' if before!=after else 'does not change'}: {before.replace('_',' ')} → {after.replace('_',' ')}. Shipping readiness remains blocked in both views because the original decision evidence is missing.",
            'next_action':next_action,
            'limits':'Controlled mutation of public data, not an error attributed to the original analyst. The supplied reference is the comparison baseline, not independently proven production truth. Intervals are retrospective, unadjusted and conditional on independent users.',
            'problem_tree':{'primary':['OP-3','OP-4','OP-5'],'value_test':['OP-1','OP-7'],'provenance':['OP-2','OP-6']}}
