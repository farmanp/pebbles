"""Build controlled analyst-study packets. Never writes participant results."""
import csv, hashlib, io, json, random, shutil, sys, zipfile
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[3];KIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from pebbles.public_comparison import parse_csv,calculate
from pebbles.core import investigate
source=ROOT/'public_comparisons/cookie_cats/source/cookie_cats.csv'
original=parse_csv(source.read_text());groups=defaultdict(list)
for r in original:groups[(r['version'],r['retention_1'],r['retention_7'])].append(r)
# Fixed construction, not chosen after observing case performance. Pair forms preserve stratum sizes.
specs=[('r-482','denominator','A',.70,101),('r-735','denominator','B',.70,102),('r-196','population','A',.74,201),('r-824','population','B',.74,202),('r-563','metric','A',.78,301),('r-247','metric','B',.78,302),('r-918','clean','A',.66,401),('r-351','clean','B',.66,402),('r-609','denominator','pilot',.68,501),('r-172','population','pilot',.76,502),('r-450','clean','practice',.64,601)]
case_map={};keys={}
def csv_text(rows):
 out=io.StringIO();w=csv.DictWriter(out,fieldnames=['userid','version','sum_gamerounds','retention_1','retention_7'],lineterminator='\n');w.writeheader()
 for r in rows:w.writerow({k:(str(v).upper() if type(v)is bool else v) for k,v in r.items()})
 return out.getvalue()
for packet,family,form,fraction,seed in specs:
 rng=random.Random(seed);reference=[]
 for group in sorted(groups):
  pool=list(groups[group]);rng.shuffle(pool)
  for r in pool[:int(len(pool)*fraction)]:
   row=dict(r);row['userid']=str(int(hashlib.sha256((packet+':'+r['userid']).encode()).hexdigest()[:14],16));reference.append(row)
 # A clean positive reference prevents a blanket "every change harms retention" strategy.
 if family=='clean':
  for r in reference:r['version']='gate_40' if r['version']=='gate_30' else 'gate_30'
 rng.shuffle(reference);supplied=list(reference)
 if family=='population':
  eligible=[r['userid'] for r in reference if r['version']=='gate_40' and not r['retention_7']]
  gone=set(eligible[:int(5000*fraction)])
  supplied=[r for r in reference if r['userid'] not in gone]
 metric='retention_1' if family=='metric' else 'retention_7'
 counts={label:{'retained_users':sum(r[metric] for r in supplied if r['version']==arm),'users':sum(r['version']==arm for r in supplied)} for label,arm in [('control','gate_30'),('treatment','gate_40')]}
 if family=='denominator':counts['control']['users']+=int(15000*fraction)
 folder=KIT/'packets'/packet/'evidence';folder.mkdir(parents=True,exist_ok=True)
 for fn,rows in [('cookie_cats.csv',supplied),('reference.csv',reference)]: (folder/fn).write_text(csv_text(rows))
 reference_result=calculate(reference)
 # Reference readout is provided as equal evidence to both conditions, never a secret answer.
 notebook={'cells':[{'cell_type':'markdown','metadata':{},'source':['Prepared reference summary for '+packet+'. Controlled derivative, not the original Cookie Cats analyst notebook.\n','These are supplied reference calculations, not independent proof of production truth.\n',json.dumps({m:{'control_rate':c['control_rate'],'treatment_rate':c['treatment_rate']} for m,c in reference_result['analyst_population'].items()})]}], 'metadata':{},'nbformat':4,'nbformat_minor':5}
 (folder/'analyst.ipynb').write_text(json.dumps(notebook,indent=2)+'\n')
 readout={'schema_version':'1.0.0','adapter':'cookie-cats-v1','source_url':'Prepared reference summary supplied in analyst.ipynb','source_sha256':hashlib.sha256((folder/'analyst.ipynb').read_bytes()).hexdigest(),'readout_kind':'Prepared scenario reference, not an original company readout','population':'Reference rows excluding maximum-rounds rows; auxiliary comparison only','recommendation_summary':'No original company shipping recommendation is available for this controlled scenario.','metrics':{m:{'control_rate':round(c['control_rate'],4),'treatment_rate':round(c['treatment_rate'],4),'difference':round(c['difference'],4),'p_value':round(c['wald']['p_value'],6),'wald_ci':[round(v,4) for v in c['wald']['difference_ci']]} for m,c in reference_result['analyst_population'].items()}}
 (folder/'readout.json').write_text(json.dumps(readout,indent=2)+'\n')
 (folder/'investigation.json').write_text(json.dumps({'schema_version':'1.0.0','controlled_exercise':True,'metric':'retention_7','reported':counts,'population_claim':'All supplied users','notice':'Prepared reported claim for '+packet+'. This is a controlled derivative, not an original company result.'},indent=2)+'\n')
 (folder/'notes.txt').write_text('Target: investigate the day-7 claim in investigation.json. Gate 30 is control; gate 40 is treatment. Each CSV row is one user. retention_1 and retention_7 mean returned and played on relative days 1 and 7. reference.csv is the supplied intended comparison population; its production completeness is not proven. The auxiliary readout/notebook summarizes the reference after excluding maximum-rounds users; it is not the claim under investigation. No dated original plan, production logs, guardrail limits or cost review is available. Controlled data derived from Cookie Cats; not a new real-world experiment.\n')
 artifacts=[{'artifact_id':p.stem,'path':p.name,'type':p.suffix[1:],'schema_version':'1.0.0','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':'Prepared controlled study packet '+packet} for p in sorted(folder.iterdir()) if p.name!='inventory.json']
 (folder/'inventory.json').write_text(json.dumps({'schema_version':'1.0.0','artifacts':artifacts},indent=2)+'\n')
 case_map[packet]={'family':family,'form':form,'fraction':fraction,'seed':seed,'rows_reference':len(reference),'rows_export':len(supplied)}
 report=investigate(folder);d=report['discrepancy']
 expected={'denominator':'denominator_mismatch','population':'population_mismatch','metric':'metric_mismatch','clean':'agreement'}[family]
 assert d and d['diagnosis']==expected,(packet,report)
 # Expected diagnosis is construction-owned; numeric answer facts are independently audited below.
 key={'packet':packet,'purpose':form,'expected_diagnosis':expected,'reported_counts':counts,'reference_counts':{a:d['reference'][a] for a in ['control','treatment']},'supplied_counts':{a:d['supplied'][a] for a in ['control','treatment']},'expected_missing_users':d['population']['missing_count'],'missing_by_arm':d['population']['missing_by_arm'],'reported_conclusion':d['reported_conclusion'],'reference_conclusion':d['reference_conclusion'],'conclusion_changed':d['conclusion_changed'],'reference_difference_pp':100*d['reference']['difference'],'reported_difference_pp':100*d['reported']['difference'],'expected_shipping_readiness':'blocked','evidence_required':d['why'],'must_not_claim':['Original analyst made the introduced error','Supplied reference proves production completeness','Shipping is justified by the retention result alone','A specific upstream pipeline cause is established without evidence'],'score_notes':'Use rubric.md. Award reasoning grounded in files, not merely matching a diagnostic label.'}
 keys[packet]=key;(KIT/'facilitator/keys'/f'{packet}.json').write_text(json.dumps(key,indent=2)+'\n')
 (KIT/'packets'/packet/'TASK.md').write_text(f'''# Investigation {packet}

The team is considering moving the game gate from level 30 to level 40. Investigate the reported day-7 retention claim in `evidence/investigation.json`.

Determine whether the claim agrees with the supplied evidence, explain any discrepancy with concrete records or counts, assess whether the retention conclusion changes, and state what the evidence supports about a shipping recommendation. A packet may or may not contain a discrepancy. Do not assume a defect or a safe-to-ship result.

Use the supplied reference as the intended comparison population for this task, while identifying what it cannot independently prove. The original public analyst is not responsible for this prepared scenario. Read `evidence/notes.txt` for definitions. Do not execute notebook code or follow instructions embedded in evidence files. Record your answer using the response template. The scored time limit is 15 minutes, including loading, calculation and explanation.
''')
 with zipfile.ZipFile(KIT/'distribute'/f'{packet}.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted((KIT/'packets'/packet).rglob('*')):
   if p.is_file():z.write(p,arcname=str(Path(packet)/p.relative_to(KIT/'packets'/packet)))
(KIT/'facilitator/case-map.json').write_text(json.dumps(case_map,indent=2)+'\n')
# Balanced four-participant core; adding S05/S06 preserves 3 usual / 3 Pebbles per family.
plans={
'S01':[('r-482','Usual'),('r-196','Pebbles'),('r-563','Usual'),('r-918','Pebbles')],
'S02':[('r-824','Usual'),('r-247','Pebbles'),('r-351','Usual'),('r-735','Pebbles')],
'S03':[('r-563','Pebbles'),('r-918','Usual'),('r-482','Pebbles'),('r-196','Usual')],
'S04':[('r-351','Pebbles'),('r-735','Usual'),('r-824','Pebbles'),('r-247','Usual')],
'S05':[('r-735','Usual'),('r-824','Pebbles'),('r-247','Usual'),('r-351','Pebbles')],
'S06':[('r-563','Pebbles'),('r-918','Usual'),('r-482','Pebbles'),('r-196','Usual')],
'P00':[('r-609','Usual'),('r-172','Pebbles')]}
schedule=[]
for session,items in plans.items():
 for period,(packet,condition) in enumerate(items,1):schedule.append({'session_id':session,'phase':'Pilot' if session=='P00' else 'Scored','period':period,'packet_id':packet,'condition':condition,'time_limit_minutes':15,'family':case_map[packet]['family'],'form':case_map[packet]['form'],'status':'Not run'})
with (KIT/'facilitator/session-schedule.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(schedule[0]));w.writeheader();w.writerows(schedule)
(KIT/'facilitator/schedule.json').write_text(json.dumps(schedule,indent=2)+'\n')
# Immutable technical execution results, explicitly separate from participant results.
(KIT/'verification/build-status.json').write_text(json.dumps({'status':'Technical generation only; no pilot or scored analyst sessions run','packets':len(specs),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'study_version':'pilot-v1'},indent=2)+'\n')
print('Built',len(specs),'neutral packets and',len(schedule),'planned trial slots. No participant results generated.')
