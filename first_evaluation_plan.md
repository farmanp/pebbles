# Pebbles first evaluation plan

Author: Farman Pirzada
Date: 2026-11-12
Status: proposed, unrun. All thresholds, staffing and budget below are proposed defaults to freeze before execution. This document specifies evaluation preparation and a later minimal build sequence; it implements no product code.

## Decision and bounded scope

Decide whether to continue a file-based evidence reviewer for product data scientists and experimentation analysts. First demonstrate correct, appropriately limited findings; then seek a directional signal that the report reduces total investigation effort compared with the analyst's ordinary workflow. Do not infer demand, production correctness, causal validity or statistically established productivity from this pilot.

Use one synthetic user-randomized checkout A/B experiment family, two arms, one primary binary conversion metric, fixed observation window and no sequential stopping. Only deterministic counts, ratios, evidence consistency and claim boundaries are scored. Do not calculate or validate significance, confidence intervals, power, SRM calibration, multiple testing, interference or treatment-effect causality. A scorecard containing inferential fields may be retained but those fields are explicitly unevaluated. The tiny eight-user seed cannot validate inference. A later inference evaluation would require a selected method, assumptions and independent simulation/calibration plan; original BR-D07/08 proposals are deferred.

## Current evidence and missing assets

Available: eight assignments, six exposure events, three purchases, metric v1/v2 prose definitions, a manifest, exact rational answers, repeat-user and orphan-exposure mutations, and a reference consistency checker. The parent agent ran the four existing checker tests successfully. They check fixture consistency only; they do not exercise Pebbles and do not enforce timestamps, attribution windows, experiment/revision isolation or all stated metric semantics.

Preparation update: [evaluation materials](evaluation/README.md) now contain scorecards, metric SQL examples, inventories, provenance metadata, notes, six canonical packages, twelve A/B forms, private per-check oracles, boundary probes, operational test recipes, and study/scoring materials. See the independent verification records for the audited scope and remaining requirements. Matched difficulty has not been validated with people; operational recipes are not product test results. The evaluator, participant evidence and results remain absent. The original `duplicate_exposure_mutation.json` adds a distinct event ID; it is a repeat encounter, not an identical-event replay.

## Proposed contracts to freeze

Use an explicit synthetic contract, not an inferred rule: experiment `checkout-button`, revision 1, unit `user_id`; control and treatment; UTC observation interval `[2026-01-01T12:00:00Z, 2026-01-02T12:00:00Z)`. A qualifying assignment/exposure must match experiment, revision, user and variant. Exposure must be at or after assignment. Metric v1 denominator is distinct valid exposed users; numerator is those users with at least one purchase strictly after their first qualifying exposure and before the exclusive window end. Metric v2 is a separately labeled comparison: assigned users and purchases strictly after assignment within the same window. Do not silently substitute v2 for v1. Zero denominator yields an undefined rate, not zero conversion.

A new event ID for the same user is a legitimate repeat encounter. Identical event-ID replay with identical fields counts once and yields an informational replay note; conflicting payloads sharing an event ID block affected metric checks until resolved. Crossovers, mismatched revisions and orphan records are surfaced with record references; valid subset counts may be stated only as subset counts under the explicit exclusion rule. An orphan relative to an export of unknown completeness does not prove faulty production assignment. Unknown identity, window or attribution semantics yield Insufficient evidence for affected checks rather than guessed defaults.

The prototype should inspect supplied SQL as evidence and compute the supported metric from the explicit structured definition using its own bounded deterministic implementation. It must not execute arbitrary supplied SQL. For this first case, the scoring rubric expects recognition of the simple row-count denominator versus distinct-user rule; unsupported SQL analysis is recorded as an operational capability limit. No claim of general SQL equivalence is in scope.

A package inventory records artifact ID, relative path, type/schema version, hash, source, export timestamp (or unknown), grain (or unknown), population/filter/window metadata, experiment/revision when known, and completeness as declared or unknown with declaration source. Unknown optional metadata is permitted and constrains only dependent checks. Preserve original files and record explicit mappings; do not fabricate metadata to satisfy admission.

Each finding records check ID/version, exact proposition, evidence locators/hashes, scope and prerequisites, calculation/reason, expected/observed values where applicable, outcome, limitations, and next useful evidence request. The request states what decision it unlocks and whether the analyst or another team could provide it. Use question-first report sections with the outcome and scope together; no experiment-wide success badge or percent passed.

## Evidence outcomes and execution records

| Field | Values and interpretation |
|---|---|
| Check evidence outcome | Verified: supported scoped proposition; Failed: sufficient comparable evidence contradicts proposition; Insufficient evidence: prerequisite evidence absent or unresolved. |
| Check execution state | Completed; blocked-invalid-input; blocked-unsupported-operation; errored. Non-completed checks have no evidence outcome, plus an explicit cause and affected proposition. |
| Run execution state | Completed; partial; failed. Partial preserves completed findings and conspicuously lists all uncompleted checks. It is never an overall analytical pass. |
| Evaluation gate | Not yet evaluated; pass; fail; blocked. These describe the evaluation, not the experiment. |

For example, E03's absent metric definition is a completed Insufficient evidence finding. Malformed JSON is an operational parse error with file/line, not proof of defective experimentation. No unexecuted check can become Verified. The report inventory lists planned check coverage so absence of a finding cannot conceal failure.

## Case matrix and independent expected results

All cases use neutral participant-facing IDs; case labels, defect flags, private expectations and withheld files stay outside the evaluated package. E00–E05 are coverage conditions, not six independent experiments. The following answers specify the tiny canonical seed; workflow forms require separately authored answers for their changed counts.

| Case | Supplied evidence and change | Required output | Forbidden conclusion |
|---|---|---|---|
| E00 — clean control | Configuration, metric v1 definition, valid SQL, accurate scorecard, assignments/exposures/outcomes, provenance and notes. Include the legitimate extra treatment encounter with a new event ID. | Assigned 4/4; distinct exposed 3/3; purchasers 1/2; rates 1/3 and 2/3. Treatment has four exposure rows but three users. Scorecard agreement Verified; repeat informational. Delivery/completeness remain unresolved. | Consequential defect from repeat encounter alone; whole experiment verified. |
| E01 — planted denominator defect | Same analytical evidence as E00. SQL and scorecard use treatment exposure-row count four, reporting 2/4 rather than required 2/3. | Failed named denominator/scorecard agreement check; cite metric definition, SQL/count rule and offending scorecard field. Recompute 2/3, difference 1/6 (16.667 percentage points). Control remains 1/3. | Production duplicate delivery proven; shipping or significant-effect recommendation. |
| E02 — summary only | Configuration and scorecard with arm numerator/denominator/rate fields (1/3 and 2/3), source metadata; no event exports or metric definition. | Verify only arithmetic identities and permitted bounds: numerator ≤ denominator and displayed rate matches fields within declared rounding. Event-level count validity, intended denominator and attribution remain Insufficient evidence. | Recomputed from events, no duplicates/crossovers, metric intention or production capture verified. |
| E03 — missing definition | Scorecard and event exports; no metric definition, SQL or notes that define denominator. Any metric reference is opaque. | State counts as record facts; show that 3 exposed versus 4 assigned per arm allow different candidate denominators. Intended conversion/scorecard semantic agreement is Insufficient evidence. Request versioned denominator, eligibility and attribution rules. | Choosing v1 from fixture knowledge or declaring the scorecard wrong solely because another denominator is possible. |
| E04 — contradictory sources | Scorecard says four distinct treatment exposed users; supplied exposure file has three. Provenance does not establish identical export scope/completeness. | Report exact conflict with both locators. Failed literal agreement proposition (“these displayed counts are equal”); Insufficient evidence on whether scope is comparable or which source is correct. Ask for aligned export filters/window/snapshot and calculation definition. | Logs authoritative; scorecard incorrect in reality; missing user certainly lost in tracking. |
| E05 — missing implementation evidence | Accurate complete-for-this-synthetic-analytical-task package, no application logs/code/SDK evidence. Explicit task asks whether treatment was actually rendered correctly. | Supported analytical checks Verified; treatment-delivery proposition Insufficient evidence with explanation. Request narrowly relevant implementation/render evidence if delivery is decision-critical; permit it to remain unresolved. | Analytical agreement proves rendering, causal validity or eligibility to ship. |

Every case has at least one claim-boundary assertion. E01 also lacks production implementation evidence; E05 is a focused probe of interpretation, not the only case with that limit. E00 is clean with respect to the declared calculation contract, not proof that production behavior is perfect.

## Focused adversarial and operational probes

Add small independent probes beside the six cases, not a generalized event-testing framework:

- Purchase before exposure, purchase exactly at exposure, purchase exactly at exclusive window end, and valid purchase just before end: exclude/include under the pinned rules and cite records.
- Exposure from another revision or a conflicting arm; orphan relative to supplied assignments: show mismatch/exclusion without claiming real-world root cause.
- Identical event replay versus legitimate repeat versus conflicting same-ID payload: distinct handling as contracted above.
- Empty events and zero denominator: report zero observed users and undefined rate, without assuming zero real-world exposure.
- Missing required evidence versus malformed file versus unsupported operation versus evaluator exception: distinct states and actionable affected-check list.
- Reorder rows and rerun unchanged inputs: canonical findings invariant apart from run metadata. Change metric version: new run and new findings, old files unchanged.
- Oversized package and timeout: visible operational failure, no fabricated or silently partial assurance.

Proposed envelope: ten files, 50 MB uncompressed, 100,000 event rows, 2 GB process memory, one worker, 60-second runtime cap; record machine and actual peak/runtime. No network and no mutation of input evidence. These limits are proposed, not measured performance claims.

## Oracle design and leakage prevention

An oracle author writes expected integer counts, rational rates, check eligibility, statuses, evidence locators, forbidden claims, and minimum additional-evidence requests independently of evaluator implementation. A second reviewer who did not write the evaluator recomputes the answer manually or with an independently constructed calculation, checks source semantics, and resolves all discrepancies before freezing the oracle. The existing checker is scaffolding, not the sole oracle reviewer.

For each package freeze a private record: case/form ID, input hashes, contract versions, intended defect or omission, expected per-check assertions, criticality, acceptable wording equivalence, and rationale. Rate comparisons prefer exact fractions; displayed percentages tolerate only stated rounding (proposed ±0.000005 on a 0–1 rate when displaying three percentage decimals). Thresholds cannot be revised after seeing results. Correct this rounding tolerance during readiness if display precision changes, documenting the reason before execution.

Keep private expectations and omitted files in a separate directory unavailable to the evaluator, report preparer and participant. Reveal only admitted artifacts per case. Assign neutral randomized packet names and prevent filenames/notes from naming the defect. Record package and evaluator versions before the run. If oracle error is discovered later, invalidate affected results, issue a new oracle version with reason and rerun; never quietly edit expectations into a pass.

Automated assertions check values, evidence dependencies, statuses and critical forbidden claims in canonical findings. Independent human scoring checks prose overclaim, explanation and participant conclusions. Two scorers adjudicate critical disagreements; uncertainty remains unresolved rather than counted correct. Score before viewing comparative time summaries where feasible.

## Analyst comparison without same-case learning

Proposed sample: six relevant analysts with recent A/B analysis experience, recruited before prototype commitment. Six users provide formative evidence, not a powered significance test. No analyst is assumed to be available today. If recruitment fails, do only the technical rehearsal and label workflow comparison Not evaluated.

Prepare two independently authored matched forms, A and B, for each E00–E05 condition: 12 cases in total. They remain variants of the checkout experiment family but use different user IDs, counts, event ordering and defect location. Cosmetic renaming alone is inadequate. Match investigation difficulty in an independent dry run; freeze after revision. Each analyst sees only two tasks, different conditions and different forms, so never sees the same underlying case or its counterpart twice. Use this proposed schedule (N = normal tools; P = same tools plus Pebbles):

| Analyst | Task 1 | Task 2 |
|---|---|---|
| 1 | E00-A, N | E01-B, P |
| 2 | E03-B, P | E02-A, N |
| 3 | E04-A, N | E05-B, P |
| 4 | E01-A, N | E02-B, P |
| 5 | E04-B, P | E03-A, N |
| 6 | E00-B, P | E05-A, N |

This covers every condition under both methods, balances first-method exposure 3/3, and yields one observation per condition/method. Within-person times compare different tasks, so case difficulty and general task learning remain limitations. Report individual paired observations and condition/form tables; do not interpret them as causal estimates. Randomly map recruited participants to schedule rows; match A/B difficulty before allocation. Use a neutral unrelated practice task for both methods, then provide no correctness feedback or cross-task discussion until both tasks finish.

Both methods start from equivalent source folders and the same task prompt: “List supported findings, consequential discrepancies, unresolved questions and the next evidence you would request; state what this does and does not justify.” Normal tools include participants' usual SQL, notebooks, spreadsheets and available diagnostics; record them. Do not remove familiar tools to improve Pebbles' apparent benefit. P adds the frozen report/evaluator only; identical moderator rules and assistance logging apply. No participant, moderator helper or report producer may consult the oracle during task execution.

Each session lasts at most 90 minutes: consent/context and ordinary-workflow inventory (10), unrelated practice (10), two tasks (25 each), and scope comprehension/debrief (20). Task cutoff is 25 minutes including case-specific preparation. Record timeout as censored/incomplete, not success at 25 minutes; any critical task left incomplete blocks a positive utility decision. Export acquisition is simulated by selecting permitted source files, so real warehouse-access costs remain unknown.

Measure per task active minutes for source selection/export preparation, mapping/packaging, investigation, interpretation, follow-up and corrections; elapsed waiting separately. Include moderator assistance and any manual report preparation as labor cost. Record participant onboarding separately and show both observed pilot total and a clearly labeled amortized scenario if useful; the primary effort result includes actual task preparation plus allocated observed onboarding/report-production effort. Do not exclude setup only from the assisted method. Shared fixture-authoring/oracle work is evaluation cost, reported separately rather than passed off as recurring user work.

A human-produced report may be used only as an explicitly labeled concierge variant; include all report-maker time, and do not claim automated accuracy, runtime or productivity. The preferred comparison is a frozen deterministic prototype once technical gates pass.

After each task, obtain two unprompted scope answers: one fact established by supplied evidence and one material fact not established. E02/E05 additionally ask whether event validation/delivery was established. Record answers before debrief. Ask for a recent analogous investigation and likely use occasion as exploratory discovery; no invented testimony or demand conclusion.

## Proposed acceptance and next decisions

| Gate | Proposed acceptance | If unmet |
|---|---|---|
| R0 — package readiness | All six cases, matched forms and probes have reviewed independent oracles; no ambiguity in critical expected behavior; no leakage; contracts/thresholds frozen. | Repair materials; do not build or run scored comparisons from ambiguous truth. |
| R1 — technical safety/correctness | Every predeclared critical assertion passes across E00–E05 and probes; all supported exact counts match; E01 defect and E04 discrepancy correctly sourced; zero critical false assurance or clean-control false defect; errors separated; canonical replay matches. | Fix contract, material or evaluator according to diagnosis and rerun affected tests. No speed trade-off. |
| R2 — comprehension | At least 80% of scope questions correct overall and zero critical claims that delivery/whole experiment was verified. | Revise report wording/structure; fresh-user retest before claiming usability. |
| R3 — workflow signal | Assisted critical defect detection and justified-conclusion coverage no worse than baseline, zero critical unsupported conclusion, no incomplete critical task; median total task effort ratio P/N ≤0.80 and at least 4/6 analysts lower total effort. | Examine preparation burden and condition-level failures; revise, narrow to checklist/concierge, or stop. |

All gates are currently **Not yet evaluated**. R3 is a proposed continuation heuristic with sparse, confounded formative observations, not a statistically significant treatment effect. Report numerators/denominators, each person's results, timeouts, assistance and outliers. Do not average away critical safety failures. A missing participant makes R3 incomplete; report observed data but do not silently lower the threshold or replace target users with internal reviewers.

If R0–R2 pass and R3 shows the proposed signal, proceed to a broader evaluation with different experiments and realistic permitted exports; investigate demand separately. If correctness passes but time fails, prefer a simpler checklist/report or narrower use case. If evidence boundaries fail, revise before expanding scope. If repeated revision cannot produce defensible findings within the cap, stop this approach. Integrations become candidates only after measured preparation friction identifies a specific valuable connection.

## Minimal later build sequence, owners and bounds

No code is implemented in this phase. Assign one evaluation lead (proposed: Farman Pirzada), one independent oracle reviewer/scorer, and one builder; builder and oracle reviewer must be different people or independent processes. Confirm actual availability before execution. The lead owns scope freeze and decision; the oracle reviewer owns truth/readiness; the builder owns operational behavior; independent scorers own judgments.

1. **Days 1–2, readiness:** draft check/report and package schema contracts; create private oracles and public packages; recruit six analysts and freeze comparison materials. No production integrations.
2. **Days 3–5, bounded prototype after authorization:** immutable file admission and inventory → prerequisite checks → v1 deterministic counts and simple SQL-denominator inspection → reconciliation → structured report. Add operation/error distinction and run provenance before any UI. A command producing JSON plus readable Markdown is sufficient.
3. **Day 6, technical exam and dry run:** run critical cases/probes, check leakage and report interpretation with an independent non-scored reviewer, repair before freeze. A changed evaluator after freeze requires rerunning relevant technical checks.
4. **Days 7–8, analyst sessions:** execute the frozen schedule, log all effort/assistance and preserve outputs.
5. **Days 9–10, adjudication and decision:** score independently, inspect effort only after quality, publish results and proceed/revise/narrow/stop decision.

Proposed ceilings: ten working days excluding recruitment delays, 60 builder hours, 16 evaluation/reviewer hours, six analyst sessions up to 90 minutes, and $600 external spending excluding labor. Track actual time by role; stop and re-scope when the cap is reached rather than silently extending into platform work. Budget availability and participants are unresolved logistics, not established commitments.

Preserve source evidence unchanged. Prepared assets are under `evaluation/packages/`, private answers under `evaluation/private-oracles/`, and check/scoring contracts under `evaluation/contracts/`. Future product-run output belongs under `evaluation/runs/<run-id>/`; no product runs exist yet. A subsequent implementation plan must enumerate actual code/dependency/file choices; this concept evaluation plan does not claim zero-decision coding readiness.

Every run record must contain case/form ID, input hashes, contract/oracle/evaluator versions, code commit, dependencies, machine, timestamps, execution/evidence/gate states, expected versus observed assertions, error diagnosis, time/labor observations, adjudication and next decision. Results append as new runs; rollback means selecting a prior version and producing a new run, never overwriting history. Unsupported package versions are explicitly rejected; no existing deployed clients or data migration is assumed.

## Readout template

For each gate: status, observed evidence, unmet assertions, limitations and decision. For each case: input version, required/observed findings, forbidden claims, provenance completeness and execution failures. For each analyst: method/order/case, tools, total and component effort, assistance, timeouts, correctness and scope answers. End with remaining uncertainty and the next smallest useful test.

Current readout: no Pebbles product or user result. The original fixture's four consistency tests passed; prepared material audit results and outstanding R0 requirements are recorded under `evaluation/verification/`. R1–R3 remain Not yet evaluated. The preparation audit does not establish matched task difficulty, participant availability, or prototype correctness.

## Sources

- [Current review input](planning/review-input.md) and [user evidence boundary](planning/source/user-evidence-boundary.txt): controlling scope.
- [Business requirements](planning/source/pebbles_v0_1/01_BUSINESS_REQUIREMENTS_EVAL_DATASETS.md): scenario/oracle discipline and tiny fixture limitations.
- [Technical contracts](planning/source/pebbles_v0_1/02_TECHNICAL_SPEC_TDD.md): provenance and explicit gate principles; original platform scope deferred.
- [Opportunity tree](planning/source/pebbles_v0_1/03_OPPORTUNITY_TREE.md): technical versus product uncertainty.
- [Goldfish synthesis](planning/goldfish_review_report.md): six independent review statuses and dispositions.
