import unittest, tempfile, json
from pathlib import Path
from pebbles.intake import inspect, package
from pebbles.core import investigate
from pebbles.revisions import compare_runs
from pebbles.report import html_report, markdown

class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.csv='person,group,converted\na,C,0\nb,C,1\nc,T,true\nd,T,false\n'
        self.mapping=dict(unit='person',variant='group',outcome='converted',control='C',treatment='T',metric='Purchase in 7 days',population='All assigned users',window='2026-01-01 to 2026-01-08',experiment='checkout',design='independent-fixed-binary',confirmed=True)
    def run_import(self,content=None,mapping=None):
        with tempfile.TemporaryDirectory() as d:
            for f in package(dict(content=content or self.csv,mapping=mapping or self.mapping)):(Path(d)/f['name']).write_text(f['content'])
            return investigate(d)
    def test_import_replay_exports_and_revision(self):
        a=self.run_import();b=self.run_import(self.csv.replace('d,T,false','d,T,true'))
        self.assertEqual(a['intake']['comparison']['difference'],0)
        self.assertEqual(b['intake']['comparison']['difference'],.5)
        self.assertEqual(b['decision']['status'],'blocked')
        self.assertEqual(compare_runs(a,b)['after_result']['difference'],.5)
        self.assertIn('import.json',html_report(a));self.assertIn('Purchase in 7 days',markdown(a))
    def test_bad_rows_are_not_silently_dropped(self):
        for content in [self.csv+'a,T,1\n',self.csv.replace('c,T,true','c,T,'),self.csv.replace('d,T,false','d,X,false'),self.csv.replace('d,T,false','d,T,0.5')]:
            with self.subTest(content=content):
                self.assertTrue(inspect(content,self.mapping)['errors'])
                with self.assertRaises(ValueError):self.run_import(content)
    def test_csv_shape_and_headers(self):
        for content in ['id,id,x\na,C,1','id,arm,x\na,C,1,extra','id,arm,x\na,C','id,arm,x\n', self.csv.replace('b,C,1','\nb,C,1')]:
            with self.assertRaises(ValueError):inspect(content)
    def test_design_and_confirmation(self):
        for change in [dict(design='clustered'),dict(design='unknown'),dict(confirmed=False),dict(metric=''),dict(outcome='group')]:
            with self.assertRaises(ValueError):self.run_import(mapping=self.mapping|change)
    def test_changed_mapping_visible(self):
        a=self.run_import();b=self.run_import(mapping=self.mapping|{'metric':'Different meaning'})
        self.assertTrue(compare_runs(a,b)['settings_changed'])
        b=self.run_import();b['intake']['mapping']['source_filename']='renamed.csv'
        self.assertFalse(compare_runs(a,b)['settings_changed'])
    def test_bom_hash_preserved(self):
        import hashlib
        content='\ufeff'+self.csv
        r=self.run_import(content)
        self.assertEqual(r['input_hashes']['source.csv'],hashlib.sha256(content.encode()).hexdigest())

    def test_http_preview_import_and_revision(self):
        import threading, urllib.request, urllib.error
        from pebbles.web import make_server
        with tempfile.TemporaryDirectory() as tmp:
            server=make_server(0,tmp)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            def request(path,data):
                req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-Pebbles-Token':server.token})
                with urllib.request.urlopen(req) as response:return json.load(response)
            try:
                payload={'content':self.csv,'mapping':self.mapping,'filename':'ordinary.csv'}
                p=request('/api/intake/preview',payload);self.assertEqual(p['rows'],4)
                a=request('/api/investigate',{'label':'CSV','intake':payload})
                e=request('/api/workspace',{'action':'create','name':'CSV review'})['experiment']
                request('/api/workspace',{'action':'attach','experiment_id':e['id'],'run_id':a['run_id']})
                original=(Path(tmp)/a['run_id']/'report.json').read_bytes()
                b=request('/api/investigate',{'label':'Correction','intake':payload|{'content':self.csv.replace('d,T,false','d,T,true')},'revision':{'experiment_id':e['id'],'parent_run_id':a['run_id'],'reason':'Corrected outcome'}})
                self.assertEqual(b['revision_comparison']['after_result']['difference'],.5)
                self.assertEqual(original,(Path(tmp)/a['run_id']/'report.json').read_bytes())
                for report in ('report.html','report.md'):
                    self.assertIn(a['run_id'],(Path(tmp)/b['run_id']/report).read_text())
                with self.assertRaises(urllib.error.HTTPError):request('/api/investigate',{'intake':payload|{'mapping':self.mapping|{'design':'unknown'}}})
            finally:server.shutdown();server.server_close();thread.join()
