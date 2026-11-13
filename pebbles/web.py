"""Loopback-only UI for the existing investigator: python3 -m pebbles.web."""
import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import re
import secrets
import shutil
import tempfile
from urllib.parse import unquote, urlsplit
import uuid
import zipfile

from .core import FILES, investigate
from .report import html_report, markdown

ROOT = Path(__file__).resolve().parents[1]
STATIC = Path(__file__).parent / 'static'
EXAMPLES = {
    'checkout': ('p-a893', 'Checkout conversion', 'A checkout experiment with a scorecard, metric definition and event exports.'),
    'missing': ('p-c617', 'An incomplete handoff', 'An experiment with event exports but no metric definition.'),
    'conflict': ('p-82da', 'Two sources to reconcile', 'A scorecard and export whose source metadata is incomplete.'),
    'clean': ('p-7c41', 'A repeat visit', 'An experiment with a returning user in the exposure records.')}
ANALYSIS_EXAMPLES = {
 'ship-supported': ('ship-supported','A supported shipping recommendation','Primary conversion improves, refund harm is within the declared limit, and the review is recorded.'),
 'ship-harm': ('ship-harm','A guardrail blocks shipping','Conversion improves, but refunds increase beyond the acceptable harm limit.'),
 'ship-uncertain': ('ship-uncertain','A guardrail needs more evidence','Conversion improves, but uncertainty about refund harm blocks a recommendation.'),
 'benefit': ('benefit','A worthwhile improvement','A completed synthetic A/B test with enough evidence to assess a conversion gain.'),
 'uncertain': ('uncertain','An uncertain result','A completed synthetic test whose observed lift may not meet the goal.'),
 'harm': ('harm','A harmful change','A completed synthetic test where treatment reduces conversion.')}
PUBLIC_EXAMPLES = {'cookie-cats': ('cookie_cats','Cookie Cats · public analyst comparison','Reproduce a published retention analysis and inspect the evidence gaps. Public data, not a synthetic example.')}
CONTROLLED_EXAMPLES = {
 'cookie-clean': ('clean','Cookie Cats · control case','Controlled exercise with matching counts and records.'),
 'cookie-denominator': ('denominator','Cookie Cats · case A','Controlled discrepancy: investigate a reported retention result.'),
 'cookie-missing': ('missing-users','Cookie Cats · case B','Controlled discrepancy: investigate a supplied player export.'),
 'cookie-metric': ('wrong-metric','Cookie Cats · case C','Controlled discrepancy: investigate the reported metric.') }
EXAMPLES = {**CONTROLLED_EXAMPLES, **PUBLIC_EXAMPLES, **ANALYSIS_EXAMPLES, **EXAMPLES}

def example_folder(key):
    if key in CONTROLLED_EXAMPLES:return ROOT/'public_comparisons/cookie_cats/cases'/CONTROLLED_EXAMPLES[key][0]
    if key in PUBLIC_EXAMPLES:return ROOT/'public_comparisons/cookie_cats/packet'
    packet=EXAMPLES[key][0]
    return ROOT/'examples/analysis'/packet if key in ANALYSIS_EXAMPLES else ROOT/'evaluation/packages'/packet

def example_info(key):
    value=EXAMPLES[key]
    path=example_folder(key)/'configuration.json'
    config=json.loads(path.read_text()) if path.exists() else {}
    return {'id':key,'name':value[1],'description':value[2],'synthetic':key not in PUBLIC_EXAMPLES,'public_dataset':key in PUBLIC_EXAMPLES or key in CONTROLLED_EXAMPLES,'controlled_exercise':key in CONTROLLED_EXAMPLES,'analysis_plan':config.get('analysis_plan')}

MAX_BODY = 60_000_000


def make_server(port=8848, storage=None):
    storage = Path(storage or ROOT / 'runs/ui').resolve()
    storage.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.storage = storage
    server.token = secrets.token_urlsafe(32)
    return server


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send(self, value, status=200, content_type='application/json; charset=utf-8', download=None):
        body = json.dumps(value, ensure_ascii=False).encode() if content_type.startswith('application/json') else value if isinstance(value, bytes) else value.encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        if download:
            self.send_header('Content-Disposition', f'attachment; filename="{download}"')
        self.end_headers()
        self.wfile.write(body)

    def allowed(self, mutation=False):
        authority = f'127.0.0.1:{self.server.server_port}'
        alternate = f'localhost:{self.server.server_port}'
        if self.headers.get('Host') not in (authority, alternate):
            self.send({'error':'Use the local Pebbles address.'},403)
            return False
        origin = self.headers.get('Origin')
        if origin and origin not in ('http://'+authority,'http://'+alternate):
            self.send({'error':'Requests must originate from this local app.'},403)
            return False
        if mutation and not secrets.compare_digest(self.headers.get('X-Pebbles-Token',''),self.server.token):
            self.send({'error':'Reload the app before running an investigation.'},403)
            return False
        return True

    def run_dir(self, run_id):
        if not re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',run_id):
            raise ValueError('Unknown investigation.')
        directory = self.server.storage/run_id
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError('Unknown investigation.')
        return directory

    def do_GET(self):
        if not self.allowed(): return
        path = unquote(urlsplit(self.path).path)
        try:
            if path == '/':
                self.send((STATIC/'index.html').read_text().replace('__TOKEN__',self.server.token),content_type='text/html; charset=utf-8')
            elif path in ('/app.js','/presentation.js','/workspace.js','/intake.js','/decisions.js','/received.js','/analyst-workspace.js','/analyst-workspace.css','/style.css'):
                self.send((STATIC/path[1:]).read_text(),content_type='text/javascript; charset=utf-8' if path.endswith('.js') else 'text/css; charset=utf-8')
            elif path == '/api/workspace':
                from .workspace import access
                self.send(access(self.server.storage))
            elif path.startswith('/api/handoff/'):
                from .workspace import access
                from .handoff import bundle
                parts=path.split('/')
                if len(parts)!=5:raise ValueError('Unknown decision handoff.')
                experiment=next((e for e in access(self.server.storage)['experiments'] if e['id']==parts[3]),None)
                if experiment is None:raise ValueError('Unknown experiment.')
                decision=next((d for d in experiment.get('decisions',[]) if d['id']==parts[4]),None)
                if decision is None:raise ValueError('Unknown decision.')
                self.send(bundle(experiment,decision,self.run_dir),content_type='application/zip',download='pebbles-decision-handoff.zip')
            elif path.startswith('/api/decision-preview/'):
                from .handoff import obligations
                run=json.loads((self.run_dir(path.split('/')[-1])/'report.json').read_text())
                self.send({'obligations':obligations(run),'assessment':run.get('decision')})
            elif path == '/api/examples':
                self.send([example_info(key) for key in EXAMPLES if (example_folder(key)/'inventory.json').is_file()])
            elif path.startswith('/api/examples/'):
                parts=path.split('/')
                if len(parts)!=5 or parts[4]!='download' or parts[3] not in EXAMPLES: raise ValueError('Unknown example.')
                data=io.BytesIO()
                with zipfile.ZipFile(data,'w',zipfile.ZIP_DEFLATED) as archive:
                    for p in sorted(example_folder(parts[3]).iterdir()):
                        if p.is_file() and p.name in FILES|{'inventory.json'}: archive.writestr(p.name,p.read_bytes())
                self.send(data.getvalue(),content_type='application/zip',download='pebbles-example.zip')
            elif path == '/api/runs':
                runs=[]
                for p in self.server.storage.iterdir():
                    if p.is_symlink() or not p.is_dir(): continue
                    try:
                        r=json.loads((p/'report.json').read_text())
                        runs.append({k:r[k] for k in ('run_id','source_label','created_at','headline','execution_state')})
                    except (OSError,ValueError,KeyError): continue
                self.send(sorted(runs,key=lambda r:r['created_at'],reverse=True))
            elif path.startswith('/api/runs/'):
                parts=path.split('/')
                folder=self.run_dir(parts[3])
                if len(parts)==4:
                    self.send(json.loads((folder/'report.json').read_text()))
                elif len(parts)==5 and parts[4] in ('report.json','report.html','report.md'):
                    mime={'report.json':'application/json; charset=utf-8','report.html':'text/html; charset=utf-8','report.md':'text/markdown; charset=utf-8'}[parts[4]]
                    body=(folder/parts[4]).read_bytes()
                    if parts[4]=='report.json': self.send(json.loads(body))
                    else: self.send(body,content_type=mime,download=parts[4] if parts[4].endswith('.md') else None)
                elif len(parts)==6 and parts[4]=='evidence' and parts[5] in FILES|{'inventory.json'}:
                    p=folder/'evidence'/parts[5]
                    if p.is_symlink() or not p.is_file(): raise ValueError('Evidence file unavailable.')
                    # Keep evidence preview bounded; full inputs remain saved locally.
                    with p.open('rb') as f: data=f.read(200_001)
                    self.send({'name':p.name,'content':data[:200_000].decode('utf-8',errors='replace'),'truncated':len(data)>200_000})
                else: raise ValueError('Unknown resource.')
            else: self.send({'error':'Not found.'},404)
        except (ValueError,KeyError,IndexError,OSError) as ex:
            self.send({'error':str(ex)},404)

    def do_POST(self):
        if not self.allowed(mutation=True): return
        if urlsplit(self.path).path == '/api/workspace':
            try:
                from .workspace import access
                length=int(self.headers.get('Content-Length','0'))
                if not 0 < length <= 6_100_000: raise ValueError('Received evidence request is too large.')
                if self.headers.get('Content-Type','').split(';')[0]!='application/json': raise ValueError('Expected JSON.')
                body=json.loads(self.rfile.read(length))
                if not isinstance(body,dict): raise ValueError('Expected a workspace action.')
                if body.get('action')!='receive' and length>64000:raise ValueError('Workspace request exceeds 64 KB.')
                self.send(access(self.server.storage, body, lambda rid: json.loads((self.run_dir(rid)/'report.json').read_text())))
            except (ValueError,KeyError,TypeError,OSError) as ex:
                self.send({'error':str(ex)},400)
            return
        if urlsplit(self.path).path == '/api/intake/preview':
            try:
                from .intake import inspect
                length=int(self.headers.get('Content-Length','0'))
                if not 0 < length <= MAX_BODY: raise ValueError('CSV request too large.')
                body=json.loads(self.rfile.read(length))
                self.send(inspect(body.get('content'),body.get('mapping')))
            except (ValueError,TypeError,AttributeError) as ex: self.send({'error':str(ex)},400)
            return
        if urlsplit(self.path).path != '/api/investigate':
            self.send({'error':'Not found.'},404);return
        folder=None
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<=0 or length>MAX_BODY: raise ValueError('Choose a package under 50 MB, with no more than 10 files.')
            if self.headers.get('Content-Type','').split(';')[0]!='application/json': raise ValueError('Expected a JSON upload.')
            body=json.loads(self.rfile.read(length))
            if not isinstance(body,dict): raise ValueError('Invalid investigation request.')
            if 'intake' in body:
                from .intake import package
                if 'example' in body or 'files' in body: raise ValueError('Choose one import mode.')
                body['files']=package(body['intake'])
            revision=body.get('revision')
            destination=body.get('experiment_id')
            if destination is not None:
                from .workspace import access
                if revision is not None: raise ValueError('Use the revision destination only.')
                if not isinstance(destination,str) or not any(e['id']==destination for e in access(self.server.storage)['experiments']):
                    raise ValueError('Choose an existing experiment before importing.')
            parent=None
            if revision is not None:
                from .workspace import access, text
                if not isinstance(revision,dict): raise ValueError('Invalid revision metadata.')
                reason=text(revision,'reason',4000,True)
                parent_id=text(revision,'parent_run_id',36,True)
                experiment_id=text(revision,'experiment_id',36,True)
                experiment=next((e for e in access(self.server.storage)['experiments'] if e['id']==experiment_id),None)
                if experiment is None or parent_id not in experiment['runs']: raise ValueError('Choose an attached parent run.')
                if 'example' in body: raise ValueError('Upload a complete revised evidence package.')
                parent=json.loads((self.run_dir(parent_id)/'report.json').read_text())
                from .received import linked_receipt
                receipt=linked_receipt(experiment,revision)
                if receipt is not None:
                    import hashlib
                    supplied=(body.get('intake') or {}).get('content')
                    if not parent.get('intake') or not isinstance(supplied,str) or hashlib.sha256(supplied.encode()).hexdigest()!=receipt['sha256']:
                        raise ValueError('Rerun the exact received CSV using a mapped CSV parent.')
                revision={'experiment_id':experiment_id,'parent_run_id':parent_id,'reason':reason,**{k:revision[k] for k in ('followup_id','receipt_id') if k in revision}}
                # Preserve explicit user-entered settings; otherwise use the revised configuration.
                if 'analysis_plan' not in body:
                    a=parent.get('analysis') or {}
                    if a.get('plan_source')=='user-entered run settings': body['analysis_plan']=a.get('plan')
                    elif parent.get('submitted_analysis_plan') is not None: body['analysis_plan']=parent['submitted_analysis_plan']
            if 'example' in body:
                if body['example'] not in EXAMPLES: raise ValueError('Unknown example.')
                packet,default_label,_=EXAMPLES[body['example']]
                label=body.get('label',default_label)
                files=[{'name':p.name,'content':p.read_bytes().decode('utf-8')} for p in example_folder(body['example']).iterdir() if p.is_file()]
                synthetic=body['example'] not in PUBLIC_EXAMPLES
            else:
                files=body.get('files')
                label=body.get('label','Uploaded experiment')
                synthetic=False
            if not isinstance(label,str) or not label.strip() or len(label)>120: raise ValueError('Experiment name must be 1–120 characters.')
            if not isinstance(files,list) or not 1<=len(files)<=10: raise ValueError('Choose 1–10 evidence files, including inventory.json.')
            seen=set();total=0
            for f in files:
                if not isinstance(f,dict) or not isinstance(f.get('name'),str) or f['name'] not in FILES|{'inventory.json'} or f['name'] in seen: raise ValueError('Unsupported or duplicate filename. Load the files from one experiment package.')
                if not isinstance(f.get('content'),str): raise ValueError('Evidence files must contain UTF-8 text.')
                seen.add(f['name']);total+=len(f['content'].encode())
            if total>50_000_000: raise ValueError('Package exceeds 50 MB.')
            if 'inventory.json' not in seen: raise ValueError('inventory.json is missing. Download an example to see the supported package format.')
            with tempfile.TemporaryDirectory(prefix='pebbles-upload-') as temporary:
                packet_dir=Path(temporary)
                for f in files: (packet_dir/f['name']).write_text(f['content'],encoding='utf-8',newline='')
                report=investigate(packet_dir,analysis_plan=body.get('analysis_plan'))
                report.update(source_label=label.strip(),synthetic_example=synthetic,
                              evidence_files=[{'name':f['name'],'bytes':len(f['content'].encode())} for f in files])
                if revision is not None:
                    from .revisions import compare_runs
                    report['revision']=revision
                    report['revision_comparison']=compare_runs(parent,report)
                folder=self.server.storage/report['run_id'];folder.mkdir()
                shutil.copytree(packet_dir,folder/'evidence')
                (folder/'report.json').write_text(json.dumps(report,indent=2))
                (folder/'report.html').write_text(html_report(report))
                (folder/'report.md').write_text(markdown(report))
            if revision is not None:
                access(self.server.storage,{'action':'revision',**revision,'run_id':report['run_id']},
                       lambda rid: json.loads((self.run_dir(rid)/'report.json').read_text()))
            elif destination is not None:
                access(self.server.storage,{'action':'attach','experiment_id':destination,'run_id':report['run_id']},
                       lambda rid: json.loads((self.run_dir(rid)/'report.json').read_text()))
            self.send(report,201)
        except (ValueError,KeyError,TypeError,OSError) as ex:
            self.send({'error':str(ex)},400)
        except Exception:
            # Never turn an unexpected engine error into a verified analytical conclusion.
            self.send({'error':'Investigation could not complete. No analytical result is being claimed. Check the package format and try again.'},500)


def main():
    parser=argparse.ArgumentParser(description='Start the local Pebbles investigation UI.')
    parser.add_argument('--port',type=int,default=8848)
    parser.add_argument('--storage',type=Path,default=ROOT/'runs/ui')
    args=parser.parse_args()
    server=make_server(args.port,args.storage)
    print(f'Pebbles is ready: http://127.0.0.1:{server.server_port}',flush=True)
    print(f'Investigations and supplied files stay in {server.storage}',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=='__main__': main()
