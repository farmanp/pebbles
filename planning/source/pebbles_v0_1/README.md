# Pebbles — Foundation v0.1

**Pebbles** is a durability-by-design experimentation platform prototype. This bundle defines the first build as three linked artifacts, not a Jira backlog.

1. **[Business requirements = evaluation datasets](01_BUSINESS_REQUIREMENTS_EVAL_DATASETS.md):** What situations must the platform handle, what ground truth do we know, and what user-relevant failure does each evaluation reveal?
2. **[Technical specification = test-driven contracts](02_TECHNICAL_SPEC_TDD.md):** How will we build and prove each behavior, starting from failing, meaningful tests?
3. **[Opportunity tree = plan of work](03_OPPORTUNITY_TREE.md):** Which uncertainties, hypotheses, experiments, decisions, and evidence drive work?

## First-pass outcome

Run **one** simulated A/B experiment, correctly distinguish assignment from exposure, calculate a versioned conversion metric, perform an explicitly defined analysis, and reproduce its historical result after a metric or engine change. Preserve the chain from problem → hypothesis → evidence → decision.

**Separate discovery outcome:** Identify a validated reason for customers to choose Pebbles. A successful engineering prototype does *not* establish product-market demand.

## How the artifacts connect

`Opportunity O-xx` → `Hypothesis H-xx` → `Experiment E-xx` → `Dataset BR-Dxx` → `Contract/TDD test TC-xx` → `Gate Gx` → `Evidence/Decision`

- Datasets represent acceptance examples and known adversarial scenarios; they are *not* a substitute for production requirements, user research, or statistical calibration.
- Technical tests are linked to risks and expectations in the datasets, not arbitrary code coverage targets.
- Gates may be **PASS**, **FAIL**, **BLOCKED**, or **NOT YET EVALUATED**. Never infer PASS from an unrun test.
- Candidate stack: Python/Pydantic; SQLite; GrowthBook SDK; DataJunction; DuckDB/Parquet; SciPy/statsmodels; pytest; Streamlit. DataJunction and GrowthBook integrations have **not been validated** in this bundle.

## Included executable fixture

`evaluation_datasets/golden_checkout/` includes eight synthetic assignments, six exposures, three purchases, and hand-specified expected outcomes for metric versions v1 and v2, plus mutations for duplicate and orphan exposures.

The standalone reference checker only confirms the *test data and stated oracle agree*; it does **not** validate an integrated experimentation platform.

```bash
cd pebbles_v0_1
python -m unittest discover -s evaluation_datasets -p 'test_*.py' -v
```
