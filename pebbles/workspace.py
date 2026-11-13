"""Local investigation workflow metadata. Never mutates analytical run artifacts."""
import json
import sqlite3
import uuid
from datetime import datetime, timezone

STATUSES = ("open", "waiting for evidence", "ready to recheck", "resolved", "dismissed")


def text(body, key, limit=4000, required=False):
    value = body.get(key, "")
    if (
        not isinstance(value, str)
        or len(value) > limit
        or (required and not value.strip())
    ):
        raise ValueError(
            f'{key} must be {"nonempty " if required else ""}text, at most {limit} characters.'
        )
    return value.strip()


def access(storage, body=None, read_run=None):
    """Apply one action and its audit event in a single database transaction."""
    with sqlite3.connect(storage / "workspace.sqlite", timeout=10) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS workspace (id INTEGER PRIMARY KEY, data TEXT NOT NULL)"
        )
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT data FROM workspace WHERE id=1").fetchone()
        data = json.loads(row[0]) if row else {"experiments": []}
        if body is None:
            return data
        now = datetime.now(timezone.utc).isoformat()
        action = body.get("action")
        if action == "create":
            experiment = _create(data, body, now)
        else:
            experiment = next(
                (
                    item
                    for item in data["experiments"]
                    if item["id"] == body.get("experiment_id")
                ),
                None,
            )
            if experiment is None:
                raise ValueError("Unknown experiment.")
            handler = ACTIONS.get(action) if isinstance(action, str) else None
            if handler is None:
                raise ValueError("Unknown workspace action.")
            handler(experiment, body, now, read_run)
        experiment["events"].append(
            {
                "at": now,
                "action": action,
                "details": {
                    key: value
                    for key, value in body.items()
                    if key not in ("action", "experiment_id", "content")
                },
            }
        )
        db.execute("INSERT OR REPLACE INTO workspace VALUES (1,?)", (json.dumps(data),))
        return {"experiment": experiment}


def _create(data, body, now):
    experiment = {
        "id": str(uuid.uuid4()),
        "name": text(body, "name", 120, True),
        "owner": text(body, "owner", 120),
        "created_at": now,
        "runs": [],
        "followups": [],
        "events": [],
    }
    data["experiments"].append(experiment)
    return experiment


def _attach(experiment, body, now, read_run):
    run_id = text(body, "run_id", 36, True)
    read_run(run_id)
    if run_id in experiment["runs"]:
        raise ValueError("This run is already attached.")
    experiment["runs"].append(run_id)


def _track(experiment, body, now, read_run):
    run_id = text(body, "run_id", 36, True)
    run = read_run(run_id)
    if run_id not in experiment["runs"]:
        raise ValueError("Attach the run before tracking its finding.")
    finding_id = text(body, "finding_id", 80, True)
    finding = next((f for f in run["findings"] if f["check_id"] == finding_id), None)
    if finding is None:
        raise ValueError("Unknown finding in this run.")
    if any(
        (
            f["run_id"] == run_id and f["finding_id"] == finding_id
            for f in experiment["followups"]
        )
    ):
        raise ValueError("This finding is already tracked in this experiment.")
    experiment["followups"].append(
        {
            "id": str(uuid.uuid4()),
            "run_id": run_id,
            "finding_id": finding_id,
            "question": finding["question"],
            "check_outcome": finding["evidence_outcome"] or finding["execution_state"],
            "request": text(body, "request", 4000, True),
            "owner": text(body, "owner", 120),
            "notes": text(body, "notes"),
            "status": "open",
            "revision": 1,
            "updated_at": now,
        }
    )


def _receive(experiment, body, now, read_run):
    from .received import receive

    receive(experiment, body, now, text)


def _revision(experiment, body, now, read_run):
    from .revisions import compare_runs

    parent_id = text(body, "parent_run_id", 36, True)
    child_id = text(body, "run_id", 36, True)
    reason = text(body, "reason", 4000, True)
    if parent_id not in experiment["runs"]:
        raise ValueError("Parent run is not attached to this experiment.")
    if child_id in experiment["runs"]:
        raise ValueError("Revision already attached.")
    from .received import linked_receipt

    receipt = linked_receipt(experiment, body)
    parent, child = (read_run(parent_id), read_run(child_id))
    lineage = child.get("revision") or {}
    if (
        lineage.get("parent_run_id") != parent_id
        or lineage.get("experiment_id") != experiment["id"]
        or lineage.get("reason") != reason
    ):
        raise ValueError("Revision lineage does not match the saved run.")
    if receipt is not None:
        if any((lineage.get(k) != body.get(k) for k in ("followup_id", "receipt_id"))):
            raise ValueError("Received evidence lineage does not match.")
        if child.get("input_hashes", {}).get("source.csv") != receipt["sha256"]:
            raise ValueError("Rerun source does not match received evidence.")
        receipt["runs"].append(child_id)
    comparison = compare_runs(parent, child)
    experiment["runs"].append(child_id)
    experiment.setdefault("revisions", []).append(
        {
            "parent_run_id": parent_id,
            "run_id": child_id,
            "reason": reason,
            "created_at": now,
            "comparison": comparison,
            **{k: body[k] for k in ("followup_id", "receipt_id") if k in body},
        }
    )
    _recheck_followups(experiment, parent_id, child_id, comparison, now)


def _recommend(experiment, body, now, read_run):
    from .handoff import create, report_fingerprint

    run_id = text(body, "run_id", 36, True)
    if run_id not in experiment["runs"]:
        raise ValueError("Choose an attached run.")
    run = read_run(run_id)
    decision = create(experiment, body, run, now, text)
    decision["report_fingerprints"] = {
        rid: report_fingerprint(read_run(rid)) for rid in experiment["runs"]
    }
    experiment.setdefault("decisions", []).append(decision)


def _review(experiment, body, now, read_run):
    from .handoff import REVIEWS, needs_renewal

    decision = next(
        (
            d
            for d in experiment.get("decisions", [])
            if d["id"] == body.get("decision_id")
        ),
        None,
    )
    if decision is None:
        raise ValueError("Unknown recommendation.")
    if decision.get("review"):
        raise ValueError(
            "This review is already recorded. Create a new recommendation to change it."
        )
    if needs_renewal(experiment, decision):
        raise ValueError(
            "New evidence was attached or received. Create a new recommendation against the current evidence before review."
        )
    if body.get("outcome") not in REVIEWS:
        raise ValueError("Choose agree, request changes or disagree.")
    if body.get("confirmed") is not True:
        raise ValueError("Confirm review of the cited run and unresolved evidence.")
    decision["review"] = {
        "reviewer": text(body, "reviewer", 120, True),
        "outcome": body["outcome"],
        "rationale": text(body, "rationale", 4000, True),
        "at": now,
    }


def _update(experiment, body, now, read_run):
    followup = next(
        (f for f in experiment["followups"] if f["id"] == body.get("followup_id")), None
    )
    if followup is None:
        raise ValueError("Unknown follow-up.")
    if (
        type(body.get("revision")) is not int
        or body["revision"] != followup["revision"]
    ):
        raise ValueError(
            "This follow-up changed elsewhere. Reopen the workspace before editing."
        )
    status = body.get("status")
    if status not in STATUSES:
        raise ValueError("Unknown workflow status.")
    notes = text(body, "notes", required=status in ("resolved", "dismissed"))
    followup.update(
        owner=text(body, "owner", 120),
        request=text(body, "request", 4000, True),
        notes=notes,
        status=status,
        revision=followup["revision"] + 1,
        updated_at=now,
    )


def _recheck_followups(experiment, parent_id, child_id, comparison, now):
    for f in experiment["followups"]:
        previous = f.get("rechecks", [])
        if f["run_id"] != parent_id and (
            not any((r["run_id"] == parent_id for r in previous))
        ):
            continue
        check = next(
            (c for c in comparison["findings"] if c["check_id"] == f["finding_id"]),
            None,
        )
        outcome = check["after"] if check else "Not evaluated"
        f.setdefault("rechecks", []).append(
            {"run_id": child_id, "at": now, "outcome": outcome}
        )
        # A fresh pass needs review; a regression reopens even a closed finding.
        f["status"] = "ready to recheck" if outcome == "Verified" else "open"
        f["revision"] += 1
        f["updated_at"] = now


ACTIONS = {
    "attach": _attach,
    "track": _track,
    "receive": _receive,
    "revision": _revision,
    "recommend": _recommend,
    "review": _review,
    "update": _update,
}
