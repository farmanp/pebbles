"""Decision-policy regressions at the public entry point."""
import unittest
from unittest.mock import patch

from pebbles.decision import decide
import test_decision


class DecisionPolicy(unittest.TestCase):
    def test_primary_harm_remains_adverse_when_guardrail_evidence_is_missing(self):
        report, plan, _, assignments, config = test_decision.Decision().fixture()
        report["analysis"]["status"] = "harm"
        result = decide(report, plan, None, assignments, config)
        self.assertEqual(result["status"], "do_not_ship")
        self.assertEqual(result["guardrails"][0]["status"], "blocked")
        self.assertTrue(result["blockers"])

    def test_family_and_assignment_errors_both_remain_visible(self):
        report, plan, evidence, assignments, config = test_decision.Decision().fixture()
        evidence["schema_version"] = "unsupported"
        assignments.append(({"user_id": "control0", "variant_id": "treatment"}, 0))
        result = decide(report, plan, evidence, assignments, config)
        self.assertIn("Unsupported guardrail evidence version.", result["blockers"])
        conflict = "Conflicting assignment variants prevent guardrail analysis."
        self.assertIn(conflict, result["blockers"])
        self.assertEqual(result["guardrails"][0]["explanation"], conflict)
        self.assertIsNone(result["guardrails"][0]["comparison"])

    def test_contract_error_takes_precedence_over_invalid_rows(self):
        report, plan, evidence, assignments, config = test_decision.Decision().fixture()
        evidence["metrics"][0]["definition"] = "Changed definition"
        evidence["metrics"][0]["rows"][0]["value"] = 1
        result = decide(report, plan, evidence, assignments, config)
        self.assertEqual(
            result["guardrails"][0]["explanation"],
            "Evidence definition/version differs from the declared guardrail contract.",
        )
        self.assertEqual(result["status"], "blocked")

    def test_interval_touching_harm_limit_does_not_establish_safety(self):
        report, plan, evidence, assignments, config = test_decision.Decision().fixture()
        for interval in ([0, 0.02], [0.02, 0.04]):
            with self.subTest(interval=interval), patch(
                "pebbles.guardrails.compare_proportions",
                return_value={
                    "control_rate": 0.01,
                    "treatment_rate": 0.02,
                    "difference_ci": interval,
                },
            ):
                result = decide(report, plan, evidence, assignments, config)
                self.assertEqual(result["guardrails"][0]["status"], "uncertain")
                self.assertEqual(result["status"], "blocked")
