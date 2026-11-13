# Facilitator protocol — PRIVATE

Status: planned. One unscored pilot first; then a descriptive study with four analysts, optionally six if decided before the scored cohort starts. Recruit product data scientists or experimentation analysts who regularly interpret A/B tests. The pilot participant does not join the scored cohort. Record relevant experience and prior Cookie Cats familiarity without collecting unnecessary personal information.

## Design

Use P00 for the pilot. For scored sessions use S01–S04, or S01–S06. Randomly assign participants to those session IDs before opening responses. Each scored analyst gets four cases, one per family, two Usual and two Pebbles. Each family appears equally often in both conditions across the four- and six-person schedules. Form and order are balanced in the four-person core; the six-person extension is not a fully balanced Latin square. Do not claim independent observations from 16 or 24 tasks: tasks are nested within people and share a source dataset.

Both conditions receive identical files for a given packet. Pebbles is an addition to usual tools, not a restriction on scripting. Apply participant tool rules consistently. Give everyone the same practice and training before timing. Supply only the current packet; collect the response and close its workspace before releasing the next. No correctness feedback between scored tasks. Record technical help and deviations. Stop a scored task at 900 seconds; submit partial work. A technical failure remains in the log and is reported separately, never silently removed or replaced by a successful retry.

The intended reference is stipulated by the task, not verified production truth. The auxiliary notebook/readout describes a prepared reference calculation with a maximum-rounds exclusion; the primary task is the claim in investigation.json against the full intended reference. This distinction is explained equally in both conditions. No original predeclared plan, logging proof, guardrails or implementation review is supplied. All shipping conclusions remain limited even when retention agrees or improves.

## Outcomes and scoring

Primary: justified successful investigations and false-assurance counts, reported by condition and participant. Success requires 2/2 on diagnosis, evidence and decision impact, with no false assurance. Report denominators and every timeout/technical failure. Secondary: elapsed time for successful tasks, assistance, and observations. Correct-only time is selection-biased; accompany it with the capped-resolution measure assigning 900 seconds to unsuccessful submitted tasks and timeouts. That measure is an evaluation convention, not observed time to a correct answer.

Use two independent scorers if available. Copy responses to neutral response IDs and remove condition/tool references where feasible without deleting evidence. Keep the identity mapping private. Score before revealing condition, record initial scores separately, then reconcile disagreements with written reasons. Complete blinding may be impossible because responses reference Pebbles; record this limitation. A single scorer is acceptable for pilot rehearsal, not an independent reliability check.

This small study is exploratory: show paired participant results, task types, raw counts and ranges. Do not infer population-level speed gains, statistical significance, general defect coverage or shipping safety. Do not pick a favorable success threshold after observing results. Advance to a larger study only after reviewing failures, false assurance and case difficulty; this pilot does not have a product go/no-go threshold.

## Freeze and provenance

Before scored sessions, freeze protocol, rubric, packets and application files with the audit tool, save its manifest under a new version, and archive the exact staged runtimes. Record facilitator, dates, app/kit version, assigned session and deviations. Pilot changes require a new version; do not regenerate already-used packets in place. Public data provenance is in public_comparisons/cookie_cats/COMPARISON.md and source hashes in verification/build-status.json. Answer keys are construction-based expectations; technical execution is not participant evidence.
