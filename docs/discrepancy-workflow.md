# Cookie Cats discrepancy investigation

The product question is whether Pebbles can explain a consequential disagreement, trace its evidence, and distinguish numerical impact from shipping readiness. This increment is a bounded deterministic investigator, not a general SQL/pipeline debugger or an analyst-value study.

## Use

Open the local app and choose Cookie Cats control case, case A, B or C. Run the investigation. The first section shows reported counts, fresh calculation from the supplied export, and fresh calculation from the supplied reference. Reasons, affected counts and user IDs, source-file buttons, conclusion impact and next steps follow. The original public readout remains below for comparison. Saved JSON/HTML/Markdown include the investigation.

| Case | Controlled problem | Reported difference | Reference difference | Retention conclusion |
|---|---|---:|---:|---|
| Control | None | −0.820 pp | −0.820 pp | Lower → lower |
| A | Control denominator 60,000 instead of 44,700 | +4.030 pp | −0.820 pp | Higher → lower |
| B | 5,000 non-retained gate-40 users missing | +1.427 pp | −0.820 pp | Higher → lower |
| C | Day-1 counts labeled day-7 | −0.591 pp | −0.820 pp | Inconclusive → lower |

Conclusions use whether a retrospective 95% Newcombe interval is above zero, below zero, or includes zero. They are not business-goal or shipping classifications. All shipping reviews remain blocked on the public dataset's original evidence gaps. The original analyst is not responsible for these deliberately introduced problems.

## Evidence and diagnosis

`investigation.json` is a separate controlled reported claim: schema version 1.0.0, controlled_exercise true, metric retention_1 or retention_7, and exactly two reported arms with integer retained_users/users. `reference.csv` uses the same strictly validated Cookie Cats schema as `cookie_cats.csv`. Both snapshots and the claim are fingerprinted in inventory.json. No event timestamps are invented.

The engine joins snapshots by userid to identify missing, extra and changed rows. It compares reported numerators/denominators with independent counts from the requested metric, and checks whether counts exactly match the other supported retention metric. It distinguishes agreement, denominator mismatch, population mismatch, metric mismatch and unresolved count differences. It does not invent an upstream pipeline cause when only a mismatch is established. Extra reported-arm fields are rejected rather than mistaken for numerical disagreement.

The reference is explicitly supplied comparison evidence, not a newly established production source of truth. A missing reference blocks investigation. A match between a report and its export does not prove the export complete. If population and reported-count discrepancies coexist, both are called out. Case labels, notes, fixture recipes and expected diagnoses do not drive the runtime diagnosis.

The generator is `public_comparisons/cookie_cats/build_cases.py`. It preserves the baseline packet and original notebook/readout, writes separate exercise packets, and records expectations under `evaluation/discrepancy/expected.json`. Runtime imports only product modules and selected evidence. Tests also rename packets and remove explanatory notes. This is not a blind external benchmark: these are engineered cases for supported failure patterns.

## Verification and limits

49 tests pass, including the clean case, three problem types, unknown-count refusal, malformed count fields, missing reference, existing workflow regressions, HTTP persistence and evidence fingerprints. Four cases were executed and saved under evaluation/discrepancy/runs; summary results are in evaluation/discrepancy/results.json. The missing-user case and its source-file preview were verified in the browser. Independent review found and prompted a fix for extra-field false discrepancies. HTTP testing also caught newline normalization breaking CSV hashes; example loading now preserves exact UTF-8 bytes.

We have not tested analyst speed, comprehension, general unseen defects, arbitrary metrics, SQL lineage or real production data completeness. Next: give an analyst a controlled case with and without this workflow and score the correct defect, evidence explanation, decision impact and time—not merely whether the final number matches.

## Problem tree

OP-3 identifies population and record problems; OP-4 reconciles calculations and definitions; OP-5 exposes conclusion impact. OP-2/6 preserve the metric claim, source fingerprints and replay. OP-7 provides the investigation UI. OP-1 and OP-7's user-value hypotheses remain unvalidated until an analyst evaluation runs.
