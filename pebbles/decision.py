"""Combine primary, guardrail and business evidence into a shipping recommendation."""
from .guardrails import assess_guardrails

LIMITS = "A conditional analyst recommendation, not authorization to deploy. Binary observations and study/review declarations are supplied evidence; Pebbles does not independently verify production capture, randomization, rendering or the business review."


def decide(report, plan, evidence, assignments, config, evidence_error=None):
    """Keep evidence checks separate from the final recommendation policy."""
    result = _new_decision(plan)
    support, blocks = result["supporting"], result["blockers"]
    primary = report.get("analysis", {})
    _review_primary(primary, support, blocks)
    plan = plan if isinstance(plan, dict) else {}
    _review_plan(plan, support, blocks)
    guardrails, evidence_blockers = assess_guardrails(
        report, plan, evidence, assignments, config, evidence_error
    )
    result["guardrails"] = guardrails
    blocks.extend(evidence_blockers)
    for guardrail in guardrails:
        messages = support if guardrail["status"] == "within_limit" else blocks
        messages.append(guardrail["name"] + ": " + guardrail["explanation"])
    adverse = primary.get("status") in ("harm", "below_threshold") or any(
        guardrail["status"] == "harm" for guardrail in guardrails
    )
    _set_recommendation(result, adverse)
    return result


def _new_decision(plan):
    return {
        "version": "1.0.0",
        "status": "blocked",
        "title": "Not ready for a shipping recommendation.",
        "supporting": [],
        "blockers": [],
        "unresolved": [
            "Production capture, randomization and treatment rendering are not independently verified.",
            "Cost and implementation review is an analyst declaration, not an automated audit.",
        ],
        "guardrails": [],
        "limitations": LIMITS,
        "plan": plan,
        "problem_tree": {
            "branch": "OP-1 / OP-5",
            "supporting": ["OP-2", "OP-3", "OP-4", "OP-6", "OP-7"],
        },
        "method": "Newcombe/Wilson with Bonferroni adjustment across the declared guardrail family; primary interval remains separate.",
    }


def _review_primary(primary, support, blocks):
    primary_status = primary.get("status", "blocked")
    if primary_status == "improvement":
        support.append(
            "Primary conversion: the entire 95% interval exceeds the predeclared worthwhile-improvement goal."
        )
    else:
        blocks.append(
            "Primary metric: "
            + primary.get("title", "Treatment effect has not been assessed.")
        )
        blocks.extend(primary.get("blockers", []))


def _review_plan(plan, support, blocks):
    for key, message in [
        (
            "guardrails_predeclared",
            "Confirm guardrail definitions, directions and acceptable harm limits were chosen before inspecting results.",
        ),
        (
            "guardrails_complete",
            "Confirm complete binary observations for every assigned user over the declared window.",
        ),
        (
            "guardrails_set_complete",
            "Confirm the declared guardrails cover all decision-critical metrics; omitted metrics are not assessed.",
        ),
        (
            "business_review_complete",
            "Complete the cost and implementation-risk review.",
        ),
    ]:
        if plan.get(key) is not True:
            blocks.append(message)
    notes = plan.get("business_review_notes")
    if not isinstance(notes, str) or not notes.strip():
        blocks.append(
            "Record the rationale for accepting costs and implementation risks."
        )
    elif plan.get("business_review_complete") is True:
        support.append(
            "Analyst-declared cost and implementation review: " + notes.strip()
        )


def _set_recommendation(result, adverse):
    result["blockers"] = list(dict.fromkeys(result["blockers"]))
    if adverse:
        result.update(
            status="do_not_ship",
            title="Evidence argues against shipping this change.",
            next_action="Address the failed primary goal or harmful guardrail before considering a new experiment. Resolve any additional blockers listed below.",
        )
    elif not result["blockers"]:
        result.update(
            status="supported",
            title="Evidence supports a conditional shipping recommendation.",
            next_action="The analyst can recommend shipping under the saved assumptions and review rationale. Confirm operational rollout and monitoring before deployment.",
        )
    else:
        result[
            "next_action"
        ] = "Resolve the blockers and run a new investigation. Do not equate an uncertain or missing guardrail with safety."
