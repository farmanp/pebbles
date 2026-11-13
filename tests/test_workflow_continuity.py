import base64,json,tempfile,unittest
from pathlib import Path
from webdemo.bridge import dispatch

class ContinuityTests(unittest.TestCase):
    def test_contextual_import_revision_and_invalid_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            def call(method,path,body=None):
                r=dispatch(root,method,path,json.dumps(body) if body is not None else '')
                return r['status'],json.loads(base64.b64decode(r['body']))
            _,e=call('POST','/api/workspace',{'action':'create','name':'Checkout'})
            eid=e['experiment']['id']
            payload={'label':'CSV','experiment_id':eid,'intake':{'filename':'input.csv','content':'user,arm,result\na,C,1\nb,C,0\nc,T,0\nd,T,0\n','mapping':dict(unit='user',variant='arm',outcome='result',control='C',treatment='T',experiment='Checkout',metric='Purchase',population='All users',window='Complete seven days',design='independent-fixed-binary',confirmed=True)}}
            status,r=call('POST','/api/investigate',payload);self.assertEqual(status,201)
            _,w=call('GET','/api/workspace');self.assertEqual(w['experiments'][0]['runs'],[r['run_id']])
            original=(root/r['run_id']/'report.json').read_bytes()
            revised={k:v for k,v in payload.items() if k!='experiment_id'}
            revised['revision']={'experiment_id':eid,'parent_run_id':r['run_id'],'reason':'Corrected input'}
            status,child=call('POST','/api/investigate',revised);self.assertEqual(status,201)
            _,w=call('GET','/api/workspace');self.assertEqual(w['experiments'][0]['runs'],[r['run_id'],child['run_id']])
            self.assertEqual(original,(root/r['run_id']/'report.json').read_bytes())
            self.assertNotIn('Attach this run',child['decision']['next_action'])
            count=len(list(root.iterdir()))
            status,_=call('POST','/api/investigate',payload|{'experiment_id':'unknown'})
            self.assertEqual(status,400);self.assertEqual(count,len(list(root.iterdir())))
            status,_=call('POST','/api/investigate',revised|{'experiment_id':'unknown'})
            self.assertEqual(status,400)
