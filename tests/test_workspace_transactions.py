"""A failed action must not persist a partial mutation or an audit event."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pebbles.workspace import access
import test_revisions


class WorkspaceTransactions(unittest.TestCase):
    def test_failed_revision_rolls_back_attachment_and_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage = Path(tmp)
            experiment = access(storage, {"action": "create", "name": "Checkout"})[
                "experiment"
            ]
            runs = {
                "parent": test_revisions.run(),
                "child": test_revisions.run("Verified"),
            }

            def action(name, **fields):
                return access(
                    storage,
                    {"action": name, "experiment_id": experiment["id"], **fields},
                    runs.__getitem__,
                )

            action("attach", run_id="parent")
            action("track", run_id="parent", finding_id="P06", request="Correct export")
            runs["child"]["revision"] = {
                "experiment_id": experiment["id"],
                "parent_run_id": "parent",
                "reason": "Correction",
            }
            before = access(storage)
            with patch(
                "pebbles.workspace._recheck_followups",
                side_effect=ValueError("Cannot recheck"),
            ):
                with self.assertRaisesRegex(ValueError, "Cannot recheck"):
                    action(
                        "revision",
                        run_id="child",
                        parent_run_id="parent",
                        reason="Correction",
                    )
            self.assertEqual(access(storage), before)
            result = action(
                "revision", run_id="child", parent_run_id="parent", reason="Correction"
            )["experiment"]
            self.assertEqual(result["runs"], ["parent", "child"])
            self.assertEqual(
                len(result["events"]), len(before["experiments"][0]["events"]) + 1
            )

    def test_invalid_update_preserves_followup_and_event_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage = Path(tmp)
            experiment = access(storage, {"action": "create", "name": "Example"})[
                "experiment"
            ]
            body = {
                "action": "update",
                "experiment_id": experiment["id"],
                "followup_id": "missing",
            }
            before = access(storage)
            with self.assertRaisesRegex(ValueError, "Unknown follow-up"):
                access(storage, body)
            self.assertEqual(access(storage), before)
