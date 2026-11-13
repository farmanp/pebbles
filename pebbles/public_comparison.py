"""Bounded Cookie Cats snapshot replay. Never fabricates timestamped event evidence."""
import csv
from datetime import datetime, timezone
import io
import math
from statistics import NormalDist
import uuid
from .analysis import compare_proportions

METRICS=('retention_1','retention_7')
GAPS=[
 'No original dated analysis plan, worthwhile-effect threshold or guardrail harm limits are supplied.',
 'No assignment/exposure timestamps or raw retention events are supplied; event attribution and treatment delivery cannot be verified.',
 'The published dataset description reports random assignment, but implementation and production completeness cannot be independently verified.',
 'Revenue, payment conversion, uninstalls, costs and implementation-risk review are absent. Day-1 retention is secondary, not a predeclared safety guardrail.',
 'The 50/50 allocation used for the diagnostic is a replay assumption, not an independently recovered allocation contract.'
]

def parse_csv(text):
    reader=csv.DictReader(io.StringIO(text))
    if reader.fieldnames!=['userid','version','sum_gamerounds','retention_1','retention_7']:
        raise ValueError('Unsupported snapshot columns: this adapter only accepts the documented Cookie Cats CSV.')
    rows=[];seen=set()
    for line,r in enumerate(reader,2):
        if len(rows)>=100_000:raise ValueError('Snapshot exceeds 100,000 users.')
        if None in r or any(v is None or not v for v in r.values()):raise ValueError(f'Incomplete or extra fields at CSV line {line}.')
        if not r['userid'].isdigit() or r['userid'] in seen:raise ValueError(f'Invalid or duplicate user at CSV line {line}.')
        if r['version'] not in ('gate_30','gate_40'):raise ValueError(f'Unknown arm at CSV line {line}.')
        if not r['sum_gamerounds'].isdigit():raise ValueError(f'Invalid rounds at CSV line {line}.')
        if any(r[m] not in ('True','False','TRUE','FALSE') for m in METRICS):raise ValueError(f'Missing or invalid retention flag at CSV line {line}.')
        seen.add(r['userid']);rows.append(dict(r,sum_gamerounds=int(r['sum_gamerounds']),**{m:r[m] in ('True','TRUE') for m in METRICS}))
    if set(r['version'] for r in rows)!={'gate_30','gate_40'}:raise ValueError('Both arms must contain observations.')
    return rows

def cohort(rows):
    arms={a:[r for r in rows if r['version']==a] for a in ('gate_30','gate_40')}
    if any(not a for a in arms.values()):raise ValueError('An exclusion emptied an arm.')
    results={}
    for metric in METRICS:
        cx,tx=[sum(r[metric] for r in arms[a]) for a in ('gate_30','gate_40')]
        cn,tn=[len(arms[a]) for a in ('gate_30','gate_40')]
        comp=compare_proportions(cx,cn,tx,tn)
        for arm in ('control','treatment'):comp[arm]['retained_users']=comp[arm].pop('purchasers')
        # Independent reproduction of the notebook's pooled z-test and unpooled Wald interval.
        c,t=cx/cn,tx/tn;pooled=(cx+tx)/(cn+tn)
        se=math.sqrt(c*(1-c)/cn+t*(1-t)/tn)
        pooled_se=math.sqrt(pooled*(1-pooled)*(1/cn+1/tn))
        z=(t-c)/pooled_se if pooled_se else 0
        comp['wald']={'difference_ci':[t-c-NormalDist().inv_cdf(.975)*se,t-c+NormalDist().inv_cdf(.975)*se],
                      'p_value':math.erfc(abs(z)/math.sqrt(2))}
        results[metric]=comp
    return results

def calculate(rows):
    maximum=max(r['sum_gamerounds'] for r in rows)
    excluded=[r for r in rows if r['sum_gamerounds']==maximum]
    matching=[r for r in rows if r['sum_gamerounds']!=maximum]
    cn=sum(r['version']=='gate_30' for r in rows);tn=len(rows)-cn
    chi=(cn-len(rows)/2)**2/(len(rows)/2)+(tn-len(rows)/2)**2/(len(rows)/2)
    return {'row_count':len(rows),'all_users':cohort(rows),'analyst_population':cohort(matching),
            'excluded_users':excluded,'analyst_row_count':len(matching),
            'srm':{'assumed_treatment_share':.5,'p_value':math.erfc(math.sqrt(chi/2)),
                   'control_users':cn,'treatment_users':tn,'warning':'Assumed allocation; not proof of correct randomization.'}}

def investigate_snapshot(e,analysis_plan=None):
    from .core import InputProblem
    findings=[]
    def finding(cid,question,explanation,status='Verified',values=None,request=None,state='Completed'):
        findings.append({'check_id':cid,'check_version':'1.0.0','question':question,'scope':'Public snapshot only',
                         'execution_state':state,'evidence_outcome':status if state=='Completed' else None,
                         'explanation':explanation,'values':values,'evidence':e.refs(('cookie_cats.csv','readout.json','analyst.ipynb')),
                         'limitations':'Retrospective public-data replay, not an independently validated production experiment.',
                         'next_evidence_request':request})
    result=None
    discrepancy=None
    controlled='investigation.json' in e.hashes or 'reference.csv' in e.hashes
    try:
        missing=e.require('cookie_cats.csv','readout.json','analyst.ipynb')
        if missing:raise ValueError('Missing comparison evidence: '+', '.join(missing))
        # Do not permit another invalid supplied file to disappear behind snapshot routing.
        if e.errors:raise ValueError('; '.join(str(v) for v in e.errors.values()))
        if set(e.entries)-{'cookie_cats.csv','readout.json','analyst.ipynb','notes.txt','reference.csv','investigation.json'}:raise ValueError('Do not mix timestamped event packages with this bounded public-snapshot adapter.')
        rows=parse_csv(e.data['cookie_cats.csv']);result=calculate(rows)
        if controlled:
            missing=e.require('reference.csv','investigation.json')
            if missing:raise ValueError('Controlled investigation needs '+', '.join(missing))
            from .discrepancy import investigate_discrepancy
            discrepancy=investigate_discrepancy(rows,parse_csv(e.data['reference.csv']),e.data['investigation.json'])
        readout=e.data['readout.json']
        if readout.get('source_sha256')!=e.hashes.get('analyst.ipynb'):raise ValueError('Readout source fingerprint does not match the supplied analyst notebook.')
        if readout.get('adapter')!='cookie-cats-v1' or not isinstance(readout.get('metrics'),dict):raise ValueError('Unsupported analyst-readout contract.')
        checks=[]
        for metric in METRICS:
            expected=readout['metrics'].get(metric)
            if not isinstance(expected,dict):raise ValueError('Readout needs both retention metric summaries.')
            observed=result['analyst_population'][metric]
            for key,value in [('control_rate',observed['control_rate']),('treatment_rate',observed['treatment_rate']),('difference',observed['difference']),('p_value',observed['wald']['p_value'])]:
                target=expected.get(key)
                if type(target) not in (int,float) or not math.isfinite(target):raise ValueError('Readout numeric summaries must be finite.')
                tolerance=.0000005 if key=='p_value' else .00005
                checks.append({'metric':metric,'field':key,'published':target,'recalculated':value,'tolerance':tolerance,'matches':abs(target-value)<=tolerance+1e-12})
            bounds=expected.get('wald_ci')
            if not isinstance(bounds,list) or len(bounds)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in bounds):raise ValueError('Readout needs finite two-sided Wald bounds.')
            for index in range(2):
                value=observed['wald']['difference_ci'][index]
                checks.append({'metric':metric,'field':'wald_ci_'+str(index),'published':bounds[index],'recalculated':value,'tolerance':.00005,'matches':abs(bounds[index]-value)<=.00005+1e-12})
        result.update(readout=readout,readout_checks=checks,method='Newcombe/Wilson 95% per-metric intervals; unadjusted retrospective comparisons, not a predeclared guardrail family.',
                      interpretation='Day-7 retention is lower for gate_40 in this snapshot, consistent with the analyst’s recommendation to retain gate_30. The snapshot alone does not establish a complete shipping decision.',gaps=GAPS)
        # Interpretation must follow the computed evidence, not the included dataset's expected result.
        day7=result['all_users']['retention_7']
        result['interpretation']=('The day-7 interval is below zero: the snapshot supports lower retention for gate_40 under independent-user assumptions.' if day7['difference_ci'][1]<0 else 'The day-7 interval is above zero under independent-user assumptions.' if day7['difference_ci'][0]>0 else 'The day-7 interval includes zero; the snapshot does not resolve the direction of the difference.')+' The original study and shipping prerequisites remain unresolved.'
        result['population_warning'] = ('Incomplete or differing supplied export: these export-only intervals must not be used for the intended-population conclusion. Use the supplied-reference comparison above, subject to its limitations.' if discrepancy and discrepancy['diagnosis']=='population_mismatch' else 'These calculations describe the supplied export. Agreement does not independently establish production completeness.')
        result['exclusion_note'] = 'Applying the supplied notebook’s maximum-rounds exclusion rule does not establish that its population matches this export. Compare user membership and the supplied reference separately.'
        result['srm']['display_p_value'] = '< 0.000001' if result['srm']['p_value'] < .000001 else f"{result['srm']['p_value']:.6f}"
        finding('P01','Are the snapshot rows usable?',f'{len(rows):,} unique users; both retention fields contain complete Boolean observations. This does not prove production capture completeness.',values={'rows':len(rows),'missing':0,'duplicate_users':0})
        finding('P02','Can the supplied readout retention results be reproduced?', 'Applying the supplied notebook exclusion to the export reproduces the supplied readout values at display precision; this is not independent proof of matching populations.' if all(c['matches'] for c in checks) else 'At least one supplied readout value differs beyond its display precision. Applying the same exclusion rule does not establish matching populations.', 'Verified' if all(c['matches'] for c in checks) else 'Failed',values=checks)
        finding('P03','Does the analyst’s exclusion change the result?', 'Show all supplied users and separately replay the notebook’s exclusion of every maximum-rounds row. The exclusion uses a post-assignment outcome; it is not silently accepted as the primary population.',values={'excluded_users':result['excluded_users'],'all_users':result['all_users'],'analyst_population':result['analyst_population']})
        finding('P04','Does the allocation look balanced?',f"Against an assumed 50/50 allocation, the full-snapshot sample-ratio p-value is {result['srm']['display_p_value']}. The diagnostic is {'flagged' if result['srm']['p_value']<.001 else 'not flagged'} at Pebbles' 0.001 cutoff. This is not independent verification of assignment.",'Insufficient evidence',values=result['srm'],request='Recover the actual planned allocation and investigate the imbalance.')
        finding('P05','Does the public snapshot support a shipping review?', ' '.join(GAPS),'Insufficient evidence',request='Obtain original study-plan, instrumentation, guardrail and business-review evidence.')
        if discrepancy:
            finding('P06','What disagrees, why, and does it change the conclusion?', ' '.join(discrepancy['why'])+' '+discrepancy['decision_impact'], 'Verified' if discrepancy['diagnosis']=='agreement' else 'Failed',values=discrepancy,request=discrepancy['next_action'])
            findings[-1]['evidence']=e.refs(('cookie_cats.csv','reference.csv','investigation.json'))
    except (InputProblem,ValueError,TypeError,KeyError,OverflowError,csv.Error) as ex:
        result=None
        discrepancy=None
        finding('P00','Can the snapshot comparison run?',str(ex),state='blocked-invalid-input')
    complete=all(f['execution_state']=='Completed' for f in findings)
    decision={'version':'1.0.0','status':'blocked','title':'The public snapshot is not enough for a shipping recommendation.',
              'supporting':[result['interpretation']] if result else [],'blockers':GAPS if result else ['Correct the snapshot input errors before interpreting results.'],
              'unresolved':['The supplied readout is not the original company decision record.'],
              'guardrails':[],'plan':None,'limitations':'Retrospective comparison only. No invented event times, guardrail thresholds or study attestations.',
              'next_action':'Use the reproduced retention result to investigate the proposed change; recover missing decision evidence before a production recommendation.',
              'method':'Snapshot replay with separate all-user and analyst-excluded populations.',
              'problem_tree':{'branch':'OP-1 / OP-5','supporting':['OP-2','OP-3','OP-4','OP-6','OP-7']}}
    if discrepancy and discrepancy['diagnosis']!='agreement':
        decision['blockers']=['Controlled discrepancy: '+discrepancy['diagnosis'].replace('_',' ')+'. '+discrepancy['decision_impact']]+decision['blockers']
        decision['supporting']=['The supplied export calculation is provisional; inspect the discrepancy and reference comparison above.']
        decision['next_action']=discrepancy['next_action']+' Recover the missing study, guardrail and business-review evidence before a shipping recommendation.'
    return {'schema_version':'1.0.0','prototype_version':'public-snapshot-1','run_id':str(uuid.uuid4()),'created_at':datetime.now(timezone.utc).isoformat(),
            'input_hashes':e.hashes,'execution_state':'Completed' if complete else 'partial','uncompleted_checks':[] if complete else ['P00'],
            'headline':'Public retention readout compared; shipping evidence remains incomplete' if complete else 'Public snapshot comparison could not complete',
            'scope':'Cookie Cats user-level retention snapshot. No timestamped assignment or exposure evidence is inferred.',
            'findings':findings,'analysis':None,'decision':decision,'public_comparison':result,'public_dataset':True,'controlled_exercise':controlled,'discrepancy':discrepancy,
            'submitted_analysis_plan':analysis_plan,'not_evaluated':GAPS+['Original notebook bootstrap and engagement Mann–Whitney test are not rerun.']}
