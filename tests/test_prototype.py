import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKETS = ROOT / 'evaluation/packages'


def refresh(folder):
    p = folder / 'inventory.json'
    inv = json.loads(p.read_text())
    inv['artifacts'] = [a for a in inv['artifacts'] if (folder / a['path']).exists()]
    for a in inv['artifacts']:
        a['sha256'] = hashlib.sha256((folder / a['path']).read_bytes()).hexdigest()
    p.write_text(json.dumps(inv))


class Prototype(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def packet(self, name='p-7c41'):
        dest = self.base / 'input'
        shutil.copytree(PACKETS / name, dest)
        return dest

    def run_packet(self, folder, output='result'):
        out = self.base / output
        result = subprocess.run([sys.executable, '-m', 'pebbles', str(folder), '--output', str(out)], cwd=ROOT, capture_output=True, text=True)
        self.assertIn(result.returncode, (0, 2), result.stderr)
        self.assertTrue((out / 'report.json').exists(), result.stdout + result.stderr)
        report = json.loads((out / 'report.json').read_text())
        self.assertTrue((out / 'report.html').exists())
        self.assertTrue((out / 'report.md').exists())
        return report

    def check(self, report, cid):
        return next(x for x in report['findings'] if x['check_id'] == cid)

    def test_all_prepared_packets_statuses_and_exact_metrics(self):
        mapping = json.loads((ROOT / 'evaluation/private-oracles/packet-map.json').read_text())['packets']
        for item in mapping:
            pid = item['packet_id']
            with self.subTest(case=item['case'], form=item['form']):
                # Only the test harness reads expected answers. The CLI gets a packet path.
                r = self.run_packet(PACKETS / pid, pid + '-all')
                oracle = json.loads((ROOT / 'evaluation/private-oracles' / (pid + '.json')).read_text())
                for a in oracle['assertions']:
                    if a['check_id'] not in {'C%02d' % n for n in range(1,11)}:
                        continue
                    f = self.check(r, a['check_id'])
                    self.assertEqual(f['execution_state'], a['execution_state'], a['check_id'])
                    self.assertEqual(f['evidence_outcome'], a['evidence_outcome'], a['check_id'])
                    if a['check_id'] == 'C02' and a['evidence_outcome'] == 'Verified':
                        for arm, rate in a['expected'].get('rates', {}).items():
                            self.assertEqual(f['values'][arm]['rate'], rate)
                        for arm in ('control', 'treatment'):
                            expected = a['expected'].get(arm)
                            if expected and 'numerator' in expected:
                                for key in ('numerator','denominator','rate'):
                                    self.assertEqual(f['values'][arm][key], expected[key])

    def test_sql_comment_cannot_supply_verified_expression(self):
        p = self.packet()
        old = 'denominators AS (SELECT variant_id,COUNT(DISTINCT user_id) AS denominator FROM valid GROUP BY variant_id)'
        (p/'metric.sql').write_text('/* ' + old + ' */ SELECT 1;')
        refresh(p)
        r = self.run_packet(p)
        self.assertIsNone(self.check(r,'C03')['evidence_outcome'])

    def test_sql_string_cannot_supply_verified_expression(self):
        p = self.packet()
        (p/'metric.sql').write_text("SELECT 'denominators AS (SELECT variant_id,COUNT(DISTINCT user_id) AS denominator FROM valid GROUP BY variant_id)';")
        refresh(p)
        r = self.run_packet(p)
        self.assertIsNone(self.check(r,'C03')['evidence_outcome'])

    def test_out_of_range_utc_timestamp_is_visible_input_error(self):
        p = self.packet()
        rows = (p/'outcomes.jsonl').read_text().splitlines()
        row = json.loads(rows[0]); row['occurred_at'] = '0001-01-01T00:00:00+01:00'
        rows[0] = json.dumps(row)
        (p/'outcomes.jsonl').write_text('\n'.join(rows)+'\n')
        refresh(p)
        r = self.run_packet(p)
        self.assertEqual(self.check(r,'C02')['execution_state'],'blocked-invalid-input')
        self.assertEqual(self.check(r,'C04')['evidence_outcome'],'Verified')

    def test_runs_with_only_runtime_and_evidence_present(self):
        isolated = self.base / 'isolated'
        shutil.copytree(ROOT/'pebbles', isolated/'pebbles', ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(PACKETS/'p-a893', isolated/'input')
        result = subprocess.run([sys.executable,'-m','pebbles','input','--output','output'],cwd=isolated,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        report = json.loads((isolated/'output/report.json').read_text())
        self.assertEqual(self.check(report,'C02')['values']['treatment']['rate'],'2/3')
        self.assertEqual(self.check(report,'C05')['evidence_outcome'],'Failed')

    def test_reordering_and_version_change(self):
        p = self.packet()
        first = self.run_packet(p)
        for name in ('assignments.jsonl','exposures.jsonl','outcomes.jsonl'):
            lines = (p/name).read_text().splitlines()
            (p/name).write_text('\n'.join(reversed(lines))+'\n')
        refresh(p)
        reordered = self.run_packet(p,'reordered')
        self.assertEqual(self.check(first,'C02')['values'], self.check(reordered,'C02')['values'])
        m = json.loads((p/'metric.json').read_text())
        m.update(version='v2',denominator='distinct valid assigned users',numerator='assigned users with purchase strictly after assignment and before window_end')
        (p/'metric.json').write_text(json.dumps(m))
        c = json.loads((p/'configuration.json').read_text());c['metric_ref']='purchase_conversion@v2'
        (p/'configuration.json').write_text(json.dumps(c))
        (p/'metric.sql').unlink(); refresh(p)
        second = self.run_packet(p,'v2')
        self.assertEqual(self.check(second,'C02')['values']['control']['rate'],'1/4')
        self.assertEqual(self.check(second,'C02')['values']['treatment']['rate'],'1/2')
        self.assertEqual(self.check(second,'C05')['evidence_outcome'],'Failed')
        self.assertEqual(json.loads((self.base/'result/report.json').read_text()), first)

    def test_actual_denominator_defect(self):
        r = self.run_packet(self.packet('p-a893'))
        self.assertEqual(self.check(r, 'C05')['evidence_outcome'], 'Failed')
        self.assertEqual(self.check(r, 'C02')['values']['treatment']['rate'], '2/3')
        self.assertEqual(self.check(r, 'C03')['evidence_outcome'], 'Failed')
        self.assertIn('2/4', self.check(r, 'C05')['explanation'])
        self.assertIn('2/3', self.check(r, 'C05')['explanation'])
        self.assertEqual(self.check(r, 'C09')['evidence_outcome'], 'Insufficient evidence')

    def test_clean_repeat_is_not_a_defect(self):
        r = self.run_packet(self.packet())
        self.assertEqual(self.check(r, 'C05')['evidence_outcome'], 'Verified')
        self.assertEqual(self.check(r, 'C02')['values']['treatment']['denominator'], 3)
        self.assertEqual(self.check(r, 'C08')['values']['repeat_encounters'], 1)
        self.assertFalse(any(f['evidence_outcome'] == 'Failed' for f in r['findings']))

    def test_missing_evidence_and_contradictory_sources(self):
        for name, expected in [('p-39f2', 'Insufficient evidence'), ('p-c617', 'Insufficient evidence'), ('p-82da', 'Insufficient evidence')]:
            with self.subTest(name=name):
                folder = self.base / name
                shutil.copytree(PACKETS / name, folder)
                r = self.run_packet(folder, name + '-out')
                self.assertEqual(self.check(r, 'C05')['evidence_outcome'], expected)
                self.assertEqual(self.check(r, 'C04')['evidence_outcome'], 'Verified')
                if name == 'p-82da':
                    self.assertEqual(self.check(r, 'C06')['evidence_outcome'], 'Failed')
                    self.assertEqual(self.check(r, 'C07')['evidence_outcome'], 'Insufficient evidence')
                else:
                    self.assertEqual(self.check(r, 'C02')['evidence_outcome'], 'Insufficient evidence')

    def test_malformed_scorecard_preserves_metric(self):
        p = self.packet()
        (p / 'scorecard.json').write_text('{\nwrong')
        refresh(p)
        r = self.run_packet(p)
        self.assertEqual(r['execution_state'], 'partial')
        self.assertEqual(self.check(r, 'C02')['evidence_outcome'], 'Verified')
        self.assertIsNone(self.check(r, 'C04')['evidence_outcome'])
        self.assertIn('line 2', self.check(r, 'C04')['explanation'])

    def test_timestamp_boundaries(self):
        for stamp, count in [('2026-01-01T12:04:59Z', 1), ('2026-01-01T12:05:00Z', 1), ('2026-01-02T12:00:00Z', 1), ('2026-01-02T11:59:59Z', 2)]:
            with self.subTest(stamp=stamp):
                folder = self.base / str(count) / stamp.replace(':', '-')
                shutil.copytree(PACKETS / 'p-7c41', folder)
                with (folder / 'outcomes.jsonl').open('a') as f:
                    f.write(json.dumps({'outcome_id':'new', 'user_id':'C2','event_type':'purchase','occurred_at':stamp})+'\n')
                refresh(folder)
                r = self.run_packet(folder, 'out-' + stamp.replace(':','-'))
                self.assertEqual(self.check(r, 'C02')['values']['control']['numerator'], count)

    def test_replay_and_conflict(self):
        p = self.packet()
        rows = [json.loads(x) for x in (p/'exposures.jsonl').read_text().splitlines()]
        with (p/'exposures.jsonl').open('a') as f:
            f.write(json.dumps(rows[0])+'\n')
        refresh(p)
        r = self.run_packet(p)
        self.assertEqual(self.check(r,'C02')['values']['control']['rate'], '1/3')
        rows[0]['user_id'] = 'C2'
        with (p/'exposures.jsonl').open('a') as f:
            f.write(json.dumps(rows[0])+'\n')
        refresh(p)
        r = self.run_packet(p, 'conflict')
        self.assertIsNone(self.check(r, 'C02')['evidence_outcome'])
        self.assertEqual(self.check(r, 'C08')['evidence_outcome'], 'Verified')

    def test_unknown_definition_is_not_guessed(self):
        p = self.packet()
        metric = json.loads((p/'metric.json').read_text())
        metric['numerator'] = 'all purchases including purchases before exposure'
        (p/'metric.json').write_text(json.dumps(metric))
        refresh(p)
        r = self.run_packet(p)
        self.assertEqual(self.check(r,'C02')['execution_state'], 'blocked-unsupported-operation')
        self.assertIsNone(self.check(r,'C02')['evidence_outcome'])

    def test_hash_mismatch(self):
        p = self.packet()
        with (p/'outcomes.jsonl').open('a') as f:
            f.write('\n')
        r = self.run_packet(p)
        self.assertIsNone(self.check(r,'C02')['evidence_outcome'])
        self.assertIn('hash', self.check(r,'C02')['explanation'].lower())

    def test_zero_denominator(self):
        p = self.packet()
        (p/'exposures.jsonl').write_text('')
        (p/'outcomes.jsonl').write_text('')
        refresh(p)
        r = self.run_packet(p)
        self.assertIsNone(self.check(r,'C02')['values']['control']['rate'])

    def test_unsupported_sql_does_not_prevent_metric(self):
        p = self.packet()
        (p/'metric.sql').write_text('SELECT arbitrary_function(user_id) FROM exposures')
        refresh(p)
        r = self.run_packet(p)
        self.assertEqual(self.check(r,'C03')['execution_state'], 'blocked-unsupported-operation')
        self.assertEqual(self.check(r,'C02')['evidence_outcome'], 'Verified')

    def test_new_run_unchanged_inputs_and_existing_output_rejected(self):
        p = self.packet()
        before = {f.name: f.read_bytes() for f in p.iterdir()}
        a = self.run_packet(p)
        b = self.run_packet(p, 'second')
        self.assertEqual(a['findings'], b['findings'])
        self.assertNotEqual(a['run_id'], b['run_id'])
        self.assertEqual(before, {f.name:f.read_bytes() for f in p.iterdir()})
        proc = subprocess.run([sys.executable, '-m','pebbles', str(p),'--output',str(self.base/'result')], cwd=ROOT, capture_output=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(json.loads((self.base/'result/report.json').read_text()), a)

if __name__ == '__main__':
    unittest.main()
