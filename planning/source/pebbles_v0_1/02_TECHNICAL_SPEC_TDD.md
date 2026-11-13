# Pebbles — Technical Specification as Test-Driven Contracts v0.1

## Engineering objective

Build the smallest vertical slice that can process BR-D01 correctly, reject or flag BR-D02/03 anomalies as specified, preserve metric versions in BR-D05, and ultimately satisfy inference and durability scenarios. This is a **test-driven specification**: each implementation decision must be justified by a behavior to verify.

## Test-driven development loop

1. **Select a risk-bearing scenario** from the BRD and an opportunity-tree hypothesis.
2. **Write the failing test (RED)** against a stable interface and a hand-authored oracle; record how the test fails before implementation.
3. **Implement the simplest compliant behavior (GREEN)** and verify the failure disappears.
4. **Refactor without changing the contract**; rerun relevant unit, contract, and integration tests.
5. **Run the gate**, store evidence (commit, fixture version, execution result, configuration, timestamps), and decide PASS / FAIL / BLOCKED / NOT YET EVALUATED.
6. **If it fails, revisit the right level**: data, hypothesis, contract, method, or code. Do not mechanically edit tests to make them green.

## Core model and invariants

| Object | Identity / versioning | Non-negotiable behavior |
|---|---|---|
| Experiment | `experiment_id`, immutable published `revision` | Publishing freezes resolved references and configurations. |
| Variant | Stable `variant_id` scoped to an experiment | Allocations and interpretation explicitly belong to a revision. |
| Assignment | Unique `experiment_revision × assignment_unit` with policy-defined reassignment | A consistent unit is assigned under a declared algorithm and persistence policy. |
| Exposure | Distinct event ID, experiment/revision, unit, variant, timestamp | Does not imply assignment by itself; can be checked against it. |
| Metric | Stable `metric_id@version` | Numerator, denominator, eligible population, grain, time window and missingness rules are explicit. |
| Analysis run | Unique ID with exact input/data/config/method fingerprints | No silent overwrite of previously published output. |
| Decision | Unique record referencing an analysis | Conclusion and rationale remain attributable. |

First-pass experiment unit: `user_id`. Keep assignment and exposure as different facts. The system must not imply that an assigned unit necessarily saw the treatment.

## First-pass service boundaries (logical, not microservices)

```
Experiment manifest / models -- Pydantic
    -> Published revision + definition store -- SQLite + immutable JSON
    -> Assignment adapter -- GrowthBook SDK candidate
    -> Assignment / exposure / outcome data -- JSONL, then Parquet
    -> Metric registry + query generation -- DataJunction candidate
    -> Query execution -- DuckDB
    -> Analysis adapter -- SciPy / statsmodels
    -> Results and decision record -- immutable versioned artifacts
    -> Minimal UI -- Streamlit, only after core path is proven
```

**Integration risks to establish rather than assume:**
- GrowthBook SDK evaluation, exposure signaling, and bucketing semantics may not match our contract by default.
- DataJunction must demonstrably generate or expose SQL compatible with the local DuckDB data source; its registry/version semantics must satisfy the historical-pinning contract or Pebbles must keep independent frozen snapshots.
- Statistical results must record the test specification, alpha, method version, analysis population and exclusions.

## Test contracts and traceability

| Test | Input (BRD) | Arrange → Act → Assert | Gate |
|---|---|---|---|
| TC-01 Schema | BR-D01 | Invalid missing IDs/references rejected; valid manifest accepted. | G1 |
| TC-02 Publish immutability | BR-D05 | Publish revision 1; attempt modification; reject or create revision 2; v1 hash unchanged. | G1/G4 |
| TC-03 Assignment consistency | BR-D01 / D06 | Re-evaluate same unit under pinned policy; treatment remains consistent within declared conditions. | G2 |
| TC-04 Exposure semantics | BR-D01 | Assert assigned=4/4, distinct exposed=3/3; do not substitute assigned counts in v1. | G2/G3 |
| TC-05 Duplicate handling | BR-D02 | Inject repeat exposure; distinct count unaffected and duplication diagnosable. | G2/G3 |
| TC-06 Orphan validation | BR-D03 | Inject orphan exposure; event flagged/rejected, not silently counted. | G2/G3 |
| TC-07 Metric v1/v2 | BR-D01 / D05 | Query both pinned metrics; assert exact integer counts and expected rates. | G3 |
| TC-08 Statistical method | BR-D07 / D08 | Repeated seeded simulation; estimate calibration and coverage against preregistered intervals. | G3 |
| TC-09 Historical replay | BR-D05 / D09 | Freeze manifest, inputs and method; change definitions/adapter; old result unchanged and reproducible per documented tolerance. | G4 |
| TC-10 E2E | BR-D01–D05 | Run end-to-end to decision and trace every resulting artifact to its sources. | G5 |

## Quality gates / checkpoint criteria

**G0 — Evaluation-data readiness:** BRD fixture, contracts and independent expectations complete.

**G1 — Durable definitions:** schemas accepted/rejected as intended, immutable published revisions, resolvable pinned metric references; tests TC-01/02 PASS.

**G2 — Execution integrity:** assignment consistency demonstrated; duplicates and orphan exposures handled explicitly; tests TC-03/04/05/06 PASS. Note that a synthetic fixture alone does not validate GrowthBook's live SDK, which must have its own integration checks.

**G3 — Measurement and inference:** exact fixture counts and SQL outputs match oracle; metric version changes are explicit; predeclared statistical calibration and coverage meet thresholds when the inference scope is in play. TC-07/08 PASS, with no post-hoc tuning of thresholds.

**G4 — Durability:** historical replay passes after a versioned definition change and at least one controlled adapter change; provenance record is complete; TC-02/09 PASS.

**G5 — First-pass end-to-end demo:** one experiment travels design → assignment → exposure → measurement → analysis → decision and yields a machine-readable evidence report. TC-10 PASS and no unresolved critical integrity violation.

A gate's recorded status is not an averaged score. A failure on a critical invariant cannot be offset by passing unrelated tests.

## Acceptance vs. discovery

Technical completion means G0–G5 are **observably satisfied** for the agreed scope. It does not establish that Pebbles offers compelling competitive differentiation. Product demand remains a separate opportunity-tree branch with separate evidence.

## Artifacts to preserve for every evaluation execution

`scenario_id`, fixture hash and version, test ID, contract version, code commit, dependencies, seed (if randomized), observed result, expected result, status, failure diagnosis, decision, and timestamp. Store a machine-readable record and enough information to reproduce it.

## Implementation order (by dependency, not tickets)

1. Validate BR-D01's independent oracle (G0).
2. Specify/version manifests and registry (G1).
3. Write exposure and assignment adapter contract tests before wiring GrowthBook (G2).
4. Write metric SQL golden-answer tests before wiring DataJunction (G3).
5. Implement pinned analysis and quality checks (G3).
6. Change definitions and adapters and run replay (G4).
7. Produce integrated user workflow + traceable evidence report (G5).
