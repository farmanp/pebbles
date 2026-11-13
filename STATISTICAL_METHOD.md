# Treatment-effect analysis, version 1

The implementation in `pebbles/analysis.py` compares two independent binary conversion proportions using a two-sided 95% Newcombe interval combining Wilson score bounds. The implementation follows the method documented by [statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.confint_proportions_2indep.html), with [reference implementation](https://www.statsmodels.org/stable/_modules/statsmodels/stats/proportion.html). Runtime requires only the Python standard library.

The analysis requires one primary metric and fixed analysis time chosen before inspecting results, independent randomized users with no interference, completed collection, complete assigned-population outcomes, and the supported assigned-user v2 metric. The UI captures these declarations; checking a box does not prove them. Material failed checks, required unresolved checks, unsupported supplied SQL, conflicting or excluded records, and invalid inputs block inference. SQL inspection currently supports only the older exposed-user expression: supplying unsupported v2 SQL blocks inference conservatively. SQL is optional when the supported explicit metric definition is supplied.

An assignment-count Pearson chi-square diagnostic uses the declared allocation, requires expected counts of at least five per arm and blocks at p < 0.001. Passing does not establish randomization correctness. See Microsoft's [sample-ratio mismatch explanation](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/).

The interval's lower bound must exceed the predeclared practical goal for a worthwhile-improvement conclusion. An upper bound below zero supports harm; an upper bound below the goal supports below-goal; otherwise the result is inconclusive. A blocked run can display descriptive rates but no inferential interval. Relative lift is undefined when control conversion is zero. The conclusion concerns the primary metric; guardrails and declared risk/cost review are assessed separately in the decision summary; no shipping authorization is produced.

## Executed validation

32 tests cover investigation, HTTP persistence, rendering, analysis decisions, interval checks, edge cases and refusal conditions. Fresh review identified numeric overflow and invalid assignment-count handling; fixes have regression tests. The positive example was run through the actual browser UI.

`evaluation/statistical/protocol.json` was saved before execution. `calibrate.py` simulates 2,000 independent trials per scenario with 1,000 users per arm. Under equal 20% conversion, interval coverage is 95.55% and the two-sided zero-exclusion rate is 4.45%. Under 20% versus 23%, coverage is 95.50%. Both satisfy the saved protocol. The known-effect zero-exclusion rate is power, not a false-positive rate. `results.json` records the seed, protocol and implementation hashes.

These simulations cover two bounded regimes. They do not establish calibration across every sample size or baseline, peeking, clustering, interference or multiple comparisons. They are partial evidence toward original CP-3/G3 and BR-D07/BR-D08, not a full platform checkpoint or an analyst study.

## Guardrail extension

Guardrails are versioned binary observations for every assigned user, with exact experiment/revision/window matching. Higher-is-better metrics reverse the sign of treatment-minus-control to express harm. Lower-is-better metrics retain it. The upper harm bound must be strictly below the predeclared acceptable-harm margin to pass; a lower bound above the margin indicates unacceptable harm; crossing/touching the margin is uncertain.

For m required guardrails (1–10), each Newcombe interval uses confidence 1−0.05/m. The adjustment follows the [NIST Bonferroni simultaneous-interval rule](https://www.itl.nist.gov/div898/handbook/prc/section4/prc473.htm). Since the underlying intervals are approximate, this is nominal family coverage, not an exact finite-sample guarantee. It does not require independence between the guardrail metrics. Independence between randomized users remains required. The primary interval remains separately 95%; no joint 95% coverage claim is made for the primary-plus-guardrail collection.

The prior 4,000-trial primary calibration was rerun after parameterizing confidence and reproduced its results. Direction, adjusted-interval widening, known harm/uncertainty and blocking behavior have deterministic tests. The expanded guardrail family has not received a broad simulation calibration. Binary flags and their definitions are supplied assertions: Pebbles checks population completeness and calculates rates but does not verify upstream event-to-flag logic. Cost/risk review is likewise an analyst declaration.
