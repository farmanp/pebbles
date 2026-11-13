"""Synthetic shipping reviews; per-user flags are supplied observations, not production evidence."""
import hashlib
import json
from pathlib import Path
import shutil
ROOT=Path(__file__).parent
for name,count in [('ship-supported',20),('ship-harm',200),('ship-uncertain',55)]:
    target=ROOT/name
    target.mkdir(exist_ok=True)
    for p in (ROOT/'benefit').iterdir():shutil.copyfile(p,target/p.name)
    config=json.loads((target/'configuration.json').read_text())
    definition='Assigned user had at least one refund during the declared experiment window.'
    config['analysis_plan'].update(guardrails=[{'id':'refund','name':'Refund rate','version':'v1','definition':definition,'direction':'lower','max_harm_pp':2}],guardrails_predeclared=True,guardrails_complete=True,guardrails_set_complete=True,business_review_complete=True,business_review_notes='Synthetic review: implementation can be rolled back and expected operating costs are acceptable. This is demonstration data, not a real business assessment.')
    (target/'configuration.json').write_text(json.dumps(config,indent=2)+'\n')
    evidence={k:config[k] for k in ('schema_version','experiment_id','revision','window_start','window_end')}
    evidence['metrics']=[{'id':'refund','version':'v1','definition':definition,'rows':[{'user_id':f'{arm}-{i}','value':i<(20 if arm=='control' else count)} for arm in ['control','treatment'] for i in range(2000)]}]
    (target/'guardrails.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (target/'notes.txt').write_text('Synthetic shipping-review demonstration. Guardrail true/false observations cover all assigned users over the declared window. Study and business-review declarations are illustrative, not independently verified production evidence.\n')
    inv=json.loads((target/'inventory.json').read_text())
    template=dict(inv['artifacts'][0])
    template.update(artifact_id='guardrails',path='guardrails.json',type='json',grain='one binary observation per assigned user per metric')
    inv['artifacts'].append(template)
    for entry in inv['artifacts']:entry['sha256']=hashlib.sha256((target/entry['path']).read_bytes()).hexdigest()
    (target/'inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
