import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class WebApp(unittest.TestCase):
    def test_web_workflow(self):
        # Run an actual ephemeral HTTP server in a child process; no mock backend.
        script = r'''
import json, tempfile, threading, urllib.request, urllib.error
from pathlib import Path
from pebbles.web import make_server
with tempfile.TemporaryDirectory() as tmp:
 server = make_server(port=0, storage=Path(tmp))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 base='http://127.0.0.1:'+str(server.server_port)
 def req(path, data=None, token=None, origin=None):
  headers={}
  if token: headers['X-Pebbles-Token']=token
  if origin: headers['Origin']=origin
  if data is not None: headers['Content-Type']='application/json'
  r=urllib.request.Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
  return urllib.request.urlopen(r)
 html=req('/').read().decode()
 assert 'Run investigation' in html
 token=server.token
 examples=json.load(req('/api/examples'))
 assert len(examples)==15
 for bad in ({'example':'checkout'}, {'files':[{'name':'../outside','content':'bad'}]}):
  try: req('/api/investigate',bad,token if 'files' in bad else None)
  except urllib.error.HTTPError as e: assert e.code in (400,403)
  else: raise AssertionError('unsafe request accepted')
 r=json.load(req('/api/investigate',{'example':'checkout'},token))
 rid=r['run_id']
 assert r['findings'] and r['source_label']=='Checkout conversion'
 assert next(f for f in r['findings'] if f['check_id']=='C05')['evidence_outcome']=='Failed'
 assert len(json.load(req('/api/runs')))==1
 assert json.load(req('/api/runs/'+rid))['run_id']==rid
 ev=json.load(req('/api/runs/'+rid+'/evidence/scorecard.json'))
 assert 'rate_percent' in ev['content']
 assert 'Pebbles' in req('/api/runs/'+rid+'/report.html').read().decode()
 try: req('/api/investigate',{'example':'checkout'},token, 'http://evil.example')
 except urllib.error.HTTPError as e: assert e.code==403
 else: raise AssertionError('cross origin accepted')
 files=[{'name':p.name,'content':p.read_text()} for p in Path('evaluation/packages/p-c617').iterdir() if p.is_file()]
 r=json.load(req('/api/investigate',{'files':files,'label':'My experiment'},token))
 assert r['source_label']=='My experiment'
 assert next(f for f in r['findings'] if f['check_id']=='C02')['evidence_outcome']=='Insufficient evidence'
 assert len(json.load(req('/api/runs')))==2
 # A genuine fixed-horizon assigned-user example traverses HTTP -> core -> analysis.
 r=json.load(req('/api/investigate',{'example':'benefit'},token))
 assert r['analysis']['status']=='improvement'
 assert r['analysis']['comparison']['difference_ci'][0] > .01
 rid=r['run_id']
 assert json.load(req('/api/runs/'+rid))['analysis']==r['analysis']
 assert 'Treatment versus control' in req('/api/runs/'+rid+'/report.html').read().decode()
 p=dict(r['analysis']['plan'],minimum_effect_pp=10)
 r=json.load(req('/api/investigate',{'example':'benefit','analysis_plan':p},token))
 assert r['analysis']['status']=='below_threshold'
 assert r['analysis']['plan_source']=='user-entered run settings'
 r=json.load(req('/api/investigate',{'example':'ship-supported'},token))
 assert r['decision']['status']=='supported'
 assert json.load(req('/api/runs/'+r['run_id']))['decision']==r['decision']
 assert 'Shipping decision' in req('/api/runs/'+r['run_id']+'/report.html').read().decode()
 r=json.load(req('/api/investigate',{'example':'cookie-cats'},token))
 assert r['public_dataset'] and not r['synthetic_example']
 assert r['decision']['status']=='blocked' and r['public_comparison']['row_count']==90189
 assert json.load(req('/api/runs/'+r['run_id']))['public_comparison']==r['public_comparison']
 assert 'Supplied readout versus export' in req('/api/runs/'+r['run_id']+'/report.html').read().decode()
 r=json.load(req('/api/investigate',{'example':'cookie-missing'},token))
 assert r['controlled_exercise'] and r['discrepancy']['diagnosis']=='population_mismatch'
 assert r['discrepancy']['population']['missing_count']==5000
 assert json.load(req('/api/runs/'+r['run_id']))['discrepancy']==r['discrepancy']
 assert 'Controlled discrepancy investigation' in req('/api/runs/'+r['run_id']+'/report.html').read().decode()
 # Revision HTTP workflow preserves originals and attaches lineage atomically in workspace.
 parent=r
 e=json.load(req('/api/workspace',{'action':'create','name':'Revision test'},token))['experiment']
 json.load(req('/api/workspace',{'action':'attach','experiment_id':e['id'],'run_id':parent['run_id']},token))
 before=req('/api/runs/'+parent['run_id']+'/report.json').read()
 files=[{'name':p.name,'content':p.read_bytes().decode()} for p in Path('public_comparisons/cookie_cats/cases/missing-users').iterdir() if p.is_file()]
 revised=json.load(req('/api/investigate',{'files':files,'label':'Evidence recheck','revision':{'experiment_id':e['id'],'parent_run_id':parent['run_id'],'reason':'Recheck same evidence'}},token))
 assert revised['revision']['parent_run_id']==parent['run_id']
 assert revised['revision_comparison']['after_decision']['status']=='blocked'
 assert req('/api/runs/'+parent['run_id']+'/report.json').read()==before
 stored=json.load(req('/api/workspace'))['experiments'][0]
 assert stored['revisions'][0]['run_id']==revised['run_id']
 assert 'Evidence revision' in req('/api/runs/'+revised['run_id']+'/report.html').read().decode()
 server.shutdown();server.server_close()
 # Reopen stored investigations after a restart.
 server=make_server(port=0,storage=Path(tmp))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 base='http://127.0.0.1:'+str(server.server_port)
 assert len(json.load(req('/api/runs')))==8
 server.shutdown();server.server_close()
print('HTTP workflow passed')
'''
        r = subprocess.run([sys.executable,'-c',script],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)

if __name__=='__main__': unittest.main()
