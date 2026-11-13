"""Execute predeclared independent-binomial calibration against known simulated truth."""
import hashlib
import json
from pathlib import Path
import random
import sys
from datetime import datetime, timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from pebbles.analysis import compare_proportions, METHOD

root=Path(__file__).parent
protocol=json.loads((root/'protocol.json').read_text())
results=[]
for offset,s in enumerate(protocol['scenarios']):
    rng=random.Random(protocol['seed']+offset)
    covered=rejected=0
    truth=s['p_treatment']-s['p_control']
    for _ in range(protocol['trials_per_scenario']):
        c=sum(rng.random()<s['p_control'] for _ in range(s['n_control']))
        t=sum(rng.random()<s['p_treatment'] for _ in range(s['n_treatment']))
        low,high=compare_proportions(c,s['n_control'],t,s['n_treatment'])['difference_ci']
        covered+=low<=truth<=high
        rejected+=low>0 or high<0
    count=protocol['trials_per_scenario'];coverage=covered/count;rate=rejected/count
    passes=protocol['coverage_bounds'][0]<=coverage<=protocol['coverage_bounds'][1]
    if truth==0: passes=passes and protocol['null_rejection_bounds'][0]<=rate<=protocol['null_rejection_bounds'][1]
    results.append(dict(s,truth=truth,covered=covered,coverage=coverage,null_exclusions=rejected,null_exclusion_rate=rate,passed=passes))
result={'method':METHOD,'created_at':datetime.now(timezone.utc).isoformat(),'protocol_sha256':hashlib.sha256((root/'protocol.json').read_bytes()).hexdigest(),'implementation_sha256':hashlib.sha256((root.parents[1]/'pebbles/analysis.py').read_bytes()).hexdigest(),'trials_per_scenario':protocol['trials_per_scenario'],'seed':protocol['seed'],'results':results,'passed':all(s['passed'] for s in results),'limits':protocol['limits']}
(root/'results.json').write_text(json.dumps(result,indent=2)+'\n')
for r in results: print(f"{r['id']}: coverage={r['coverage']:.3%}, zero exclusions={r['null_exclusion_rate']:.3%}, passed={r['passed']}")
raise SystemExit(0 if result['passed'] else 1)
