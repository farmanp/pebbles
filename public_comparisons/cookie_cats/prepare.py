"""Build a hash-pinned public snapshot packet without inventing temporal evidence.
Download files from the URLs in provenance.json before running this script again.
The analyst notebook is inspected as data, never executed.
"""
import hashlib
import json
from pathlib import Path
import shutil
from datetime import datetime,timezone
ROOT=Path(__file__).parent
source=ROOT/'source';packet=ROOT/'packet';packet.mkdir(exist_ok=True)
commit='9dc979bb7cb7fe82755eddc03e738a927d76b7c7'
base=f'https://raw.githubusercontent.com/nsy0079/cookie-cats-ab-test/{commit}/'
urls={'cookie_cats.csv':base+'data/cookie_cats.csv','analyst.ipynb':base+'cookie_cats_ab_test.ipynb','analyst-readme.md':base+'README.md'}
provenance={'retrieved_at':datetime.now(timezone.utc).isoformat(),'repository':'https://github.com/nsy0079/cookie-cats-ab-test','commit':commit,
 'source_type':'Independent public portfolio analysis and mirrored dataset; not original company decision record.',
 'upstream_dataset':'https://www.kaggle.com/datasets/mursideyarkin/mobile-games-ab-testing-cookie-cats',
 'license_note':'Mirror has no repository license; upstream dataset terms were not independently established. Files retained locally for the requested comparison, not published or relicensed.',
 'files':{n:{'url':u,'sha256':hashlib.sha256((source/n).read_bytes()).hexdigest(),'bytes':(source/n).stat().st_size} for n,u in urls.items()},
 'candidate_selection':{'Cookie Cats':'90,189 user records, two arms and binary retention with notebook and explicit exclusion policy. Fits a bounded snapshot replay.',
 'Marketing AB':'588,101 records exceeds current row admission limit; weaker direct provenance.',
 'Criteo':'Millions of rows and nonuniform subsampling; original experiment lift cannot be recovered from the public release.'}}
(ROOT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
shutil.copyfile(source/'cookie_cats.csv',packet/'cookie_cats.csv')
shutil.copyfile(source/'analyst.ipynb',packet/'analyst.ipynb')
readout={'schema_version':'1.0.0','adapter':'cookie-cats-v1','source_url':f'https://github.com/nsy0079/cookie-cats-ab-test/blob/{commit}/cookie_cats_ab_test.ipynb',
 'source_sha256':provenance['files']['analyst.ipynb']['sha256'],'readout_kind':'Independent portfolio notebook, not original company readout',
 'source_cells':{'exclusion':11,'srm':23,'rates_z_test_wald_ci':26},'cell_indexing':'zero-based notebook cell indices',
 'population':'Drop every row whose sum_gamerounds equals the dataset maximum (notebook cell 11).',
 'recommendation_summary':'Retain gate_30; the analyst argues against moving the gate to level 40.',
 'metrics':{'retention_1':{'control_rate':.4482,'treatment_rate':.4423,'difference':-.0059,'p_value':.073921,'wald_ci':[-.0124,.0006]},
 'retention_7':{'control_rate':.1902,'treatment_rate':.1820,'difference':-.0082,'p_value':.001592,'wald_ci':[-.0133,-.0031]}},
 'missing':'Original pre-experiment plan, assignment/exposure logs, event timestamps, monetization/uninstall guardrails and costs are not supplied.'}
(packet/'readout.json').write_text(json.dumps(readout,indent=2)+'\n')
(packet/'notes.txt').write_text('Public Cookie Cats dataset replay. '+provenance['source_type']+'\nNo assignment, exposure or outcome timestamps have been invented. Retention flags are not purchase events. All users are retained for the main snapshot; the analyst exclusion is a separate sensitivity comparison. Primary selection is retrospective for this comparison. No original guardrail margins or study attestations are supplied.\nSource: '+provenance['repository']+'\nPinned revision: '+commit+'\nRaw CSV SHA-256: '+provenance['files']['cookie_cats.csv']['sha256']+'\n')
artifacts=[{'artifact_id':p.stem,'path':p.name,'type':p.suffix[1:],'schema_version':'1.0.0','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':provenance['repository'],'population':'public Cookie Cats player snapshot','window':'relative day 1 and day 7 after install; calendar dates unavailable','completeness':'unknown production coverage'} for p in sorted(packet.iterdir()) if p.name!='inventory.json']
(packet/'inventory.json').write_text(json.dumps({'schema_version':'1.0.0','artifacts':artifacts},indent=2)+'\n')
