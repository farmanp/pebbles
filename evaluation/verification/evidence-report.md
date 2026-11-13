# Independent evaluation-material evidence report

Audit date: 2026-11-12 America/Denver (2026-11-13 UTC). Reviewer: independent audit agent; no package-generator algorithm, legacy checker or product evaluator read/imported. Environment: Python 3.14.2, macOS 26.4 arm64.

Command: `python3 evaluation/verification/audit_materials.py`

Observed result: exit 0; 1629 assertions, 18 packages, 0 failures. All 16 declarative overlays were applied in temporary copies and independently inspected/recomputed; six operational recipes were reviewed as materials only. No product was implemented or executed.

## Package evidence

Values below are control/treatment. For E03 they are private reviewer candidate record facts, never a determination of the intended metric. E02 has no admitted events: only internal scorecard arithmetic was checked.

| Case/form | Packet | Assigned | Distinct exposed | Purchasers | Scoped v1 rate or limitation |
|---|---|---|---|---|---|
| E00/canonical | p-7c41 | 4/4 | 3/3 | 1/2 | 1/3, 2/3 |
| E01/canonical | p-a893 | 4/4 | 3/3 | 1/2 | 1/3, 2/3 |
| E02/canonical | p-39f2 | unavailable | unavailable | unavailable | scorecard arithmetic only: 1/3, 2/3 |
| E03/canonical | p-c617 | 4/4 | 3/3 | 1/2 | definition absent; intention unresolved |
| E04/canonical | p-82da | 4/4 | 3/3 | 1/2 | 1/3, 2/3 |
| E05/canonical | p-5b09 | 4/4 | 3/3 | 1/2 | 1/3, 2/3 |
| E00/A | p-d140 | 6/7 | 4/5 | 2/3 | 1/2, 3/5 |
| E00/B | p-296e | 8/6 | 6/4 | 3/1 | 1/2, 1/4 |
| E01/A | p-ef32 | 7/8 | 5/6 | 2/4 | 2/5, 2/3 |
| E01/B | p-61ab | 9/7 | 7/5 | 4/2 | 4/7, 2/5 |
| E02/A | p-948c | unavailable | unavailable | unavailable | scorecard arithmetic only: 1/4, 4/6 |
| E02/B | p-b705 | unavailable | unavailable | unavailable | scorecard arithmetic only: 3/7, 2/5 |
| E03/A | p-03de | 7/9 | 5/6 | 3/2 | definition absent; intention unresolved |
| E03/B | p-f821 | 10/8 | 7/5 | 2/3 | definition absent; intention unresolved |
| E04/A | p-475a | 8/9 | 5/7 | 2/4 | 2/5, 4/7 |
| E04/B | p-ac60 | 10/7 | 8/4 | 5/1 | 5/8, 1/4 |
| E05/A | p-186f | 9/8 | 6/5 | 2/3 | 1/3, 3/5 |
| E05/B | p-73bd | 7/10 | 5/8 | 3/4 | 3/5, 1/2 |

## Semantic inspection and corrections

- All physical package files, including inventory, fit the ten-file envelope. Full packets contain ten files, not eleven. All private input hashes, public inventory hashes and assertion-reference hashes match; inventory coverage exactly matches actual files. No symlinks, case labels, private answer keys or omitted evidence were found in neutral packets by the declared checks. E02 omits events/definition/SQL; E03 omits definition/SQL/defining notes. File separation is verified; runtime mount isolation remains a future requirement.
- Temporal reconstruction uses valid assignment in the half-open interval, matched experiment/revision/user/arm exposure at or after assignment, then purchases strictly after first exposure and before end. The outcome user join is explicitly supplied in definitions; missing outcome scope fields are not invented. Before/exact-exposure/exact-end purchases are excluded; just-before-end is included. Revision mismatch, conflicting arm and orphan overlays leave the valid subset unchanged. Replay deduplicates by identical payload and ID; distinct IDs remain encounters; conflicting IDs are diagnosed without yielding an affected control metric.
- E01 canonical treatment recomputes 2/3 versus 2/4, difference 1/6. A moves the row denominator defect to control (2/5 versus 2/7, difference 4/35); B uses treatment (2/5 versus 2/8, difference 3/20). SQL branches match these arms. The SQL review is limited to the supplied distinct-user versus row-count expression, not general SQL equivalence, replay handling or execution.
- E04 literal distinct-count inequality is Failed; comparability and semantic source authority remain Insufficient evidence. The independently recomputed C02 value is scoped to admitted event records. Neither the logs nor scorecard is deemed authoritative in production. E00/E05 analytical matches do not establish delivery or completeness. E03 candidate counts do not establish intended v1 conversion.
- Initial semantic review found missing C02/C05 assignment/configuration evidence locators and C05 inventory dependency. The author added them; the audit then rechecked all hashes/dependencies. Conflicting-ID probe now separates completed C08 diagnosis from blocked C02/C05 execution. The version-change probe separates v2 calculation from failed metric-reference equality; it does not claim the original v1 scorecard is wrong under v1. Resource recipes now use the decimal contract limits rather than MiB/GiB labels.
- Malformed JSON overlay independently produces a parser error at scorecard.json line 2. Unsupported-SQL overlay contains the declared unsupported function and was never executed. Missing definition remains completed Insufficient evidence. Empty exposure/outcome files produce zero observed denominator and undefined rate. Reordered raw events give identical independent counts, while unchanged source hashes are preserved. v2 separately yields 1/4 and 1/2. These are materials/reconstruction checks, not proof of a future evaluator’s operational behavior.
- The corrected schedule has 12 unique condition/form tasks, each condition under N and P, six people each with one of each method and different conditions/forms, and 3/3 first-method balance. The source schedule’s E02 twice-P/E04 twice-N defect was repaired before results. The 28 comprehension questions imply a minimum 23 correct for 80%; critical assurance failures remain disqualifying. Effort includes preparation, assistance, report production and observed onboarding; waiting is separate. Median ratio and 4/6 threshold agree across rubric and scoring instructions.

## Outstanding readiness and execution evidence

R0 remains Not yet evaluated. Numerical variants exist and differ in counts, arm location and ordering, but no independent human matched-difficulty dry run has occurred. Review all A/B difficulty and timing before freeze; a structural difference is not evidence of matched difficulty. Confirm actual roles, recruitment, budget, isolation and immutable version approval. Private records retain draft/pending freeze status intentionally.

R1–R3 remain Not yet evaluated. No prototype findings, false-assurance prose scores, runtime/peak-memory measurement, operational resource/timeout/exception run, participant comprehension, labor observation or utility result exists. Operational recipes are explicit future stimuli, not executed tests. The audit uses an independently written bounded reconstruction, not a production-quality evaluator; it does not prove support for unrepresented malformed records or arbitrary SQL.

Future sessions must expose only the allocated packet and participant instructions, never this verification directory, all packets at once, private oracles or private schedules. Human scorers must review claim boundaries and adjudicate disagreements before time summaries. All product gates and human difficulty gates require their own evidence.
