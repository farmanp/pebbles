# Pebbles — Business Requirements as Evaluation Datasets (BRD) v0.1

## Purpose

In this project, **business requirements are expressed as observable scenarios**, represented by datasets, the expected outcome (oracle), and the real consequence of getting them wrong. The datasets are the acceptance specification for Pebbles' first pass. Broader market demand remains a distinct, unvalidated product-discovery question.

Each dataset contract must specify:

- **Intent:** the real-world question it represents.
- **Context and grain:** what each row/event means; experiment unit; eligible population; time window.
- **Fixtures:** data to feed into the system, plus controlled changes/mutations.
- **Ground truth:** hand-authored exact answers or externally justified statistical expectations.
- **Failure risk:** what would be misleading or broken if Pebbles failed.
- **Observable acceptance:** the externally visible output to check.
- **Traceability:** which hypothesis, technical test, and gate use this dataset.

## First-pass evaluation dataset matrix

| ID | Scenario | Expected observable result | Why it matters | Status |
|---|---|---|---|---|
| BR-D01 | Healthy 50/50 checkout A/B: assigned vs exposed | v1 exposed-based conversion: control 1/3; treatment 2/3. v2 assigned-based: control 1/4; treatment 2/4. | A wrong denominator changes the meaning of a result. | Fixture included |
| BR-D02 | Repeat an exposure for one already-exposed treatment user | Treatment remains **3 distinct exposed users**, despite 4 treatment exposure rows. Duplicate is diagnosable. | Duplicate delivery must not inflate unique-user metrics. | Mutation included |
| BR-D03 | Inject an exposure for a user with no experiment assignment | Flag orphan exposure; do not silently treat it as valid. | Evidence integrity affects trust in the analysis. | Mutation included |
| BR-D04 | Sample-ratio mismatch under declared 50/50 allocation | Strongly imbalanced assignments, e.g. 800:200 of 1,000, trigger the predeclared SRM diagnostic threshold. | Misallocated groups can compromise comparisons. | Planned fixture/generator |
| BR-D05 | Metric evolves from exposed-user to assigned-user denominator | Published experiment using v1 retains v1 and its outputs; v2 is recorded separately with its own result. | Historical meaning must survive change. | Fixture and oracle included; platform test pending |
| BR-D06 | Assignment adapter replaced | A replacement satisfies stated consistency, allocation, identity, and fallbacks; identical bucket mappings only if expressly promised by the contract. | Swap implementations without silently changing treatment behavior. | Planned conformance dataset |
| BR-D07 | A/A repeated experiments with true effect = 0 | Nominal 5% false positive rate remains within a **predeclared statistical tolerance**, e.g. 3%–7% across 2,000 independent seeded simulations, under stated assumptions. | A single correct calculation cannot establish inferential reliability. | Planned simulation |
| BR-D08 | Confidence interval calibration for known simulated effects | Nominal 95% interval coverage within e.g. 93%–97% over 2,000 seeded independent trials with design assumptions recorded. | Tests analysis reliability, not only arithmetic. | Planned simulation |
| BR-D09 | Reproduce result after metric/analysis implementation upgrade | Original pinned definitions, inputs, method, settings and original analysis output stay available; replay agrees within declared tolerance or shows a documented incompatibility. | Durability is an observed property, not a slogan. | Planned integration scenario |

**Important:** Suggested statistical thresholds are provisional acceptance criteria, to be finalized before running their simulations; the simulations must match the inference procedure and assignment unit. There is no requirement that every statistical scenario pass exactly 100% of the time.

## Golden dataset BR-D01

**Business question:** Does a new checkout button improve purchase conversion for exposed users?

**Experimental design:** 8 distinct assigned users, 4 control and 4 treatment. 3 users are exposed per arm. Purchases occur after exposure. These tiny counts establish deterministic arithmetic only; they do not justify a causal claim or a statistically significant treatment effect.

**Event model:**
- `assignments.jsonl`: one assignment record per unit × experiment revision.
- `exposures.jsonl`: one event per rendered treatment encounter (can repeat per unit).
- `outcomes.jsonl`: purchase events from users, with timestamps.
- All metrics are calculated over unique users, under the experiment's specified observation window.

**Metric v1** = distinct exposed users with a valid subsequent purchase / distinct exposed users.

**Metric v2** = distinct assigned users with a qualifying purchase / distinct assigned users. In this fixture, all purchasers were exposed, but v2 is a separate estimand and is not interchangeable with v1.

| Arm | Assigned users | Exposed users | Purchasers | v1 | v2 |
|---|---:|---:|---:|---:|---:|
| Control | 4 | 3 | 1 | 33.333333% | 25% |
| Treatment | 4 | 3 | 2 | 66.666667% | 50% |

**Ground truth:** `golden_checkout/expected.json` explicitly records the expected integer counts and rational rates. This oracle is written separately from the eventual Pebbles metric implementation. Exact integer counts are preferred over floating-point rates when possible.

**Risks:** Confusing assignment with exposure, counting an event instead of a person, or interpreting a metric definition change as if it were the same measurement.

## Required dataset review gate (G0)

No engineering implementation starts from a scenario until:
1. Its business question is clear.
2. Population, unit, grain, attribution window and metric formula are explicit.
3. Its expected answer is independently specified.
4. At least one plausible failure mode has a corresponding assertion.
5. The scenario is mapped to a hypothesis and technical contract test.

A fixture is only **ready** when those five checks are documented. Dataset quality and correctness are themselves part of the evidence.

## Scope boundaries

- Synthetic datasets do not prove that real-world telemetry matches observed product behavior.
- The prototype supports simple user-randomized A/B tests; interference, switchbacks, network experiments, multiple-testing correction and sophisticated sequential stopping are future problem spaces.
- Privacy, consent, retention, and production security are required for real data but outside the synthetic first-pass demonstration.
- Customer desirability must be studied separately with actual users rather than inferred from synthetic results.
