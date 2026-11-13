#!/usr/bin/env python3
"""Independent materials audit; not a Pebbles evaluator or product gate runner."""
import json, hashlib, re, sys, tempfile, shutil, csv
from pathlib import Path
from datetime import datetime
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[1]
errors=[]; checks=0; results=[]
def check(ok,msg):
 global checks
 checks+=1
 if not ok: errors.append(msg)
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p): return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def stamp(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
def recompute(folder):
 """Per-user relational reconstruction, using time objects and exact fractions."""
 cfg=read(folder/'configuration.json'); lo=stamp(cfg['window_start']); hi=stamp(cfg['window_end'])
 raw={k:rows(folder/(k+'.jsonl')) for k in ('assignments','exposures','outcomes')}
 unique={}; conflicts=[]; replays=0
 for kind,events in raw.items():
  key={'assignments':'assignment_id','exposures':'exposure_id','outcomes':'outcome_id'}[kind]
  groups={}
  for event in events: groups.setdefault(event[key],[]).append(event)
  unique[kind]=[]
  for id,group in groups.items():
   variants={json.dumps(e,sort_keys=True) for e in group}
   if len(variants)>1: conflicts.append(id)
   else: unique[kind].append(group[0]); replays+=len(group)-1
 users={}
 for a in unique['assignments']:
  if a['experiment_id']==cfg['experiment_id'] and a['revision']==cfg['revision'] and a['variant_id'] in cfg['variants'] and lo<=stamp(a['assigned_at'])<hi:
   users.setdefault(a['user_id'],[]).append(a)
 stats={}; excluded=[]
 for arm in cfg['variants']:
  assigned=[]; exposed=[]; buyers=[]; v2buyers=[]; nrows=0
  for user,aa in users.items():
   if len(aa)!=1: continue
   a=aa[0]
   if a['variant_id']!=arm: continue
   assigned.append(user)
   events=[e for e in unique['exposures'] if e['user_id']==user and all(e[f]==a[f] for f in ('experiment_id','revision','variant_id')) and lo<=stamp(e['exposed_at'])<hi and stamp(e['exposed_at'])>=stamp(a['assigned_at'])]
   purchases=[o for o in unique['outcomes'] if o['user_id']==user and o['event_type']=='purchase']
   if any(stamp(a['assigned_at'])<stamp(o['occurred_at'])<hi for o in purchases):v2buyers.append(user)
   if events:
    exposed.append(user); nrows+=len(events); anchor=min(stamp(e['exposed_at']) for e in events)
    if any(anchor<stamp(o['occurred_at'])<hi for o in purchases):buyers.append(user)
  stats[arm]={'assigned':len(assigned),'distinct_exposed':len(exposed),'exposure_rows':nrows,'purchasers':len(buyers),'v2_purchasers':len(v2buyers),'rate':str(Fraction(len(buyers),len(exposed))) if exposed else None,'v2_rate':str(Fraction(len(v2buyers),len(assigned))) if assigned else None}
 return stats,conflicts,replays

def audit_packet(entry):
 p=ROOT/'packages'/entry['packet_id']; o=read(ROOT/'private-oracles'/(p.name+'.json')); inv=read(p/'inventory.json'); assertions={a['check_id']:a for a in o['assertions']}
 files={x.name for x in p.iterdir() if x.is_file()}
 check(files==set(o['input_hashes']),p.name+' private hash coverage')
 check(files=={a['path'] for a in inv['artifacts']}|{'inventory.json'},p.name+' inventory coverage')
 check(len(files)<=10,p.name+' file envelope')
 for name,h in o['input_hashes'].items():check(sha(p/name)==h,p.name+' hash '+name)
 for a in inv['artifacts']:check(sha(p/a['path'])==a['sha256'],p.name+' inventory hash '+a['path'])
 for a in o['assertions']:
  for ref in a['evidence_locators']:check(sha(p/ref['path'])==ref['sha256'],p.name+' evidence locator hash')
 for f in p.iterdir():
  check(not f.is_symlink(),p.name+' symlink isolation')
  check(not re.search(r'\bE0[0-5]\b|private-oracle|forbidden_claim|intended defect',f.read_text(),re.I),p.name+' text leakage '+f.name)
 case=entry['case']
 check(('metric.json' in files)==(case not in ('E02','E03')),p.name+' definition withholding')
 check(('assignments.jsonl' in files)==(case!='E02'),p.name+' events withholding')
 check(('metric.sql' in files)==(case not in ('E02','E03')),p.name+' SQL withholding')
 sc=read(p/'scorecard.json')
 for arm,s in sc['arms'].items():
  check(0<=s['numerator']<=s['denominator'],p.name+' scorecard bounds')
  check(abs(Fraction(str(s['rate_percent']))/100-Fraction(s['numerator'],s['denominator']))<=Fraction(5,1000000),p.name+' arithmetic '+arm)
 if case!='E02':
  stats,conflicts,replays=recompute(p)
  for arm,s in stats.items():
   for field,value in assertions['C01']['expected'][arm].items():check(s[field]==value,p.name+' record '+arm+' '+field)
   if case!='E03':
    exp=assertions['C02']['expected']; check(s['rate']==exp['rates'][arm],p.name+' rate '+arm)
    delta=Fraction(s['rate'])-Fraction(sc['arms'][arm]['numerator'],sc['arms'][arm]['denominator'])
    check(str(delta)==exp['scorecard_rate_difference'][arm],p.name+' discrepancy '+arm)
  if case=='E04':
   e=assertions['C06']['expected'];check(sc['arms'][e['arm']]['distinct_exposed']==e['displayed'] and stats[e['arm']]['distinct_exposed']==e['export'] and e['displayed']!=e['export'],p.name+' literal conflict')
  if case not in ('E03',):
   for cid in ('C02','C05'):
    dependencies={r['path'] for r in assertions[cid]['evidence_locators']}
    check({'assignments.jsonl','configuration.json','metric.json','exposures.jsonl','outcomes.jsonl'}<=dependencies,p.name+' '+cid+' semantic dependencies')
   check('inventory.json' in {r['path'] for r in assertions['C05']['evidence_locators']},p.name+' reconciliation provenance dependency')
   sql=(p/'metric.sql').read_text()
   check('COUNT(DISTINCT user_id)' in sql,p.name+' SQL distinct rule')
   check(('THEN COUNT(*)' in sql)==(case=='E01'),p.name+' SQL planted row-count branch')
  check(assertions['C05']['evidence_outcome']==({'E01':'Failed','E03':'Insufficient evidence','E04':'Insufficient evidence'}.get(case,'Verified')),p.name+' semantic status')
  results.append({'packet':p.name,'case':case,'form':entry['form'],'recomputed':stats})
 if case=='E02':results.append({'packet':p.name,'case':case,'form':entry['form'],'recomputed':None,'scope':'scorecard arithmetic only; no event exports or intended metric supplied','scorecard':sc['arms']})
 for id in ('C09','C10'):check(assertions[id]['evidence_outcome']=='Insufficient evidence',p.name+' boundary '+id)
 check(bool(o['forbidden_claims']),p.name+' forbidden claims')

entries=read(ROOT/'private-oracles/packet-map.json')['packets']
check(len(entries)==18,'18 packets')
check({(e['case'],e['form']) for e in entries}=={('E0'+str(i),f) for i in range(6) for f in ('canonical','A','B')},'complete case-form cross product')
for entry in entries:audit_packet(entry)
# Apply declarative overlays in disposable copies only; never execute supplied SQL.
probes=read(ROOT/'private-oracles/probes.json')['probes']
check(len(probes)==22,'22 focused probes/recipes')
probe_results=[]
for probe in probes:
 id=probe['probe_id']; expected=probe['expected']
 check(bool(probe['affected_checks']),id+' affected checks')
 if probe.get('kind')=='operational-recipe':
  check(probe['evidence_outcome'] is None,id+' nonexecution no evidence outcome')
  check('unrun' in probe['run_status'],id+' recipe unrun')
  probe_results.append({'probe':id,'review':'recipe inspected, not executed'})
  continue
 overlay_path=ROOT/'packages/probes'/id/'overlay.json'
 check(sha(overlay_path)==probe['overlay_sha256'],id+' overlay hash')
 overlay=read(overlay_path); base=ROOT/'packages'/overlay['base_packet']
 before={p.name:sha(p) for p in base.iterdir()}
 with tempfile.TemporaryDirectory(prefix='pebbles-independent-') as tmp:
  folder=Path(tmp)/'packet';shutil.copytree(base,folder)
  for op in overlay['operations']:
   target=folder/op['path']; action=op['operation']
   if action=='append': target.write_text(target.read_text()+json.dumps(op['record'])+'\n')
   elif action=='remove':target.unlink()
   elif action=='replace_fields':
    data=read(target);data.update(op['fields']);target.write_text(json.dumps(data))
   elif action=='replace_rows':target.write_text(''.join(json.dumps(r)+'\n' for r in op['rows']))
   elif action=='replace_text':target.write_text(op['text'])
   elif action=='reverse_rows':target.write_text('\n'.join(reversed(target.read_text().splitlines()))+'\n')
   else:check(False,id+' unknown operation '+action)
  stats,conflicts,replays=recompute(folder)
  if id.startswith('t-'):
   for arm in ('control','treatment'):
    for field,actual in [('denominator','distinct_exposed'),('numerator','purchasers'),('rate','rate')]:check(stats[arm][actual]==expected[arm][field],id+' '+arm+' '+field)
  if id in ('i-18','i-29','i-30'):
   for arm in ('control','treatment'):
    check(stats[arm]['distinct_exposed']==expected['valid_subset_exposed'][arm],id+' excluded count '+arm)
    check(stats[arm]['rate']==expected['valid_subset_rates'][arm],id+' subset rate '+arm)
  if id in ('i-41','i-52'):
   check(stats['control']['distinct_exposed']==expected['control_distinct'],id+' distinct')
   check(stats['control']['rate']==expected['control_rate'],id+' rate')
   check(stats['control']['exposure_rows']==expected.get('effective_control_rows',expected.get('control_rows')),id+' effective rows')
   check(replays==(1 if id=='i-41' else 0),id+' replay versus repeat')
  if id=='i-63':
   check(conflicts==[expected['conflicting_id']],id+' conflict ID')
   check(stats['treatment']['rate']=='2/3',id+' unaffected treatment')
   check('per_check' in probe,id+' per-check operational distinction')
  if id=='z-16':
   for arm in stats:check(stats[arm]['distinct_exposed']==stats[arm]['purchasers']==0 and stats[arm]['rate'] is None,id+' undefined '+arm)
  if id=='m-17':check(not any((folder/f).exists() for f in ('metric.json','metric.sql','notes.txt')),id+' no backdoor metric')
  if id=='o-18':
   try: read(folder/'scorecard.json');check(False,id+' parse should fail')
   except json.JSONDecodeError as e:check(e.lineno==2,id+' error line')
  if id=='o-29':check('dynamic_remote_metric' in (folder/'metric.sql').read_text(),id+' unsupported expression material')
  if id=='r-10':check(recompute(base)==recompute(folder),id+' independent reordered reconstruction')
  if id=='r-21':
   for arm in stats:check(stats[arm]['v2_rate']==expected['new_rates'][arm],id+' v2 '+arm)
   check(read(folder/'metric.json')['version']=='v2' and read(folder/'scorecard.json')['metric_ref'].endswith('@v1'),id+' visible version mismatch')
   check('per_check' in probe,id+' version check status separated')
  probe_results.append({'probe':id,'review':'overlay inspected and independently reconstructed','conflicts':conflicts,'replays':replays})
 check(before=={p.name:sha(p) for p in base.iterdir()},id+' originals unchanged')
# Freeze schedule mechanics; difficulty equivalence remains a separate human test.
schedule=list(csv.DictReader((ROOT/'study/private/schedule.csv').open()))
check(len(schedule)==12,'12 workflow tasks')
for row in range(1,7):
 pair=[s for s in schedule if s['schedule_row']==str(row)]
 check(len(pair)==2 and {s['method'] for s in pair}=={'N','P'},'schedule methods '+str(row))
 check(len({s['condition'] for s in pair})==2 and len({s['form'] for s in pair})==2,'no counterpart reuse '+str(row))
check(sum(s['method']=='N' and s['task_order']=='1' for s in schedule)==3,'order balanced')
check({(s['condition'],s['form']) for s in schedule}=={('E0'+str(i),f) for i in range(6) for f in ('A','B')},'all workflow forms used once')
for condition in ('E0'+str(i) for i in range(6)):check({s['method'] for s in schedule if s['condition']==condition}=={'N','P'},condition+' both methods')
rubric=read(ROOT/'contracts/scoring-rubric.json')
check(rubric['gates']['R2']['scope_expected_denominator']==28,'28 scope questions')
check(rubric['rate_tolerance']['absolute_inclusive']==0.000005,'percentage rounding converted to rate')
check(all(g['current_status']=='Not yet evaluated' for g in rubric['gates'].values()),'product/human gates unrun')
for entry in entries:
 if entry['form']=='A':
  other=next(e for e in entries if e['case']==entry['case'] and e['form']=='B')
  a=read(ROOT/'private-oracles'/(entry['packet_id']+'.json'))['design']
  b=read(ROOT/'private-oracles'/(other['packet_id']+'.json'))['design']
  check(a!=b,entry['case']+' A/B numerical designs differ')
output={'scope':'materials only; not product execution or human difficulty validation','assertions':checks,'failures':errors,'packets':results,'probes':probe_results}
(ROOT/'verification/audit-results.json').write_text(json.dumps(output,indent=2)+'\n')
print(f'{checks} assertions; {len(entries)} packets; {len(errors)} failures')
for e in errors:print('FAIL:',e)
sys.exit(bool(errors))
