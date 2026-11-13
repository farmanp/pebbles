"""Controlled examples; recipes and expectations are kept outside investigation packets."""
import csv, hashlib, io, json, shutil
from pathlib import Path
ROOT=Path(__file__).parent
base=ROOT/'packet';raw=(base/'cookie_cats.csv').read_text()
rows=list(csv.DictReader(io.StringIO(raw)))
expected={}
for name in ('clean','denominator','missing-users','wrong-metric'):
    folder=ROOT/'cases'/name;folder.mkdir(parents=True,exist_ok=True)
    for p in base.iterdir():shutil.copyfile(p,folder/p.name)
    (folder/'reference.csv').write_text(raw)
    supplied=rows
    if name=='missing-users':
        gone={r['userid'] for r in [r for r in rows if r['version']=='gate_40' and r['retention_7']=='FALSE'][:5000]}
        supplied=[r for r in rows if r['userid'] not in gone]
        with (folder/'cookie_cats.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(supplied)
    metric='retention_1' if name=='wrong-metric' else 'retention_7'
    counts={label:{'retained_users':sum(r[metric]=='TRUE' for r in supplied if r['version']==arm),'users':sum(r['version']==arm for r in supplied)} for label,arm in [('control','gate_30'),('treatment','gate_40')]}
    if name=='denominator':counts['control']['users']=60000
    spec={'schema_version':'1.0.0','controlled_exercise':True,'metric':'retention_7','reported':counts,
          'population_claim':'All supplied users','notice':'Controlled exercise generated from public data. This reported summary is not the original analyst readout.'}
    (folder/'investigation.json').write_text(json.dumps(spec,indent=2)+'\n')
    (folder/'notes.txt').write_text('Controlled exercise based on public Cookie Cats data. The original analyst notebook and transcribed readout remain unchanged. investigation.json is a separate exercise claim. reference.csv is an explicitly supplied reference, not proof of production completeness.\n')
    artifacts=[{'artifact_id':p.stem,'path':p.name,'type':p.suffix[1:],'schema_version':'1.0.0','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':'controlled Cookie Cats exercise; original public reference preserved'} for p in sorted(folder.iterdir()) if p.name!='inventory.json']
    (folder/'inventory.json').write_text(json.dumps({'schema_version':'1.0.0','artifacts':artifacts},indent=2)+'\n')
    expected[name]={'diagnosis':{'clean':'agreement','denominator':'denominator_mismatch','missing-users':'population_mismatch','wrong-metric':'metric_mismatch'}[name], 'conclusion_changed':name!='clean'}
(ROOT.parents[1]/'evaluation/discrepancy/expected.json').write_text(json.dumps(expected,indent=2)+'\n')
