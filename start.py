#!/usr/bin/env python3
"""Launch Pebbles with a reproducible synthetic workspace; no downloads required."""
import argparse
import json
from pathlib import Path
import tempfile
import webbrowser

from pebbles.core import investigate
from pebbles.handoff import obligations
from pebbles.intake import package
from pebbles.report import html_report, markdown
from pebbles.revisions import compare_runs
from pebbles.web import make_server
from pebbles.workspace import access

ROOT = Path(__file__).resolve().parent

def seed_demo(storage):
    """Seed only once. Never modify a user's existing run or workspace."""
    storage.mkdir(parents=True, exist_ok=True)
    marker = storage / 'quickstart-demo.json'
    if marker.exists():
        saved = json.loads(marker.read_text())
        if any(e['id'] == saved['experiment_id'] for e in access(storage)['experiments']):
            return saved['experiment_id']
    e = access(storage, {'action':'create', 'name':'Checkout · synthetic demo', 'owner':'Demo analyst'})['experiment']
    mapping = dict(unit='user',variant='variant',outcome='converted',control='control',treatment='treatment',
                   experiment='Synthetic checkout',metric='Purchased within 7 days',
                   population='Synthetic assigned users; initial export deliberately omits 500 treatment non-converters',
                   window='Synthetic fixed 7-day follow-up, complete',design='independent-fixed-binary',confirmed=True)
    rows = ['user,variant,converted']
    for arm, positives in [('control',200),('treatment',150)]:
        for n in range(1000):
            rows.append(f'{arm}-{n},{arm},{int(n < positives)}')
    full = '\n'.join(rows) + '\n'
    incomplete = '\n'.join(r for r in rows if not (r.startswith('treatment-') and int(r.split(',')[0].split('-')[1]) >= 500)) + '\n'
    parent = None
    read_run = lambda rid: json.loads((storage/rid/'report.json').read_text())
    for label, content in [('Original export · synthetic', incomplete), ('Corrected export · synthetic', full)]:
        files = package({'content':content,'filename':'synthetic-checkout.csv','mapping':mapping})
        with tempfile.TemporaryDirectory(prefix='pebbles-demo-') as tmp:
            for f in files: (Path(tmp)/f['name']).write_text(f['content'],encoding='utf-8',newline='')
            report = investigate(tmp)
        report.update(source_label=label,synthetic_example=True,
                      evidence_files=[{'name':f['name'],'bytes':len(f['content'].encode())} for f in files])
        if parent:
            revision={'experiment_id':e['id'],'parent_run_id':parent['run_id'],
                      'reason':'Synthetic correction: restore 500 deliberately omitted treatment users who did not convert. This is a demo, not production evidence.'}
            report.update(revision=revision,revision_comparison=compare_runs(parent,report))
        folder=storage/report['run_id'];(folder/'evidence').mkdir(parents=True)
        for f in files:(folder/'evidence'/f['name']).write_text(f['content'],encoding='utf-8',newline='')
        (folder/'report.json').write_text(json.dumps(report,indent=2))
        (folder/'report.html').write_text(html_report(report))
        (folder/'report.md').write_text(markdown(report))
        if parent:
            access(storage,dict(action='revision',**revision,run_id=report['run_id']),read_run)
        else:
            access(storage,dict(action='attach',experiment_id=e['id'],run_id=report['run_id']),read_run)
        parent=report
    result=access(storage,dict(action='recommend',experiment_id=e['id'],run_id=parent['run_id'],
        author='Example analyst (simulated)',recommendation='hold',
        rationale='Demo recommendation: hold shipping. The corrected export has lower conversion, and original study, completeness and guardrail evidence remain unresolved.',
        acknowledged=[x['id'] for x in obligations(parent)]),read_run)
    decision=result['experiment']['decisions'][-1]
    access(storage,dict(action='review',experiment_id=e['id'],decision_id=decision['id'],
        reviewer='Example reviewer (simulated)',outcome='agree',confirmed=True,
        rationale='Simulated review for the quick-start tour. This is not an actual analyst review or production approval.'),read_run)
    marker.write_text(json.dumps({'experiment_id':e['id']}))
    return e['id']

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8848)
    parser.add_argument('--storage',type=Path,default=ROOT/'runs/quickstart')
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    storage=args.storage.resolve()
    experiment_id=seed_demo(storage)
    try: server=make_server(args.port,storage)
    except OSError:
        if args.port == 0: raise
        server=make_server(0,storage)
    url=f'http://127.0.0.1:{server.server_port}/#experiment/{experiment_id}/investigation'
    print(f'Pebbles is ready: {url}',flush=True)
    print('Synthetic demo only. Switch evidence runs, inspect revisions, then open Decision. Ctrl+C stops the app.',flush=True)
    if not args.no_browser: webbrowser.open(url)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=='__main__': main()
