import base64,json,tempfile,unittest,hashlib,io,zipfile
from pathlib import Path
from webdemo.bridge import dispatch
from start import seed_demo

class ReceivedEvidenceTests(unittest.TestCase):
    def test_receive_rerun_lineage_and_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);eid=seed_demo(root)
            def call(method,path,body=None):
                r=dispatch(root,method,path,json.dumps(body) if body is not None else '')
                return r['status'],json.loads(base64.b64decode(r['body']))
            def post(body):return call('POST','/api/workspace',dict(experiment_id=eid,**body))
            _,w=call('GET','/api/workspace');parent=w['experiments'][0]['runs'][-1]
            _,r=call('GET','/api/runs/'+parent)
            original=(root/parent/'report.json').read_bytes()
            status,e=post(dict(action='track',run_id=parent,finding_id='I03',request='Supply corrected export and plan'))
            fid=e['experiment']['followups'][0]['id']
            content=(root/parent/'evidence/source.csv').read_text()
            status,e=post(dict(action='receive',followup_id=fid,name='corrected.csv',content=content,kind='corrected_csv',note='Corrected export received'))
            self.assertEqual(status,200,e.get("error"))
            receipt=e['experiment']['followups'][0]['receipts'][0]
            self.assertEqual(receipt['sha256'],hashlib.sha256(content.encode()).hexdigest())
            payload=dict(label='Received rerun',intake=dict(filename='corrected.csv',content=content,mapping=r['intake']['mapping']),revision=dict(experiment_id=eid,parent_run_id=parent,reason='Recheck received export',followup_id=fid,receipt_id=receipt['id']))
            count=len(list(root.iterdir()))
            for bad in [dict(receipt_id='unknown'),dict(followup_id='unknown'),dict(parent_run_id=w['experiments'][0]['runs'][0])]:
                status,_=call('POST','/api/investigate',payload|dict(revision=payload['revision']|bad));self.assertEqual(status,400)
            status,_=call('POST','/api/investigate',payload|dict(intake=payload['intake']|dict(content=content+'\n')));self.assertEqual(status,400)
            self.assertEqual(count,len(list(root.iterdir())))
            status,child=call('POST','/api/investigate',payload);self.assertEqual(status,201,child)
            _,w=call('GET','/api/workspace');f=w['experiments'][0]['followups'][0]
            self.assertEqual(f['receipts'][0]['runs'],[child['run_id']])
            self.assertEqual(f['rechecks'][-1]['run_id'],child['run_id'])
            self.assertEqual(original,(root/parent/'report.json').read_bytes())
            self.assertEqual(child['decision']['status'],'blocked')
            status,_=post(dict(action='receive',followup_id=fid,name='../private.txt',content='x',kind='supporting',note='x'));self.assertEqual(status,400)
            status,_=post(dict(action='receive',followup_id=fid,name='plan.txt',content='Study plan for manual review',kind='supporting',note='Unverified document'));self.assertEqual(status,200)
            status,_=post(dict(action='receive',followup_id=fid,name='large-notes.txt',content='x'*100000,kind='supporting',note='Long text'));self.assertEqual(status,200)
            from pebbles.handoff import obligations
            status,e=post(dict(action='recommend',run_id=child['run_id'],author='Demo',recommendation='hold',rationale='Await validity evidence',acknowledged=[x['id'] for x in obligations(child)]));self.assertEqual(status,200)
            d=e['experiment']['decisions'][-1]
            post(dict(action='review',decision_id=d['id'],reviewer='Simulated',outcome='agree',rationale='Hold',confirmed=True))
            raw=dispatch(root,'GET',f'/api/handoff/{eid}/{d["id"]}')
            with zipfile.ZipFile(io.BytesIO(base64.b64decode(raw['body']))) as z:
                self.assertTrue(any(n.endswith('/plan.txt') for n in z.namelist()))
                self.assertTrue(any(n.endswith('/corrected.csv') for n in z.namelist()))
            pending=post(dict(action='recommend',run_id=child['run_id'],author='Demo',recommendation='hold',rationale='Await validity evidence',acknowledged=[x['id'] for x in obligations(child)]))[1]['experiment']['decisions'][-1]
            status,_=post(dict(action='receive',followup_id=fid,name='later.txt',content='Later evidence may contradict earlier review',kind='supporting',note='New evidence'));self.assertEqual(status,200)
            status,_=post(dict(action='review',decision_id=pending['id'],reviewer='Simulated',outcome='agree',rationale='Hold',confirmed=True));self.assertEqual(status,400,'new receipt must invalidate pending review')
            raw=dispatch(root,'GET',f'/api/handoff/{eid}/{d["id"]}')
            with zipfile.ZipFile(io.BytesIO(base64.b64decode(raw['body']))) as z:
                packet=json.loads(z.read('decision.json'))
                self.assertTrue(packet['needs_renewal'])
                self.assertTrue(any(x['name']=='later.txt' for x in packet['newer_received_evidence']))
                self.assertFalse(any(n.endswith('/later.txt') for n in z.namelist()))
