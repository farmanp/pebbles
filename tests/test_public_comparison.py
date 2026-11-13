import unittest
from pathlib import Path
from pebbles.public_comparison import calculate, parse_csv

ROOT=Path(__file__).resolve().parents[1]
class PublicComparison(unittest.TestCase):
    def test_actual_snapshot_and_analyst_exclusion(self):
        rows=parse_csv((ROOT/'public_comparisons/cookie_cats/source/cookie_cats.csv').read_text())
        r=calculate(rows)
        self.assertEqual(r['row_count'],90189)
        self.assertEqual(r['all_users']['retention_7']['control']['retained_users'],8502)
        self.assertEqual(r['all_users']['retention_7']['treatment']['retained_users'],8279)
        self.assertEqual(r['analyst_population']['retention_7']['control']['users'],44699)
        self.assertAlmostEqual(r['analyst_population']['retention_7']['wald']['p_value'],.001592,places=6)
        self.assertEqual(len(r['excluded_users']),1)
        self.assertLess(r['all_users']['retention_7']['difference_ci'][1],0)
        self.assertGreater(r['all_users']['retention_1']['difference_ci'][1],0)
    def test_invalid_rows_never_silently_filtered(self):
        header='userid,version,sum_gamerounds,retention_1,retention_7\n'
        for rows in ['1,gate_30,1,False,unknown\n','1,gate_30,1,False,True\n1,gate_40,2,True,True\n','1,gate_50,1,False,True\n','1,gate_30,-1,False,True\n']:
            with self.assertRaises(ValueError):parse_csv(header+rows)

    def test_integrated_replay_stays_blocked_and_checks_fingerprints(self):
        import tempfile, shutil, json, hashlib
        from pebbles.core import investigate
        packet=ROOT/'public_comparisons/cookie_cats/packet'
        r=investigate(packet,analysis_plan={'predeclared':True,'guardrails_set_complete':True})
        self.assertEqual(r['execution_state'],'Completed')
        self.assertEqual(r['decision']['status'],'blocked')
        self.assertIsNone(r['analysis'])
        self.assertTrue(all(c['matches'] for c in r['public_comparison']['readout_checks']))
        with tempfile.TemporaryDirectory() as tmp:
            copy=Path(tmp)/'packet';shutil.copytree(packet,copy)
            readout=json.loads((copy/'readout.json').read_text())
            readout['metrics']['retention_7']['control_rate']=.5
            (copy/'readout.json').write_text(json.dumps(readout))
            inv=json.loads((copy/'inventory.json').read_text())
            next(e for e in inv['artifacts'] if e['path']=='readout.json')['sha256']=hashlib.sha256((copy/'readout.json').read_bytes()).hexdigest()
            (copy/'inventory.json').write_text(json.dumps(inv))
            mismatch=investigate(copy)
            self.assertEqual(next(f for f in mismatch['findings'] if f['check_id']=='P02')['evidence_outcome'],'Failed')
            with (copy/'cookie_cats.csv').open('a') as f:f.write(' ')
            bad=investigate(copy);self.assertEqual(bad['execution_state'],'partial');self.assertIsNone(bad['public_comparison'])

    def test_oversized_csv_field_is_an_input_result(self):
        import tempfile, shutil, json, hashlib
        from pebbles.core import investigate
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'packet';shutil.copytree(ROOT/'public_comparisons/cookie_cats/packet',folder)
            (folder/'cookie_cats.csv').write_text('userid,version,sum_gamerounds,retention_1,retention_7\n'+'1'*140000+',gate_30,1,TRUE,FALSE\n')
            inv=json.loads((folder/'inventory.json').read_text())
            next(e for e in inv['artifacts'] if e['path']=='cookie_cats.csv')['sha256']=hashlib.sha256((folder/'cookie_cats.csv').read_bytes()).hexdigest()
            (folder/'inventory.json').write_text(json.dumps(inv))
            r=investigate(folder)
            self.assertEqual(r['execution_state'],'partial');self.assertIsNone(r['public_comparison'])
