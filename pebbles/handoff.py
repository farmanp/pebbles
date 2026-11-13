"""Frozen local decisions and evidence handoff, distinct from analytical validity."""
import copy
import hashlib
import html
import io
import json
import zipfile

RECOMMENDATIONS=('ship','hold','stop','iterate')
REVIEWS=('agree','request changes','disagree')

def report_fingerprint(report):
    """Use the same canonical report identity when recording and exporting a decision."""
    return hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()


def obligations(run):
    d=run.get('decision') or {}
    items=[('blocker',x) for x in d.get('blockers',[])]+[('assumption',x) for x in d.get('unresolved',[])]+[('not evaluated',x) for x in run.get('not_evaluated',[])]
    for f in run.get('findings',[]):
        if f.get('execution_state')!='Completed' or f.get('evidence_outcome')!='Verified':
            items.append(('finding',f['check_id']+': '+f['question']+' — '+(f.get('evidence_outcome') or f['execution_state'])+'. '+f['explanation']))
    return [{'id':str(i),'kind':kind,'text':value} for i,(kind,value) in enumerate(items)]

def received_files(context):
    return [x for f in context.get('followups',[]) for x in f.get('receipts',[])]

def needs_renewal(experiment,decision):
    return experiment['runs']!=decision['context']['runs'] or {x['id'] for x in received_files(experiment)}!={x['id'] for x in received_files(decision['context'])}

def create(experiment,body,run,now,text):
    import uuid
    recommendation=body.get('recommendation')
    if recommendation not in RECOMMENDATIONS:raise ValueError('Choose ship, hold, stop or iterate.')
    required=obligations(run)
    if body.get('acknowledged')!=[x['id'] for x in required]:raise ValueError('Review and acknowledge every blocker, assumption and unresolved finding for this exact run.')
    return {'id':str(uuid.uuid4()),'created_at':now,'run_id':run['run_id'],'author':text(body,'author',120,True),
            'recommendation':recommendation,'rationale':text(body,'rationale',4000,True),
            'obligations':required,'acknowledged':body['acknowledged'],
            'assessment':copy.deepcopy(run.get('decision')),'input_hashes':copy.deepcopy(run['input_hashes']),
            'context':copy.deepcopy({k:experiment.get(k,[]) for k in ('runs','followups','revisions','events')}),
            'prior_decisions':copy.deepcopy([{k:v for k,v in d.items() if k not in ('context','prior_decisions')} for d in experiment.get('decisions',[])]),
            'experiment_name':experiment['name'],'review':None}

def bundle(experiment,decision,read_folder):
    if not decision.get('review'):raise ValueError('Record a reviewer response before exporting the decision handoff.')
    stale=needs_renewal(experiment,decision)
    frozen_receipts={x['id'] for x in received_files(decision['context'])}
    newer_receipts=[{k:x[k] for k in ('id','name','sha256','at')} for x in received_files(experiment) if x['id'] not in frozen_receipts]
    title='REVIEW NEEDS RENEWAL — newer evidence is attached or received' if stale else 'Recorded review of the cited evidence snapshot'
    status=(decision.get('assessment') or {}).get('status','not assessed')
    lines=['# Pebbles decision handoff','',title,'','Experiment: '+decision['experiment_name'],
           'Decision ID: '+decision['id'],'Evidence run: '+decision['run_id'],
           'Analyst recommendation: '+decision['recommendation'],'Analyst: '+decision['author'],
           'Created: '+decision['created_at'],'Rationale: '+decision['rationale'],'',
           'Pebbles assessment: '+status,'Human agreement does not clear failed checks, establish safety, or authorize deployment.','',
           '## Recorded reviewer response',decision['review']['outcome']+' — '+decision['review']['reviewer'],
           decision['review']['rationale'],'Reviewed: '+decision['review']['at'],'',
           'Local names are unauthenticated labels. This records a review; it is not an approval service.','',
           '## Acknowledged unresolved evidence']
    lines += ['- '+x['kind']+': '+x['text'] for x in decision['obligations']] or ['None listed; inspect the full report assumptions.']
    lines += ['','## Contents','decision.json preserves the recommendation, review and investigation context at recommendation time. Each runs/<id>/ directory contains saved reports and original evidence. manifest.json lists SHA-256 fingerprints.','',
              'Newer runs attached since this recommendation: '+', '.join(x for x in experiment['runs'] if x not in decision['context']['runs']) if stale else 'No additional runs are attached at export time.']
    lines += ['','Received files added after this snapshot (excluded from the reviewed packet): '+', '.join(x['name'] for x in newer_receipts)] if newer_receipts else []
    md='\n'.join(lines)+'\n'
    payload={'export_status':title,'needs_renewal':stale,'current_attached_runs':experiment['runs'],'newer_received_evidence':newer_receipts,'decision':decision}
    files={'README.md':md.encode(),'decision.json':json.dumps(payload,indent=2).encode(),
           'index.html':('<!doctype html><meta charset="utf-8"><title>Pebbles decision handoff</title><style>body{max-width:900px;margin:40px auto;font:16px system-ui;line-height:1.6;padding:24px}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h1>Decision and evidence handoff</h1><pre>'+html.escape(md)+'</pre>').encode()}
    from .core import FILES
    for rid in decision['context']['runs']:
        folder=read_folder(rid)
        report=json.loads((folder/'report.json').read_text())
        if report_fingerprint(report) != decision['report_fingerprints'][rid]:
            raise ValueError('Saved report changed since recommendation; cannot export this handoff.')
        from .report import html_report, markdown
        files[f'runs/{rid}/report.json']=(folder/'report.json').read_bytes()
        files[f'runs/{rid}/report.md']=markdown(report).encode()
        files[f'runs/{rid}/report.html']=html_report(report).encode()
        for name,digest in report['input_hashes'].items():
            if name not in FILES|{'inventory.json'}:raise ValueError('Unsupported evidence path in saved report.')
            path=folder/'evidence'/name
            if path.is_symlink():raise ValueError('Evidence symlinks cannot be exported.')
            raw=path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Saved evidence changed; cannot export a verified handoff.')
            files[f'runs/{rid}/evidence/{name}']=raw
    for followup in decision['context'].get('followups',[]):
        for receipt in followup.get('receipts',[]):
            raw=receipt['content'].encode()
            if hashlib.sha256(raw).hexdigest()!=receipt['sha256']:raise ValueError('Received evidence fingerprint mismatch.')
            files[f"received/{followup['id']}/{receipt['id']}/{receipt['name']}"]=raw
    files['manifest.json']=json.dumps({name:hashlib.sha256(raw).hexdigest() for name,raw in files.items()},indent=2).encode()
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,raw in files.items():archive.writestr(name,raw)
    return stream.getvalue()
