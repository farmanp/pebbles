"""Independent CSV/count and packaging audit; no participant outcomes."""
import csv
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
ROOT = KIT.parents[1]
checks = 0
for folder in sorted((KIT/'packets').iterdir()):
    key = json.loads((KIT/'facilitator/keys'/f'{folder.name}.json').read_text())
    data = {}
    for filename, keyname in [('reference.csv','reference_counts'), ('cookie_cats.csv','supplied_counts')]:
        rows = list(csv.DictReader((folder/'evidence'/filename).open()))
        data[filename] = {r['userid']: r for r in rows}
        assert len(data[filename]) == len(rows)
        for arm, version in [('control','gate_30'), ('treatment','gate_40')]:
            selected = [r for r in rows if r['version'] == version]
            counts = {'users':len(selected), 'retained_users':sum(r['retention_7'].lower()=='true' for r in selected)}
            assert counts == key[keyname][arm], (folder.name,keyname,arm)
            checks += 1
    assert len(data['reference.csv'].keys()-data['cookie_cats.csv'].keys()) == key['expected_missing_users']
    claim=json.loads((folder/'evidence/investigation.json').read_text())
    assert claim['reported']==key['reported_counts']
    for prefix in ['reference','reported']:
        c=key[prefix+'_counts']
        delta=100*(c['treatment']['retained_users']/c['treatment']['users']-c['control']['retained_users']/c['control']['users'])
        assert abs(delta-key[prefix+'_difference_pp'])<1e-10
    with zipfile.ZipFile(KIT/'distribute'/f'{folder.name}.zip') as z:
        expected={str(Path(folder.name)/f.relative_to(folder)):f for f in folder.rglob('*') if f.is_file()}
        assert set(z.namelist()) == set(expected)
        for name,f in expected.items(): assert z.read(name)==f.read_bytes()
    checks += 4
schedule=json.loads((KIT/'facilitator/schedule.json').read_text())
for n in [4,6]:
    rows=[r for r in schedule if r['session_id'] in [f'S{i:02}' for i in range(1,n+1)]]
    for session in {r['session_id'] for r in rows}:
        selected=[r for r in rows if r['session_id']==session]
        assert len({r['family'] for r in selected})==4
        assert Counter(r['condition'] for r in selected)=={'Usual':2,'Pebbles':2}
    counts=Counter((r['family'],r['condition']) for r in rows)
    assert set(counts.values())=={n//2}
    checks+=1
files=list((KIT/'packets').rglob('*'))+list((KIT/'facilitator').rglob('*'))+list((KIT/'participant').rglob('*'))+list((KIT/'tools').glob('*.py'))+[KIT/'README.md']+list((ROOT/'pebbles').rglob('*.py'))+list((ROOT/'pebbles/static').glob('*'))
manifest={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files if f.is_file()}
(KIT/'verification/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(KIT/'verification/audit.json').write_text(json.dumps({'status':'Technical audit only; no participant sessions run','assertion_groups':checks,'packets':11,'scope':'Independent CSV counts, differences, missing IDs, ZIP bytes and schedule balance. Does not independently validate interval methodology or participant difficulty.'},indent=2)+'\n')
print(f'Passed {checks} assertion groups. No participant results.')
