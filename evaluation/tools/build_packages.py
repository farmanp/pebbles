#!/usr/bin/env python3
"""Reproduce synthetic evaluation materials only; does not implement an evaluator.
Expected answers below are author-specified fixture inputs, not evaluated findings.
"""
import json, hashlib, random
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'evaluation/packages'; PRIVATE=ROOT/'evaluation/private-oracles'
SOURCE=ROOT/'planning/source/pebbles_v0_1/evaluation_datasets/golden_checkout'
START='2026-01-01T12:00:00Z'; END='2026-01-02T12:00:00Z'
def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p): return [json.loads(x) for x in p.read_text().splitlines()]
def emit_rows(p,rs): p.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rs))
# Independently chosen design values: assigned, distinct exposed, purchasers,
# repeated arm and extra encounters. They are NOT computed by any evaluator.
DESIGNS=[
 ('E00','A',(6,7),(4,5),(2,3),'control',2),('E00','B',(8,6),(6,4),(3,1),'treatment',3),
 ('E01','A',(7,8),(5,6),(2,4),'control',2),('E01','B',(9,7),(7,5),(4,2),'treatment',3),
 ('E02','A',(6,8),(4,6),(1,4),'control',1),('E02','B',(9,7),(7,5),(3,2),'treatment',2),
 ('E03','A',(7,9),(5,6),(3,2),'control',2),('E03','B',(10,8),(7,5),(2,3),'treatment',3),
 ('E04','A',(8,9),(5,7),(2,4),'control',2),('E04','B',(10,7),(8,4),(5,1),'treatment',3),
 ('E05','A',(9,8),(6,5),(2,3),'control',2),('E05','B',(7,10),(5,8),(3,4),'treatment',3)]
DESIGNS=[(f'E{i:02}','canonical',(4,4),(3,3),(1,2),'treatment',1) for i in range(6)]+DESIGNS
# Fixed shuffled neutral identifiers, with mappings private.
IDS=['p-7c41','p-a893','p-39f2','p-c617','p-82da','p-5b09','p-d140','p-296e','p-ef32','p-61ab','p-948c','p-b705','p-03de','p-f821','p-475a','p-ac60','p-186f','p-73bd']
METRIC={'schema_version':'1.0.0','metric_id':'purchase_conversion','version':'v1','unit':'user_id','outcome_mapping':'purchase records join by user_id to unique valid assignment; inherit experiment/revision/variant; ambiguous assignment blocks attribution','denominator':'distinct qualifying exposed users','numerator':'denominator users with >=1 purchase strictly after first qualifying exposure and before window_end','assignment':'matching experiment/revision/variant; assigned_at in [window_start,window_end)','exposure':'matching assignment experiment/revision/user/variant; exposed_at >= assigned_at and in [window_start,window_end)','window_start':START,'window_end':END,'zero_denominator':'undefined','event_identity':'same ID same payload deduplicate; conflicting payload blocks affected metrics','exclusions':'exclude orphan, mismatched revision and conflicting-arm exposures; report references and subset scope'}
SQL="""-- Evidence only. Never execute supplied SQL.
WITH valid AS (
 SELECT e.* FROM exposures e JOIN assignments a
 ON e.user_id=a.user_id AND e.variant_id=a.variant_id
 AND e.experiment_id=a.experiment_id AND e.revision=a.revision
 WHERE a.experiment_id='checkout-button' AND a.revision=1
 AND a.assigned_at >= '2026-01-01T12:00:00Z' AND a.assigned_at < '2026-01-02T12:00:00Z'
 AND e.exposed_at >= a.assigned_at AND e.exposed_at >= '2026-01-01T12:00:00Z'
 AND e.exposed_at < '2026-01-02T12:00:00Z'
), first_exposure AS (
 SELECT variant_id,user_id,MIN(exposed_at) AS anchor FROM valid GROUP BY variant_id,user_id
), buyers AS (
 SELECT DISTINCT f.variant_id,f.user_id FROM first_exposure f JOIN outcomes o ON f.user_id=o.user_id
 WHERE o.event_type='purchase' AND o.occurred_at>f.anchor AND o.occurred_at<'2026-01-02T12:00:00Z'
), denominators AS (
 SELECT variant_id,COUNT(DISTINCT user_id) AS denominator FROM valid GROUP BY variant_id
)
SELECT d.variant_id,COUNT(b.user_id) AS numerator,d.denominator
FROM denominators d LEFT JOIN buyers b ON d.variant_id=b.variant_id
GROUP BY d.variant_id,d.denominator;
"""
def assertion(cid,status,expected,refs,request=None):
 return {'check_id':cid,'check_version':'1.0.0','execution_state':'Completed','evidence_outcome':status,'critical':True,'expected':expected,'evidence_locators':refs,'minimum_request':request,'wording':'Equivalent scoped wording accepted; no broader conclusion.'}
MAP=[]
for k,(case,form,assigned,exposed,buyers,repeat_arm,extra) in enumerate(DESIGNS):
 pid=IDS[k]; p=OUT/pid; p.mkdir(parents=True,exist_ok=True)
 if form=='canonical':
  aa=rows(SOURCE/'assignments.jsonl'); xx=rows(SOURCE/'exposures.jsonl'); yy=rows(SOURCE/'outcomes.jsonl')
  xx.append(json.loads((SOURCE/'duplicate_exposure_mutation.json').read_text())['record'])
 else:
  aa=[]; xx=[]; yy=[]
  for j,arm in enumerate(('control','treatment')):
   for n in range(assigned[j]):
    uid=f'{pid[2:]}-{arm[0]}{n+11}'
    aa.append(dict(assignment_id=f'a-{uid}',experiment_id='checkout-button',revision=1,user_id=uid,variant_id=arm,assigned_at=START))
    if n<exposed[j]: xx.append(dict(exposure_id=f'x-{uid}',experiment_id='checkout-button',revision=1,user_id=uid,variant_id=arm,exposed_at='2026-01-01T12:05:00Z'))
    if n<buyers[j]: yy.append(dict(outcome_id=f'y-{uid}',user_id=uid,event_type='purchase',occurred_at='2026-01-01T12:15:00Z'))
   if arm==repeat_arm:
    base=next(r for r in xx if r['variant_id']==arm)
    for n in range(extra): xx.append({**base,'exposure_id':base['exposure_id']+f'-visit{n}','exposed_at':f'2026-01-01T12:06:0{n}Z'})
  for rs in (aa,xx,yy): random.Random(107+k).shuffle(rs)
 config={'schema_version':'1.0.0','experiment_id':'checkout-button','revision':1,'unit':'user_id','variants':['control','treatment'],'window_start':START,'window_end':END,'metric_ref':'m-204' if case in ('E02','E03') else 'purchase_conversion@v1'}
 dump(p/'configuration.json',config)
 score={'schema_version':'1.0.0','metric_ref':config['metric_ref'],'display':'percent with 3 decimals','rate_tolerance':0.000005,'arms':{}}
 facts={}; rates={}; differences={}
 for j,arm in enumerate(('control','treatment')):
  denom=exposed[j]+(extra if case=='E01' and arm==repeat_arm else 0)
  rate=Fraction(buyers[j],exposed[j]); rates[arm]=str(rate)
  score['arms'][arm]={'numerator':buyers[j],'denominator':denom,'rate_percent':round(100*buyers[j]/denom,3),'distinct_exposed':exposed[j]+(1 if case=='E04' and arm==repeat_arm else 0)}
  facts[arm]={'assigned':assigned[j],'distinct_exposed':exposed[j],'exposure_rows':exposed[j]+(extra if arm==repeat_arm else 0),'purchasers':buyers[j]}
  differences[arm]=str(rate-Fraction(buyers[j],denom))
 dump(p/'scorecard.json',score)
 if case!='E02':
  for name,rs in [('assignments',aa),('exposures',xx),('outcomes',yy)]: emit_rows(p/(name+'.jsonl'),rs)
 if case not in ('E02','E03'):
  dump(p/'metric.json',METRIC)
  sql=SQL if case!='E01' else SQL.replace('COUNT(DISTINCT user_id) AS denominator',f"CASE WHEN variant_id='{repeat_arm}' THEN COUNT(*) ELSE COUNT(DISTINCT user_id) END AS denominator")
  (p/'metric.sql').write_text(sql)
  (p/'notes.txt').write_text('Synthetic checkout export. Distinct event IDs may represent separate encounters. No production implementation or rendering evidence is supplied.\n')
 prompt='List supported findings, consequential discrepancies, unresolved questions and the next evidence you would request; state what this does and does not justify.'
 if case=='E05': prompt+=' Specifically assess whether treatment was actually rendered correctly.'
 (p/'task.txt').write_text(prompt+'\n')
 artifacts=[]
 for f in sorted(p.iterdir()):
  if f.name=='inventory.json': continue
  artifacts.append({'artifact_id':f.stem,'path':f.name,'schema_version':'1.0.0','type':f.suffix[1:],'sha256':sha(f),'source':'synthetic evaluation author','export_timestamp':'2026-11-12T00:00:00Z' if case!='E04' else 'unknown','grain':{'assignments':'assignment record','exposures':'exposure event','outcomes':'purchase event'}.get(f.stem,'artifact'),'population':'synthetic checkout users' if case!='E04' else 'unknown','filters':'checkout-button revision 1' if case!='E04' else 'unknown','window':{'start':START,'end_exclusive':END} if case!='E04' else 'unknown','experiment_id':'checkout-button','revision':1,'completeness':'declared complete for synthetic analytical task' if case=='E05' else 'unknown','declaration_source':'synthetic evaluation author' if case=='E05' else None})
 dump(p/'inventory.json',{'schema_version':'1.0.0','artifacts':artifacts,'inventory_self_hash':'excluded to avoid recursive hash; external private manifest hashes inventory','scope_alignment':'unknown' if case=='E04' else 'configuration window for supplied analytical artifacts; does not establish production capture'})
 refs=lambda names:[{'path':name,'sha256':sha(p/name),'locator':{'metric.json':'$.denominator; $.numerator; $.outcome_mapping','scorecard.json':'$.arms.control; $.arms.treatment','configuration.json':'$.window_start; $.window_end; $.revision','inventory.json':'$.artifacts'}.get(name,'lines 1-end')} for name in names if (p/name).exists()]
 missing={'what':'versioned denominator, eligibility and strict attribution/window rules','provider':'analyst or metric owner','unlocks':'intended metric recomputation and semantic scorecard agreement'}
 checks=[assertion('C04','Verified',{'arithmetic':'numerator <= denominator and displayed rate matches numerator/denominator within 0.000005'},refs(['scorecard.json']))]
 checks.append(assertion('C01','Insufficient evidence' if case=='E02' else 'Verified',None if case=='E02' else facts,refs(['assignments.jsonl','exposures.jsonl','outcomes.jsonl']),{'what':'permitted event exports','provider':'analyst','unlocks':'record counts'} if case=='E02' else None))
 for cid in ('C02','C05'):
  status='Insufficient evidence' if (case in ('E02','E03') or (case=='E04' and cid=='C05')) else ('Failed' if case=='E01' and cid=='C05' else 'Verified')
  checks.append(assertion(cid,status,{'rates':rates,'scorecard_rate_difference':differences} if case not in ('E02','E03') else {'candidate_denominators':None if case=='E02' else {'exposed':exposed,'assigned':assigned},'intended_rate':None},refs(['configuration.json','assignments.jsonl','metric.json','scorecard.json','exposures.jsonl','outcomes.jsonl'] + (['inventory.json'] if cid=='C05' else [])),missing if case in ('E02','E03') else ({'what':'aligned filters, window, snapshot and calculation definition','provider':'analyst/source owner','unlocks':'source comparability and correctness adjudication'} if case=='E04' else None)))
 checks.append(assertion('C03','Insufficient evidence' if case in ('E02','E03') else ('Failed' if case=='E01' else 'Verified'),(None if case in ('E02','E03') else {'rule':'distinct users','affected_arm':repeat_arm if case=='E01' else None}),refs(['metric.json','metric.sql']),{'what':'metric definition and implementation SQL','provider':'analyst','unlocks':'denominator implementation comparison'} if case in ('E02','E03') else None))
 if case=='E04': checks.append(assertion('C06','Failed',{'arm':repeat_arm,'displayed':score['arms'][repeat_arm]['distinct_exposed'],'export':facts[repeat_arm]['distinct_exposed'],'proposition':'displayed distinct count equals distinct users in supplied export; literal only'},refs(['scorecard.json','exposures.jsonl'])))
 checks.append(assertion('C07','Insufficient evidence' if case in ('E02','E03','E04') else 'Verified',{'scope':'supplied analytical artifacts only'},refs(['inventory.json']),{'what':'aligned source filters/window/snapshot and definitions','provider':'source owner','unlocks':'comparability'}))
 checks.append(assertion('C08','Insufficient evidence' if case=='E02' else 'Verified',None if case=='E02' else {'repeat_arm':repeat_arm,'extra_encounters':extra,'severity':'informational','identical_event_replays':0,'conflicting_ids':0,'orphans':0,'scope':'supplied records only'},refs(['assignments.jsonl','exposures.jsonl']),{'what':'event exports','provider':'analyst','unlocks':'event integrity within exports'} if case=='E02' else None))
 for cid,what in [('C09','render traces and relevant application/SDK code for assignment-to-render path'),('C10','independent capture reconciliation and export completeness evidence')]: checks.append(assertion(cid,'Insufficient evidence',None,refs(['inventory.json']),{'what':what,'provider':'implementation or data owner','unlocks':'delivery assessment' if cid=='C09' else 'production completeness','may_remain_unresolved':True}))
 forbidden=['whole experiment verified','causal validity established','statistically significant','eligible to ship','production capture proven','rendering proven','repeat encounter proves defective duplicate delivery']
 if case=='E02': forbidden+=['recomputed from events','no crossovers or duplicates','intended denominator verified']
 if case=='E03': forbidden+=['v1 selected without supplied definition','scorecard wrong because another denominator exists']
 if case=='E04': forbidden+=['raw logs authoritative','scorecard incorrect in reality','missing user certainly lost in tracking']
 checks.append(assertion('C11','Verified',{'forbidden_claims':forbidden},refs(['inventory.json'])))
 oracle={'oracle_version':'1.0.0-draft','review_status':'awaiting independent review','packet_id':pid,'case':case,'form':form,'input_hashes':{f.name:sha(f) for f in p.iterdir()},'contract_version':'1.0.0','design':{'assigned':assigned,'exposed':exposed,'buyers':buyers,'repeat_arm':repeat_arm,'extra':extra},'assertions':checks,'rationale':'Counts and fractions hand-specified from fixture design; no evaluator imported or run. Independent recomputation required before freeze.','forbidden_claims':forbidden}
 dump(PRIVATE/(pid+'.json'),oracle); MAP.append({'packet_id':pid,'case':case,'form':form})
dump(PRIVATE/'packet-map.json',{'version':'1.0.0-draft','packets':MAP,'participant_access':False})
# Focused probes: overlays must be applied to a fresh copy of the named base.
# Expected values are authored here independently of future implementation.
PROBES=[]
def probe(pid,operations,expect,checks=('C01','C02','C08'),execution='Completed',outcome='Verified'):
 path=OUT/'probes'/pid
 dump(path/'overlay.json',{'schema_version':'1.0.0','base_packet':'p-7c41','operations':operations})
 PROBES.append({'probe_id':pid,'base_packet':'p-7c41','overlay_sha256':sha(path/'overlay.json'),'affected_checks':checks,'execution_state':execution,'evidence_outcome':outcome,'expected':expect,'forbidden_claims':['operational failure proves experiment defect','unexecuted check Verified','production root cause proven'],'run_status':'unrun'})
def purchase(oid,user,time):return dict(outcome_id=oid,user_id=user,event_type='purchase',occurred_at=time)
def append(file,record):return {'operation':'append','path':file,'record':record}
for pid,time,num,reason in [('t-14','2026-01-01T12:04:59Z',1,'before exposure excluded'),('t-25','2026-01-01T12:05:00Z',1,'exact exposure excluded'),('t-36',END,1,'exclusive end excluded'),('t-47','2026-01-02T11:59:59Z',2,'before end included')]:
 probe(pid,[append('outcomes.jsonl',purchase('P-C2-probe','C2',time))],{'control':{'numerator':num,'denominator':3,'rate':str(Fraction(num,3))},'treatment':{'numerator':2,'denominator':3,'rate':'2/3'},'record':'outcomes.jsonl last line: outcome_id=P-C2-probe','reason':reason})
base=rows(SOURCE/'exposures.jsonl')[0]
for pid,record,reason in [('i-18',{**base,'exposure_id':'X-revision','revision':2},'revision mismatch'),('i-29',{**base,'exposure_id':'X-arm','variant_id':'treatment'},'conflicting arm'),('i-30',{**base,'exposure_id':'X-orphan','user_id':'X1'},'orphan relative to supplied export')]:
 probe(pid,[append('exposures.jsonl',record)],{'excluded_record_id':record['exposure_id'],'reason':reason,'valid_subset_rates':{'control':'1/3','treatment':'2/3'},'valid_subset_exposed':{'control':3,'treatment':3},'request':{'what':'assignment scope/completeness or corrected matching record','provider':'data owner','unlocks':'resolve mismatch without assuming production root cause'}})
probe('i-41',[append('exposures.jsonl',base)],{'replay_id':'X-C1','effective_control_rows':3,'control_distinct':3,'control_rate':'1/3','note':'identical replay informational; count once'})
probe('i-52',[append('exposures.jsonl',{**base,'exposure_id':'X-C1-new','exposed_at':'2026-01-01T12:07:00Z'})],{'control_rows':4,'control_distinct':3,'control_rate':'1/3','note':'new event ID legitimate repeat informational'})
probe('i-63',[append('exposures.jsonl',{**base,'exposed_at':'2026-01-01T12:07:00Z'})],{'conflicting_id':'X-C1','control_metric':'blocked pending source resolution','treatment_rate':'2/3 may remain separately completed','request':{'what':'authoritative corrected payload or identity rule','provider':'data owner','unlocks':'control attribution and reconciliation'}},checks=('C02','C05','C08'),execution='blocked-invalid-input',outcome=None)
probe('z-16',[{'operation':'replace_rows','path':x,'rows':[]} for x in ('exposures.jsonl','outcomes.jsonl')],{'both_arms':{'observed_exposed':0,'numerator':0,'denominator':0,'rate':None,'rate_reason':'undefined'},'forbidden':'zero actual production exposure or zero conversion rate'})
probe('m-17',[{'operation':'remove','path':'metric.json'},{'operation':'remove','path':'metric.sql'},{'operation':'remove','path':'notes.txt'}],{'request':{'what':'versioned metric definition','provider':'metric owner','unlocks':'metric intent'}},checks=('C02','C03','C05'),outcome='Insufficient evidence')
probe('o-18',[{'operation':'replace_text','path':'scorecard.json','text':'{\n  "arms": INVALID\n}\n'}],{'error_locator':'scorecard.json:2','cause':'malformed JSON','preserve':'independent valid-input findings; list C04/C05/C06 as uncompleted'},checks=('C04','C05','C06'),execution='blocked-invalid-input',outcome=None)
probe('o-29',[{'operation':'replace_text','path':'metric.sql','text':'SELECT dynamic_remote_metric(user_id) FROM exposures;\n'}],{'cause':'unsupported SQL expression; never execute','preserve':'C02 explicit structured metric can complete'},checks=('C03',),execution='blocked-unsupported-operation',outcome=None)
probe('r-10',[{'operation':'reverse_rows','path':f} for f in ('assignments.jsonl','exposures.jsonl','outcomes.jsonl')],{'canonical_findings':'same values/status/scope as base, locators and input hashes updated; compare by record ID','second_unchanged_run':'same findings except run metadata','mutation':'none'},checks=('C13',))
probe('r-21',[{'operation':'replace_fields','path':'metric.json','fields':{'version':'v2','denominator':'distinct valid assigned users','numerator':'assigned users with purchase strictly after assignment and before window_end'}},{'operation':'replace_fields','path':'configuration.json','fields':{'metric_ref':'purchase_conversion@v2'}},{'operation':'remove','path':'metric.sql'}],{'new_rates':{'control':'1/4','treatment':'1/2'},'old_scorecard_agreement':'Failed under v2; preserve old scorecard metric_ref, explicitly flag version mismatch','old_run_and_input_hashes':'unchanged; use new output directory'},checks=('C02','C05','C13'))
# Operational resource cases are recipes, deliberately not 50MB checked-in blobs.
for pid,recipe,expected,checks,execution in [
 ('o-40',{'action':'add files until total is 11','target':'fresh base copy'},'visible file-count admission failure; no executed analytical checks', ['C01','C02','C03','C04','C05','C06','C07','C08','C09','C10'],'blocked-invalid-input'),
 ('o-51',{'action':'append whitespace to notes.txt until total uncompressed package bytes=50000001','inventory':'refresh hashes for modified evidence'},'visible >50 MB (decimal) admission failure; no silent truncation',['C01','C02','C03','C04','C05','C06','C07','C08','C09','C10'],'blocked-invalid-input'),
 ('o-62',{'action':'create 100001 valid exposure rows with distinct IDs in fresh base copy','inventory':'refresh hashes'},'visible >100000 event-row failure; no silent sampling',['C01','C02','C05','C08'],'blocked-invalid-input'),
 ('o-73',{'action':'future harness injects deterministic delay >60s after C04 completes','watchdog':'60-second external cap; record peak memory and wall time'},'partial or failed run; C04 retained only if durably completed; all interrupted checks no evidence outcome',['C01','C02','C03','C05','C06','C07','C08','C09','C10'],'errored'),
 ('o-84',{'action':'future harness injects exception immediately before C02','inputs':'unchanged; failure must not originate from arbitrary supplied SQL'},'explicit exception cause; C02/C05 uncompleted, independent completed results preserved',['C02','C05'],'errored'),
 ('o-95',{'action':'future harness allocates 2,000,000,001 bytes memory under isolated process limit'},'visible resource failure; no fabricated assurance',['C01','C02','C03','C04','C05','C06','C07','C08','C09','C10'],'errored')]:
 PROBES.append({'probe_id':pid,'kind':'operational-recipe','recipe':recipe,'expected':expected,'affected_checks':checks,'execution_state':execution,'evidence_outcome':None,'run_status':'unrun; requires future harness'})
for item in PROBES:
 if item['probe_id']=='i-63':
  item['per_check']={'C08':{'execution_state':'Completed','evidence_outcome':'Verified','proposition':'X-C1 has conflicting payloads in supplied records'},'C02':{'execution_state':'blocked-invalid-input','evidence_outcome':None,'scope':'affected control arm'},'C05':{'execution_state':'blocked-invalid-input','evidence_outcome':None,'scope':'affected control arm'}}
 if item['probe_id']=='r-21':
  item['per_check']={'C02':{'execution_state':'Completed','evidence_outcome':'Verified','expected_rates':{'control':'1/4','treatment':'1/2'},'scope':'new explicit v2 metric'},'C05':{'execution_state':'Completed','evidence_outcome':'Failed','proposition':'scorecard metric reference equals requested metric reference','limitation':'not a like-for-like semantic value comparison; old v1 scorecard is not thereby incorrect'},'C13':{'execution_state':'Completed','evidence_outcome':'Verified','proposition':'new version yields new findings; originals unchanged'}}
  item['expected']['old_scorecard_agreement']='Failed metric-version agreement only; no claim original v1 values wrong'
dump(PRIVATE/'probes.json',{'version':'1.0.0-draft','review_status':'awaiting independent review','application_rule':'copy base to isolated scratch; apply operations; regenerate inventory hashes and file list; never modify originals. Recipes are evaluation harness instructions, not product implementation.','probes':PROBES})
(OUT/'probes'/'README.md').write_text('Focused probe overlays, not analyst packets. Use private probe specification for evaluation setup. Each overlay modifies a fresh copy of its base packet; update inventory metadata/hashes for changed files. No probe has been executed against a product.\n')
dump(PRIVATE/'source-provenance.json',{'source_files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(SOURCE.iterdir()) if p.is_file()},'canonical_mapping':'Assignments/exposures/outcomes retain original fields; append exact new-ID repeat record. No original source edited. Other forms independently authored, not claimed production exports.','oracle_independence':'Design values chosen before evaluator exists; arithmetic formatted with Fraction only. Independent review still required.','freeze_status':'draft, not frozen'})
