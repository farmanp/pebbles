# Pebbles — Opportunity Tree & Evidence-Driven Work Plan v0.1

## North-star outcomes

**Delivery O-0:** One A/B experiment can be defined, assigned, measured, analyzed, and reproduced after system change, with an auditable problem → hypothesis → evidence → decision trail.

**Product O-P:** Identify a customer problem sufficiently important that a team would choose Pebbles rather than its current experimentation workflow. **Unvalidated**; do not use technical passing tests as evidence of adoption.

## Opportunity tree

```
Pebbles — durable experimentation (outcomes O-0 and O-P)
|
+-- OP-1: People struggle to move from questions to defensible decisions [customer hypothesis]
|   +-- Q1: Which workflow step is painful enough to motivate switching?
|   +-- H1: End-to-end question-to-decision traceability reduces manual reconstruction.
|   +-- E1: Workflow interviews + walkthrough comparisons (not yet run)
|   +-- Gate P1: Observe repeated, consequential pain and a measurable improvement.
|
+-- OP-2: Experiments lose meaning when definitions evolve [technical hypothesis]
|   +-- Q2: Can pinned definitions preserve historical meaning?
|   +-- H2: Versioned manifests, metrics, and immutable revisions do so.
|   +-- E2: BR-D01 and BR-D05 -> TC-01, TC-02, TC-07, TC-09
|   +-- Gate: G0, G1, G4
|
+-- OP-3: Assignment and exposure evidence can disagree or degrade
|   +-- Q3: Can we correctly distinguish and validate them?
|   +-- H3: Explicit event models and contracts prevent silent miscounting.
|   +-- E3: BR-D01, BR-D02, BR-D03, BR-D06 -> TC-03–06
|   +-- Gate: G2
|
+-- OP-4: Metric calculations can differ across systems
|   +-- Q4: Can DataJunction produce the intended DuckDB-compatible metric?
|   +-- H4a: DataJunction registry and generated SQL satisfy the contract.
|   +-- H4b: A local frozen metric schema + SQL is needed as compatibility layer.
|   +-- E4: BR-D01 / BR-D05 -> TC-07; compare implementations
|   +-- Gate: G3, with explicit decision on DataJunction fit
|
+-- OP-5: A correct number can still support invalid conclusions
|   +-- Q5: Is inference calibrated and quality independently checked?
|   +-- H5: Explicit methods + SRM and simulation diagnostics catch key risks.
|   +-- E5: BR-D04, BR-D07, BR-D08 -> TC-08 and quality checks
|   +-- Gate: G3
|
+-- OP-6: Replaceable components can rewrite historical output
|   +-- Q6: Can we replay after metric or engine changes?
|   +-- H6: Frozen evidence and conformance interfaces allow faithful replay.
|   +-- E6: BR-D05 / BR-D06 / BR-D09 -> TC-02, TC-09
|   +-- Gate: G4
|
+-- OP-7: Individual modules may work but the complete workflow may fail
    +-- Q7: Can one experiment move end-to-end with full traceability?
    +-- H7: A narrow vertical slice exposes integration failures early.
    +-- E7: BR-D01–D05 -> TC-10
    +-- Gate: G5
```

## Adaptive work protocol

Each opportunity node owns:

`problem → decisive question → hypotheses (including alternatives) → experiment → dataset → method/tools → tests → evals → quality gate → evidence → decision → next question`

Do not create work solely because a library, endpoint, or UI component could be implemented. Work exists to reduce uncertainty, satisfy a demonstrated contract, or validate an outcome.

A failed experiment can lead to **revise hypothesis**, **repair implementation**, **change dataset**, **discard approach**, or **investigate an unknown**. It does not automatically imply another engineering task.

## First-pass work sequence

| Checkpoint | Critical uncertainty resolved | Evidence required | Status |
|---|---|---|---|
| CP-0 | Do we know what correct outputs are? | BR-D01 oracle + mutation expectations reviewed (G0). | Oracle fixture included; review pending |
| CP-1 | Can a versioned experiment be published? | TC-01/02 + immutable references (G1). | Not built |
| CP-2 | Can we trust assignments and exposures? | TC-03–06 incl. real GrowthBook adapter (G2). | Not built |
| CP-3 | Can we measure and analyze correctly? | TC-07/08; DataJunction compatibility proof; diagnostics (G3). | Not built |
| CP-4 | Can history survive a change? | TC-09; frozen evidence and replay report (G4). | Not built |
| CP-5 | Does the whole path work? | TC-10, linked decision record, evidence report (G5). | Not built |
| CP-P | Does the product solve a valued customer problem? | Qualitative workflow evidence and predefined improvement criterion. | Not researched |

## Decision record template

```
Opportunity ID:
Question:
Hypothesis tested:
Dataset / evidence source:
Method and implementation versions:
Tests and eval results:
Quality-gate status:
What was learned:
What remains uncertain:
Decision: proceed | revise | reject | investigate
Next highest-value uncertainty:
```

## Immediate next move

**CP-0 → CP-1.** Treat the included golden checkout fixture as a proposed acceptance case. Review its meaning, then write failing manifest/registry tests. Only then implement the models and registry. Product discovery OP-1 may run in parallel; neither should be conflated with the other.
