"""Ordered evidence checks for ordinary experiment packages.

Each check records its own finding; the runner preserves prerequisite and error rules.
"""
from datetime import datetime, timezone
from fractions import Fraction
import re
import uuid
from . import __version__
from .core import (
    EVENTS,
    QUESTIONS,
    LIMITATION,
    VERSION_RULES,
    InputProblem,
    metric_version,
    calculate,
    sql_code_mask,
)


class Investigation:
    def __init__(self, evidence):
        self.evidence = evidence
        self.findings = {}
        self.calculation = {}
        self.metric_names = ("configuration.json", "metric.json", *EVENTS)

    def investigate(self, analysis_plan):
        self.run("C01", (), self.check_record_counts)
        self.run("C02", self.metric_names, self.check_metric)
        self.check_integrity()
        self.run("C03", ("metric.json", "metric.sql"), self.check_sql_denominator)
        self.run("C04", ("scorecard.json",), self.check_scorecard_arithmetic)
        self.run(
            "C07", ("inventory.json", "configuration.json"), self.check_source_alignment
        )
        self.run(
            "C05",
            self.metric_names + ("scorecard.json", "inventory.json"),
            self.check_scorecard_agreement,
        )
        self.run(
            "C06", ("scorecard.json", "exposures.jsonl"), self.check_exposure_counts
        )
        for cid, explanation, request in [
            (
                "C09",
                "Analytical files do not establish that treatment was actually rendered correctly. This prototype does not validate application or SDK behavior.",
                "Ask the implementation owner for relevant render/instrumentation evidence if delivery is decision-critical.",
            ),
            (
                "C10",
                "Export counts and completeness declarations do not independently establish capture of all production activity.",
                "Ask the data owner for independent capture reconciliation and source lineage if completeness is decision-critical.",
            ),
        ]:
            self.run(
                cid,
                (),
                lambda cid=cid, explanation=explanation, request=request: self.add(
                    cid, explanation, request=request, refs=("inventory.json",)
                ),
            )
        return self.report(analysis_plan)

    def add(
        self,
        cid,
        explanation,
        outcome="Insufficient evidence",
        state="Completed",
        values=None,
        refs=(),
        request=None,
    ):
        self.findings[cid] = {
            "check_id": cid,
            "check_version": "1.0.0",
            "question": QUESTIONS[cid],
            "scope": "Supplied evidence only",
            "execution_state": state,
            "evidence_outcome": outcome if state == "Completed" else None,
            "explanation": explanation,
            "values": values,
            "evidence": self.evidence.refs(refs),
            "limitations": LIMITATION,
            "next_evidence_request": request
            or (
                "Resolve the stated input limitation with the data owner."
                if state != "Completed"
                else None
            ),
        }

    def run(self, cid, names, operation):
        try:
            missing = self.evidence.require(*names)
            if missing:
                self.add(
                    cid,
                    "Required evidence is missing: " + ", ".join(missing),
                    refs=names,
                    request="Ask the analyst or metric owner for "
                    + ", ".join(missing)
                    + " to assess this check.",
                )
            else:
                operation()
        except InputProblem as ex:
            self.add(cid, str(ex), state=ex.state, refs=names)
        except (ValueError, TypeError, KeyError, IndexError) as ex:
            self.add(
                cid,
                f"Invalid supplied structure: {ex}",
                state="blocked-invalid-input",
                refs=names,
            )

    def check_record_counts(self):
        existing = [
            n for n in EVENTS if n in self.evidence.data or n in self.evidence.errors
        ]
        self.evidence.require(*existing)
        if not existing:
            self.add(
                "C01",
                "No event exports supplied; event-level counts cannot be verified.",
                request="Provide assignment, exposure and outcome exports.",
            )
            return
        v = {
            name: {
                "rows": len(self.evidence.data[name]),
                "distinct_users": len(
                    {r["user_id"] for r, _ in self.evidence.data[name]}
                ),
            }
            for name in existing
        }
        self.add(
            "C01",
            "These are literal counts in the supplied files; they do not establish metric eligibility or production coverage.",
            "Verified",
            values=v,
            refs=existing,
        )

    def check_metric(self):
        version, issue = metric_version(self.evidence)
        if issue:
            self.add(
                "C02",
                issue,
                refs=self.metric_names,
                request="Obtain an explicit, consistent versioned metric from the metric owner.",
            )
            return
        values, integrity = calculate(self.evidence, version)
        self.calculation.update(values=values, integrity=integrity, version=version)
        if integrity["conflicts"]:
            self.add(
                "C02",
                "Conflicting record identities prevent unambiguous attribution. Resolve the listed conflicts before calculating the metric.",
                state="blocked-invalid-input",
                refs=self.metric_names,
            )
        else:
            self.add(
                "C02",
                f"Computed {version} over the valid subset of supplied records using the declared assignment, identity and time rules. Zero denominators are undefined.",
                "Verified",
                values=values,
                refs=self.metric_names,
            )

    def check_record_integrity(self):
        seen, conflicts, replays = ({}, [], 0)
        for row, line in self.evidence.data["exposures.jsonl"]:
            key = row["exposure_id"]
            if key in seen:
                if seen[key] == row:
                    replays += 1
                else:
                    conflicts.append(
                        {"path": "exposures.jsonl", "record_id": key, "line": line}
                    )
            else:
                seen[key] = row
        users = {r["user_id"] for r, _ in self.evidence.data["assignments.jsonl"]}
        orphans = sorted(
            (r["exposure_id"] for r in seen.values() if r["user_id"] not in users)
        )
        values = {
            "conflicts": conflicts,
            "identical_replays": replays,
            "orphan_record_ids": orphans,
            "repeat_encounters": len(seen) - len({r["user_id"] for r in seen.values()}),
        }
        self.add(
            "C08",
            "Counted repeated IDs, repeat encounters and users absent from the supplied assignments. These are record facts only; metric eligibility and production root causes remain unresolved.",
            "Verified",
            values=values,
            refs=("assignments.jsonl", "exposures.jsonl"),
        )

    def check_integrity(self):
        if self.calculation:
            detail = self.calculation["integrity"]
            self.add(
                "C08",
                f"Identified {len(detail['excluded'])} excluded records, {len(detail['conflicts'])} identity conflicts, {detail['identical_replays']} identical replays and {detail['repeat_encounters']} repeat encounters. A repeat encounter is not itself a defect; an orphan in these files does not prove a production tracking failure.",
                "Verified",
                values=detail,
                refs=self.metric_names,
            )
        else:
            self.run(
                "C08",
                ("assignments.jsonl", "exposures.jsonl"),
                self.check_record_integrity,
            )

    def check_sql_denominator(self):
        version = self.evidence.data["metric.json"].get("version")
        if (
            version != "v1"
            or self.evidence.data["metric.json"].get("denominator")
            != VERSION_RULES["v1"]["denominator"]
        ):
            raise InputProblem(
                "SQL denominator inspection supports only the declared distinct-exposed-user v1 rule.",
                "blocked-unsupported-operation",
            )
        text = self.evidence.data["metric.sql"]
        mask = sql_code_mask(text)
        # Inspect only the supported denominator CTE; never execute arbitrary SQL.
        match = re.search(
            "\\bdenominators\\s+AS\\s*\\(\\s*SELECT\\s+variant_id\\s*,\\s*(.*?)\\s+AS\\s+denominator\\s+FROM\\s+valid\\s+GROUP\\s+BY\\s+variant_id\\s*\\)",
            mask,
            re.I | re.S,
        )
        if not match or mask.count(";") > 1:
            raise InputProblem(
                "Unsupported SQL shape. SQL was not executed; structured metric calculation remains separate.",
                "blocked-unsupported-operation",
            )
        expr = " ".join(text[match.start(1) : match.end(1)].split())
        good = re.fullmatch("COUNT\\s*\\(\\s*DISTINCT\\s+user_id\\s*\\)", expr, re.I)
        bad = re.fullmatch(
            "CASE WHEN variant_id='([^']+)' THEN COUNT\\(\\*\\) ELSE COUNT\\(DISTINCT user_id\\) END",
            expr,
            re.I,
        )
        if not good and (not bad):
            raise InputProblem(
                "Unsupported SQL denominator expression; no arbitrary SQL is executed.",
                "blocked-unsupported-operation",
            )
        explanation = (
            "The denominator expression counts distinct user IDs."
            if good
            else f"The denominator expression counts exposure rows for {bad.group(1)}; the supplied definition requires distinct users."
        )
        self.add(
            "C03",
            explanation
            + " This is expression inspection only; the rest of the SQL and general query equivalence are not verified.",
            "Verified" if good else "Failed",
            values={"expression": expr},
            refs=("metric.json", "metric.sql"),
        )

    def check_scorecard_arithmetic(self):
        score = self.evidence.data["scorecard.json"]
        if score.get("display") != "percent with 3 decimals":
            raise InputProblem(
                "Unsupported scorecard display precision.",
                "blocked-unsupported-operation",
            )
        bad = []
        for arm, row in score["arms"].items():
            n, d, rate = (row["numerator"], row["denominator"], row.get("rate_percent"))
            ok = 0 <= n <= d and _rate_matches(n, d, rate)
            if not ok:
                bad.append(arm)
        self.add(
            "C04",
            "Scorecard arithmetic is inconsistent for: " + ", ".join(bad)
            if bad
            else "Reported percentages match the scorecard’s own numerator and denominator fields within three-decimal percentage rounding. This does not validate the intended denominator.",
            "Failed" if bad else "Verified",
            values=score["arms"],
            refs=("scorecard.json",),
        )

    def check_source_alignment(self):
        names = (
            "assignments.jsonl",
            "exposures.jsonl",
            "outcomes.jsonl",
            "scorecard.json",
            "metric.json",
        )
        missing = self.evidence.require(*names)
        if missing:
            self.add(
                "C07",
                "Cannot establish shared analytical scope without "
                + ", ".join(missing),
                refs=("inventory.json",),
                request="Provide the missing definitions/exports and aligned population, filters, window and snapshot metadata.",
            )
            return
        entries = [self.evidence.entries[name] for name in names]
        valid = _scope_matches(entries, self.evidence.data["configuration.json"])
        self.add(
            "C07",
            "Inventory declares matching population, filters, window, snapshot and experiment revision. This is declared alignment, not independently proven upstream lineage."
            if valid
            else "Population, filters, window or snapshot are unknown or inconsistent. Neither the scorecard nor the export can be treated as authoritative.",
            "Verified" if valid else "Insufficient evidence",
            refs=("inventory.json", "configuration.json", "metric.json"),
            request=None
            if valid
            else "Ask the data owner for aligned export filters, population, window and snapshot metadata.",
        )

    def check_scorecard_agreement(self):
        score, metric = (
            self.evidence.data["scorecard.json"],
            self.evidence.data["metric.json"],
        )
        ref = f"{metric.get('metric_id')}@{metric.get('version')}"
        if score.get("metric_ref") != ref:
            self.add(
                "C05",
                f"Scorecard metric reference {score.get('metric_ref')!r} differs from requested {ref!r}. This does not establish that the old scorecard is wrong under its own definition.",
                "Failed",
                refs=("scorecard.json", "metric.json", "configuration.json"),
            )
            return
        calc = self.findings["C02"]
        if calc["execution_state"] != "Completed":
            raise InputProblem(
                "Metric calculation did not complete: " + calc["explanation"],
                calc["execution_state"],
            )
        if (
            calc["evidence_outcome"] != "Verified"
            or self.findings["C07"]["evidence_outcome"] != "Verified"
        ):
            self.add(
                "C05",
                "Semantic agreement is unresolved: metric definition/calculation or shared source scope is not established. A numerical discrepancy alone cannot decide which source is correct.",
                refs=self.metric_names + ("scorecard.json", "inventory.json"),
                request="Obtain a resolved metric definition and aligned source provenance from the metric/data owner.",
            )
            return
        values = self.calculation["values"]
        differences = _scorecard_differences(score, values)
        self.add(
            "C05",
            " ".join(differences)
            + " Reconcile the scorecard before relying on this measurement."
            if differences
            else "Scorecard numerators, denominators and rates agree with the declared calculation over the supplied records.",
            "Failed" if differences else "Verified",
            values={"computed": values, "reported": score["arms"]},
            refs=self.metric_names + ("scorecard.json", "inventory.json"),
            request="Ask the metric owner to correct and regenerate the scorecard using the versioned denominator rule."
            if differences
            else None,
        )

    def check_exposure_counts(self):
        score = self.evidence.data["scorecard.json"]
        values = {}
        for arm, row in score["arms"].items():
            if "distinct_exposed" not in row:
                self.add(
                    "C06",
                    "Scorecard does not supply distinct-exposed counts.",
                    refs=("scorecard.json", "exposures.jsonl"),
                )
                return
            observed = len(
                {
                    r["user_id"]
                    for r, _ in self.evidence.data["exposures.jsonl"]
                    if r["variant_id"] == arm
                }
            )
            values[arm] = {
                "reported_distinct_exposed": row["distinct_exposed"],
                "export_distinct_users": observed,
            }
        equal = all(
            (
                v["reported_distinct_exposed"] == v["export_distinct_users"]
                for v in values.values()
            )
        )
        self.add(
            "C06",
            "The displayed distinct-exposure counts equal the distinct users by arm in the exposure file."
            if equal
            else "The scorecard and exposure export contain different distinct-user counts. This establishes a literal discrepancy, not which source is correct.",
            "Verified" if equal else "Failed",
            values=values,
            refs=("scorecard.json", "exposures.jsonl"),
            request=None
            if equal
            else "Ask the data owner to reconcile source filters, snapshots and the cited counts.",
        )

    def report(self, analysis_plan):
        ordered = [self.findings[k] for k in sorted(self.findings)]
        blocked = [
            f["check_id"] for f in ordered if f["execution_state"] != "Completed"
        ]
        failed = [f["check_id"] for f in ordered if f["evidence_outcome"] == "Failed"]
        execution = (
            "failed"
            if len(blocked) == len(ordered)
            else "partial"
            if blocked
            else "Completed"
        )
        report = {
            "schema_version": "1.0.0",
            "prototype_version": __version__,
            "run_id": str(uuid.uuid4()),
            "metric_version": self.calculation.get("version"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "input_hashes": self.evidence.hashes,
            "execution_state": execution,
            "uncompleted_checks": blocked,
            "headline": "Input limitations prevented a complete investigation"
            if blocked
            else "Evidence discrepancies require investigation"
            if failed
            else "Supported checks completed; important evidence limits remain",
            "scope": LIMITATION,
            "findings": ordered,
            "not_evaluated": [
                "Production randomization implementation and interference",
                "Production treatment delivery",
                "Production capture completeness",
                "Human shipping judgment",
                "Independent report-quality scoring (C11)",
                "Cross-run replay validation (C13; demonstrated separately in tests)",
            ],
        }
        return self._assess_effect_and_decision(report, analysis_plan)

    def _assess_effect_and_decision(self, report, analysis_plan):
        from .analysis import analyze

        supplied_plan = self.evidence.data.get("configuration.json", {}).get(
            "analysis_plan"
        )
        report["analysis"] = analyze(
            report,
            analysis_plan if analysis_plan is not None else supplied_plan,
            source="user-entered run settings"
            if analysis_plan is not None
            else "configuration.json/analysis_plan",
        )
        from .decision import decide

        report["decision"] = decide(
            report,
            report["analysis"]["plan"],
            self.evidence.data.get("guardrails.json"),
            self.evidence.data.get("assignments.jsonl", []),
            self.evidence.data.get("configuration.json", {}),
            str(
                self.evidence.global_error
                or self.evidence.errors.get("guardrails.json")
            )
            if self.evidence.global_error or self.evidence.errors.get("guardrails.json")
            else None,
        )
        return report


def _scorecard_differences(score, values):
    differences = []
    if set(score["arms"]) != set(values):
        differences.append("Scorecard variants differ from the experiment variants.")
    for arm, v in values.items():
        row = score["arms"].get(arm)
        if row is None:
            continue
        if (row["numerator"], row["denominator"]) != (
            v["numerator"],
            v["denominator"],
        ):
            differences.append(
                f"{arm}: reported {row['numerator']}/{row['denominator']}; supported calculation {v['numerator']}/{v['denominator']} ({v['rate_percent']}%)."
            )
        elif v["denominator"] and not _rate_matches(
            v["numerator"], v["denominator"], row.get("rate_percent")
        ):
            differences.append(
                f"{arm}: displayed percentage differs from the supported calculation."
            )
        elif not v["denominator"] and row.get("rate_percent") is not None:
            differences.append(f"{arm}: zero denominator requires an undefined rate.")
    return differences


def _rate_matches(numerator, denominator, rate_percent):
    """Compare displayed percentages at the scorecard's three-decimal precision."""
    if denominator == 0:
        return rate_percent is None
    if denominator < 0 or rate_percent is None:
        return False
    difference = abs(
        Fraction(str(rate_percent)) / 100 - Fraction(numerator, denominator)
    )
    return difference <= Fraction(5, 1_000_000)


def _scope_matches(entries, config):
    keys = (
        "population",
        "filters",
        "window",
        "export_timestamp",
        "experiment_id",
        "revision",
    )
    baseline = entries[0]
    for key in keys:
        for entry in entries:
            if entry.get(key) in (None, "", "unknown") or entry.get(
                key
            ) != baseline.get(key):
                return False
    return (
        baseline["experiment_id"] == config["experiment_id"]
        and baseline["revision"] == config["revision"]
        and baseline["window"]
        == {"start": config["window_start"], "end_exclusive": config["window_end"]}
    )
