"""Validate binary guardrail evidence and estimate acceptable-harm intervals."""
from .analysis import compare_proportions, numeric


def assess_guardrails(report, plan, evidence, assignments, config, evidence_error=None):
    """Return metric assessments and family-level blockers in declaration order."""
    blocks = []
    specs, valid_ids = _guardrail_specs(plan, blocks)
    metrics, data_error = _evidence_metrics(evidence, config, evidence_error)
    if data_error:
        blocks.append(str(data_error))
    people, data_error = _assigned_population(assignments, data_error)
    if data_error and str(data_error) not in blocks:
        blocks.append(str(data_error))
    inference_ok = (
        report.get("analysis", {}).get("status", "blocked") != "blocked"
        and report.get("execution_state") == "Completed"
        and all(
            plan.get(key) is True
            for key in ("guardrails_predeclared", "guardrails_complete")
        )
    )
    assessments = []
    for spec in specs:
        spec = spec if isinstance(spec, dict) else {}
        metric = next(
            (metric for metric in metrics if metric["id"] == spec.get("id")), None
        )
        assessments.append(
            _assess_guardrail(
                spec,
                metric,
                people,
                plan,
                valid_ids,
                data_error,
                inference_ok,
                len(specs),
            )
        )
    return assessments, blocks


def _guardrail_specs(plan, blocks):
    specs = plan.get("guardrails")
    if not isinstance(specs, list) or not 1 <= len(specs) <= 10:
        blocks.append(
            "Declare between one and ten required binary guardrails; an empty set is not evidence of safety."
        )
        specs = []
    ids = [s.get("id") if isinstance(s, dict) else None for s in specs]
    valid_ids = all(isinstance(i, str) and i.strip() for i in ids) and len(
        set(i for i in ids if isinstance(i, str))
    ) == len(ids)
    if not valid_ids:
        blocks.append("Guardrail IDs must be nonempty and unique.")
    return specs, valid_ids


def _evidence_metrics(evidence, config, evidence_error):
    data_error = evidence_error
    if not isinstance(evidence, dict):
        data_error = (
            data_error
            or "Supply guardrails.json with complete per-user binary observations."
        )
    elif evidence.get("schema_version") != "1.0.0":
        data_error = "Unsupported guardrail evidence version."
    elif any(
        evidence.get(k) != config.get(k) or config.get(k) is None
        for k in ("experiment_id", "revision", "window_start", "window_end")
    ):
        data_error = "Guardrail experiment, revision and observation window must match the primary experiment."
    metrics = evidence.get("metrics") if isinstance(evidence, dict) else None
    if (
        not isinstance(metrics, list)
        or len(metrics) > 10
        or any(
            not isinstance(m, dict) or not isinstance(m.get("id"), str)
            for m in (metrics or [])
        )
    ):
        data_error = (
            data_error
            or "Guardrail evidence needs a list of at most ten named metrics."
        )
        metrics = []
    if len({m["id"] for m in metrics}) != len(metrics):
        data_error = "Duplicate metric IDs in guardrail evidence."
    if (
        sum(
            len(m.get("rows", [])) if isinstance(m.get("rows"), list) else 0
            for m in metrics
        )
        > 100_000
    ):
        data_error = "Guardrail evidence exceeds 100,000 observations."
    return metrics, data_error


def _assigned_population(assignments, data_error):
    people = {}
    for row, _ in assignments or []:
        uid, arm = row.get("user_id"), row.get("variant_id")
        if uid in people and people[uid] != arm:
            data_error = "Conflicting assignment variants prevent guardrail analysis."
        people[uid] = arm
    return people, data_error


def _assess_guardrail(
    spec, metric, people, plan, valid_ids, data_error, inference_ok, family_size
):
    ident = spec.get("id")
    name = spec.get("name")
    result = {
        "id": ident,
        "name": name if isinstance(name, str) and name.strip() else str(ident),
        "status": "blocked",
        "comparison": None,
        "max_harm_pp": spec.get("max_harm_pp"),
        "direction": spec.get("direction"),
        "explanation": "",
        "source": "guardrails.json",
        "definition": None,
    }
    error = _contract_error(spec, metric, valid_ids)
    observed, row_error = _observations(metric, people, data_error)
    error = error or row_error or data_error
    if not inference_ok:
        error = (
            error
            or "Resolve primary evidence and guardrail study declarations before interpreting this guardrail."
        )
    control, treatment = plan.get("control"), plan.get("treatment")
    if not error and (not people or set(people.values()) != {control, treatment}):
        error = "Assignment population must contain exactly the selected two arms."
    if error:
        result["explanation"] = str(error)
        return result
    _compare_guardrail(
        result, spec, metric, observed, people, control, treatment, family_size
    )
    return result


def _contract_error(spec, metric, valid_ids):
    margin = spec.get("max_harm_pp")
    if (
        not valid_ids
        or spec.get("direction") not in ("lower", "higher")
        or not numeric(margin)
        or not 0 <= margin <= 100
    ):
        return "Use a unique metric ID, higher/lower direction, and a finite harm limit from 0 to 100 percentage points."
    if not metric:
        return "Required metric observations are missing."
    if (
        not isinstance(metric.get("definition"), str)
        or not metric["definition"].strip()
    ):
        return "A versioned metric definition is required."
    if not isinstance(metric.get("version"), str) or not metric["version"].strip():
        return "A metric version is required."
    if any(spec.get(key) != metric.get(key) for key in ("version", "definition")):
        return (
            "Evidence definition/version differs from the declared guardrail contract."
        )
    return None


def _observations(metric, people, data_error):
    rows = metric.get("rows") if metric else None
    if not isinstance(rows, list):
        return {}, "Complete per-user observations are required."
    if data_error:
        return {}, None
    observed = {}
    for row in rows:
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("user_id"), str)
            or type(row.get("value")) is not bool
        ):
            return (
                observed,
                "Each observation needs a user_id and a literal true/false value.",
            )
        uid = row["user_id"]
        if uid in observed:
            return observed, "Duplicate user observations must be reconciled."
        observed[uid] = row["value"]
    if set(observed) != set(people):
        return (
            observed,
            "Observations must cover exactly the assigned population; missing users are not treated as false.",
        )
    return observed, None


def _compare_guardrail(
    result, spec, metric, observed, people, control, treatment, family_size
):
    counts = {
        arm: (
            sum(observed[u] for u in people if people[u] == arm),
            sum(a == arm for a in people.values()),
        )
        for arm in (control, treatment)
    }
    comparison = compare_proportions(
        *counts[control], *counts[treatment], confidence=1 - 0.05 / family_size
    )
    lower, upper = comparison["difference_ci"]
    if spec["direction"] == "higher":
        lower, upper = -upper, -lower
    result.update(
        comparison=comparison,
        harm_interval=[lower, upper],
        definition=metric["definition"],
        metric_version=metric["version"],
    )
    margin = spec["max_harm_pp"]
    limit = margin / 100
    if upper < limit:
        result["status"] = "within_limit"
        explanation = "The full harm interval stays below the acceptable-harm limit."
    elif lower > limit:
        result["status"] = "harm"
        explanation = "The full harm interval exceeds the acceptable-harm limit."
    else:
        result["status"] = "uncertain"
        explanation = (
            "The interval includes unacceptable harm; safety has not been established."
        )
    result["explanation"] = (
        f"Control {100*comparison['control_rate']:.2f}%, treatment {100*comparison['treatment_rate']:.2f}%. "
        f"Harm-oriented interval {100*lower:+.2f} to {100*upper:+.2f} percentage points; acceptable harm {margin:g} points. "
        + explanation
    )
