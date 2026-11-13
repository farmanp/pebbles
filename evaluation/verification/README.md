# Independent materials audit

Run from repository root: `python3 evaluation/verification/audit_materials.py`.

This stdlib-only audit was authored independently from raw packages, the plan, the declared contracts and the private answers. It does not import or read the package generator, legacy checker or any product evaluator. Private expected integers/fractions are compared with a separate per-user relational reconstruction using UTC datetimes and exact rational arithmetic. Overlays are applied in disposable temporary copies. SQL is inspected as text and never executed. Results are written only under this directory.

This directory is private evaluation evidence. Never distribute it, the oracle directory, or the repository root to participants, report preparers or an evaluator. Only the allocated packet may be admitted. The audit proves file-level separation and absent omitted artifacts, not process-level access control in a future session.

`audit-results.json` is the latest material verification, not a product run, study observation, performance benchmark or evaluation-gate pass. `evidence-report.md` explains semantic judgments and unresolved readiness requirements. The script checks the presently declared probe set; it is not a general event-processing engine and must not be reused as the Pebbles product or its sole correctness oracle.
