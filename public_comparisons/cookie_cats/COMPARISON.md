# First public comparison: Cookie Cats

Executed 2026-11-12. Ready as a retrospective numerical comparison with caveats, not a complete production shipping review.

## Sources and scope

The [public analyst readout](https://github.com/nsy0079/cookie-cats-ab-test/tree/9dc979bb7cb7fe82755eddc03e738a927d76b7c7) is an independent portfolio analysis, not Tactile's original company decision memo. It includes the 90,189-row public CSV and a notebook. The [dataset landing page cited by the analyst](https://www.kaggle.com/datasets/mursideyarkin/mobile-games-ab-testing-cookie-cats) is recorded as upstream provenance; this comparison uses the pinned GitHub mirror, not independently accessed production records.

Local source files, URLs, revision and SHA-256 hashes are in `source/` and `provenance.json`. The notebook was inspected as JSON and its stored outputs were compared; its code was not executed. No third-party instructions were treated as task instructions.

The experimental contrast is the game gate at level 30 versus level 40. Retention flags describe whether a player returned and played on day 1 or day 7 after installation. They are not purchase outcomes. No calendar dates or event timestamps are available. The adapter reads the CSV directly, checks fields and unique users, and retains all supplied users for the main snapshot. No sampling or synthetic events were introduced.

## Executed results

| Metric | Gate 30: all users | Gate 40: all users | Difference, treatment − control | Pebbles 95% Newcombe interval |
|---|---:|---:|---:|---:|
| Day-7 retention | 8,502 / 44,700 = 19.0201% | 8,279 / 45,489 = 18.2000% | −0.82013 pp | −1.32819 to −0.31213 pp |
| Day-1 retention | 20,034 / 44,700 = 44.8188% | 20,119 / 45,489 = 44.2283% | −0.59052 pp | −1.23919 to +0.05821 pp |

Under independent-user assumptions, the day-7 interval is below zero; day-1 includes zero. These are retrospective, unadjusted per-metric comparisons, not proof of a predeclared decision procedure or a validated guardrail family.

## Reconciliation with the readout

Notebook cell 11 (zero-based) removes every row whose rounds equal the dataset maximum. Here that is one gate-30 player, user 6390605: 49,854 rounds, day-1 false, day-7 true. Pebbles preserves that row in the main calculation and separately reproduces the analyst's 90,188-user population.

On the matching population, the day-7 difference is −0.81832 pp, with pooled z-test p = 0.001591773; day-1 difference is −0.59152 pp, with p = 0.073920760. These reproduce cell 26's rounded rates, differences, p-values and Wald confidence bounds. Pebbles independently calculates the notebook's z/Wald formula for reconciliation; its main uncertainty method remains Newcombe/Wilson. The small difference from the full-data p-values is due to the exclusion, not a calculation error.

The exclusion uses a post-assignment outcome. It is therefore visible as a sensitivity comparison rather than silently justified for retention. With or without it, day-7 points in the same negative direction. The readout's advice to retain gate 30 is directionally consistent with this result. Its bootstrap draws, Mann–Whitney engagement test, power analysis and broader business claims were not reproduced in this pass.

Against an assumed 50/50 allocation, the full-data sample-ratio p-value is 0.008608. The notebook uses its filtered population and reports about 0.0085. Both are below 0.01 but above Pebbles' 0.001 diagnostic threshold. Neither threshold establishes correct assignment; the original allocation contract and logs remain absent.

## What Pebbles refuses to conclude

The shipping summary remains blocked even if UI/API plan declarations are supplied. This snapshot path does not promote user attestations into recovered original study evidence. The absent dated plan, event-level lineage, production capture checks, monetary/uninstall guardrails, harm limits and business review remain explicit. The observed retention loss is evidence against the change, but the public snapshot is not a complete shipping dossier. Day-1 retention is a secondary measure here, not an invented safety guardrail.

## Reproduce and use

Run from the repository root:

```sh
python3 public_comparisons/cookie_cats/prepare.py
python3 -m pebbles public_comparisons/cookie_cats/packet --output runs/cookie-cats-new
```

Use a fresh output directory. `prepare.py` reads the downloaded local sources and records their hashes; it does not download or execute the notebook. In the app, choose **Cookie Cats · public analyst comparison** and **Run investigation**. The saved UI run includes raw CSV, notebook, transcribed readout contract, checks and source hashes. The format is deliberately bounded to Cookie Cats; it is not a general CSV importer.

The public-data run validates a narrow adapter and numerical reconciliation. It is not a scored analyst study, a full external validation, or independent proof of the original experiment's operation.
