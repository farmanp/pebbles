# Analyst evaluation kit — pilot v1

**Prepared, not run. No participant outcomes or customer-value findings exist.** Start with one unscored pilot, revise the materials, then freeze a version before recruiting a scored cohort. Technical checks are recorded separately in `verification/`.

The question is whether an analyst using their usual tools **plus Pebbles** can reach an evidence-supported investigation conclusion more reliably and quickly than with their usual tools alone.

## Start the unscored pilot

1. Facilitator reads [protocol](facilitator/protocol.md), [rubric](facilitator/rubric.md), and [session script](facilitator/session-script.md). Keep this kit private.
2. Rehearse the handoff: `python3 evaluation/analyst-pilot-v1/tools/stage_trial.py --practice --destination /tmp/pebbles-practice`. On the participant machine, open its `START.md`.
3. Stage P00 period 1, then period 2 separately: `python3 evaluation/analyst-pilot-v1/tools/stage_trial.py --session P00 --period 1 --destination /tmp/pebbles-pilot-1`. Change period and destination for the second task. Transfer only that staged folder to the participant.
4. Run the 60-minute pilot script. Capture observations and submitted responses; rehearse scoring without treating the scores as study evidence.
5. Record changes, resolve loading or interpretation failures, and freeze a new manifest before any scored sessions. Do not silently change packets mid-study.

## Contents

- `packets/`: eight matched scored cases, two pilot cases, one practice case. Neutral identifiers; each has task instructions and an evidence folder.
- `distribute/`: individual packet ZIPs. These contain no answer keys, but the staging tool is the preferred handoff.
- `participant/`: common instructions and response template.
- `facilitator/`: private case map, answer keys, schedule, rubric and protocol. **Never distribute this directory or the repository.**
- [Results workbook](../../outputs/analyst-pilot-v1/results.xlsx): planned slots only; outcome fields are blank. See [field definitions](facilitator/results-guide.md).
- `tools/`: reproducible construction, independent count audit and clean session staging.

Folder separation is not access control. Use a separate participant account or machine without access to this repository, keys, prior runs or the original demo server. Staged Pebbles has no example gallery and starts with fresh history; its source remains inspectable and is not an adversarial examination system.

## Connection to the problem tree

**OP-1 / OP-7:** this is the first test of analyst usefulness and workflow, not another demonstration of calculations. **OP-3:** recognize missing population evidence. **OP-4:** reconcile denominators and metric definitions. **OP-5:** explain whether the retention conclusion changes without claiming shipping readiness. **OP-2 / OP-6:** preserve definitions, source hashes, protocol version and submitted reasoning. See the [active tree](../../OPPORTUNITY_TREE.md).

All cases are controlled derivatives of Cookie Cats, not new randomized experiments or errors attributed to the original analyst. The clean forms reverse arm labels deliberately. Matching uses fixed stratified sampling; equivalent task difficulty is an assumption for the pilot to examine. This narrow, familiar benchmark cannot establish general defect discovery or real-company shipping readiness.
