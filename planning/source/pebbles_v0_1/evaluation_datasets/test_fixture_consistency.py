"""Check the hand-authored oracle and fixture are internally consistent.
These tests do NOT exercise Pebbles, DataJunction, or GrowthBook.
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent / "golden_checkout"

def read_jsonl(name):
    return [json.loads(line) for line in (ROOT / name).read_text().splitlines() if line]

class FixtureConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = read_jsonl("assignments.jsonl")
        cls.e = read_jsonl("exposures.jsonl")
        cls.o = read_jsonl("outcomes.jsonl")
        cls.expected = json.loads((ROOT / "expected.json").read_text())

    def test_base_counts_match_hand_authored_oracle(self):
        owners = {r['user_id']: r['variant_id'] for r in self.a}
        purchased = {r['user_id'] for r in self.o if r['event_type']=='purchase'}
        for arm in ('control','treatment'):
            assigned = {r['user_id'] for r in self.a if r['variant_id']==arm}
            exposed = {r['user_id'] for r in self.e if r['variant_id']==arm}
            buyers = purchased & assigned
            gold = self.expected['base'][arm]
            self.assertEqual(len(assigned),gold['assigned'])
            self.assertEqual(len(exposed),gold['distinct_exposed'])
            self.assertEqual(len(buyers),gold['purchasers'])
            self.assertEqual((len(purchased & exposed),len(exposed)),
                (gold['metric_v1']['numerator'],gold['metric_v1']['denominator']))
            self.assertEqual((len(buyers),len(assigned)),
                (gold['metric_v2']['numerator'],gold['metric_v2']['denominator']))
            self.assertTrue(exposed <= assigned)
            self.assertTrue(all(owners[u] == arm for u in exposed))

    def test_duplicate_exposure_detectable_without_double_counting(self):
        mutation=json.loads((ROOT/'duplicate_exposure_mutation.json').read_text())['record']
        es=self.e+[mutation]
        treatment=[r for r in es if r['variant_id']=='treatment']
        self.assertEqual(len(treatment),4)
        self.assertEqual(len({r['user_id'] for r in treatment}),3)
        self.assertEqual(len({r['exposure_id'] for r in es}),len(es))

    def test_orphan_exposure_is_invalid(self):
        mutation=json.loads((ROOT/'orphan_exposure_mutation.json').read_text())['record']
        assigned={r['user_id'] for r in self.a}
        self.assertNotIn(mutation['user_id'],assigned)

    def test_metric_versions_intentionally_differ(self):
        for arm in ('control','treatment'):
            x=self.expected['base'][arm]
            self.assertNotEqual(x['metric_v1']['denominator'], x['metric_v2']['denominator'])

if __name__ == '__main__':
    unittest.main()
