"""Build synthetic fixed-horizon assigned-user examples; these are not customer results."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).parent
for name,treatment_purchases in [('benefit',520),('uncertain',412),('harm',280)]:
    folder=OUT/name;folder.mkdir(exist_ok=True)
    config={'schema_version':'1.0.0','experiment_id':'checkout-button','revision':1,'unit':'user_id',
            'variants':['control','treatment'],'metric_ref':'purchase_conversion@v2',
            'window_start':'2026-01-01T12:00:00Z','window_end':'2026-01-02T12:00:00Z',
            'analysis_plan':{'schema_version':'1.0.0','control':'control','treatment':'treatment','minimum_effect_pp':1.0,'expected_treatment_share':.5,'predeclared':True,'randomized_independent':True,'window_complete':True,'complete_assigned_outcomes':True}}
    metric=json.loads((ROOT/'evaluation/packages/p-7c41/metric.json').read_text())
    metric.update(version='v2',denominator='distinct valid assigned users',numerator='assigned users with purchase strictly after assignment and before window_end')
    arms={a:{'numerator':n,'denominator':2000,'distinct_exposed':2000,'rate_percent':round(100*n/2000,3)} for a,n in [('control',400),('treatment',treatment_purchases)]}
    score={'schema_version':'1.0.0','metric_ref':'purchase_conversion@v2','display':'percent with 3 decimals','rate_tolerance':.000005,'arms':arms}
    for file,obj in [('configuration.json',config),('metric.json',metric),('scorecard.json',score)]:
        (folder/file).write_text(json.dumps(obj,indent=2)+'\n')
    assignments=[];exposures=[];outcomes=[]
    for arm,buyers in [('control',400),('treatment',treatment_purchases)]:
        for i in range(2000):
            uid=f'{arm}-{i}'
            shared={'experiment_id':'checkout-button','revision':1,'user_id':uid,'variant_id':arm}
            assignments.append(dict(shared,assignment_id='A-'+uid,assigned_at='2026-01-01T12:00:00Z'))
            exposures.append(dict(shared,exposure_id='X-'+uid,exposed_at='2026-01-01T12:05:00Z'))
            if i<buyers: outcomes.append({'outcome_id':'P-'+uid,'user_id':uid,'event_type':'purchase','occurred_at':'2026-01-01T13:00:00Z'})
    for file,rows in [('assignments.jsonl',assignments),('exposures.jsonl',exposures),('outcomes.jsonl',outcomes)]:
        (folder/file).write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows))
    (folder/'notes.txt').write_text('Synthetic demonstration with fixed assigned-user counts. Design assumptions and threshold are declared in configuration.json; they are not independently verified production facts. No guardrail observations are supplied.\n')
    artifacts=[]
    for p in sorted(folder.iterdir()):
        if p.name=='inventory.json':continue
        artifacts.append({'artifact_id':p.stem,'path':p.name,'type':p.suffix[1:],'schema_version':'1.0.0','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':'synthetic fixed-horizon example','export_timestamp':'2026-01-03T00:00:00Z','grain':'user event' if p.suffix=='.jsonl' else 'artifact','population':'all assigned synthetic checkout users','filters':'checkout-button revision 1','window':{'start':config['window_start'],'end_exclusive':config['window_end']},'experiment_id':'checkout-button','revision':1,'completeness':'declared','declaration_source':'synthetic example specification'})
    (folder/'inventory.json').write_text(json.dumps({'schema_version':'1.0.0','artifacts':artifacts,'scope_alignment':'declared fixed analytical scope'},indent=2)+'\n')
