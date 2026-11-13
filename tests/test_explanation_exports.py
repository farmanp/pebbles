import unittest
from pathlib import Path
from pebbles.core import investigate
from pebbles.report import markdown, html_report


class ExplanationExports(unittest.TestCase):
    def test_pilot_explanations_survive_export(self):
        root = Path(__file__).resolve().parents[1]
        for packet, action in [('r-609', 'control denominator: reported 40,594, supplied 30,394'),
                               ('r-172', 'gate_40: 3,800 missing users, 0 retained')]:
            report = investigate(root/'evaluation/analyst-pilot-v1/packets'/packet/'evidence')
            self.assertEqual(report['decision']['status'], 'blocked')
            self.assertEqual(report['discrepancy']['reference_conclusion'], 'lower_retention')
            self.assertIn(action, report['decision']['next_action'])
            for text in [markdown(report), html_report(report)]:
                self.assertIn(action, text)
                self.assertIn('Supplied reference', text)
                self.assertIn('does not establish that its population matches', text)
                self.assertNotIn('Analyst-matched difference', text)
                self.assertNotIn('p-value is 0.000000', text)
                if packet == 'r-172':
                    self.assertIn('must not be used for the intended-population conclusion', text)
            if packet == 'r-172':
                self.assertEqual(report['public_comparison']['srm']['display_p_value'], '< 0.000001')
