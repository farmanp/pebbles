# Pebbles evaluation materials

This directory contains synthetic evaluation inputs and study materials, not a Pebbles product implementation or customer results.

## Material boundaries

- `packages/`: evidence packets. Give the evaluator or participant only the selected packet, never this whole workspace.
- `private-oracles/`: case identities, expected answers, forbidden claims and probe expectations. Restricted study-author/scorer material; never include in evaluator or participant context.
- `contracts/`: check semantics and scoring rules.
- `study/`: participant and moderator materials. Moderator schedules and scoring aids are private; use only the designated participant materials in sessions.
- `tools/`: fixture construction utilities, not the product evaluator.
- `verification/`: independently constructed checks and their evidence.

Folder separation is organizational, not an access-control boundary. A future evaluator with workspace access could read private answers. For scored runs, copy just the selected packet and the permitted public contract into an isolated working directory and deny access to private material. Do not use filenames, case mappings or private notes as model context.

## Readiness

The [independent material audit](verification/evidence-report.md) passed 1,629 assertions across all 18 packets, with zero failures; it also checked 16 probe overlays and reviewed six operational recipes. Rerun it from the project root with `python3 evaluation/verification/audit_materials.py`. Passing this audit verifies the authored inputs and expected answers; it does not pass product gates R1–R3. Full R0 still requires an independent human difficulty dry run of the matched forms and final freeze. Analyst recruitment and an evaluator remain prerequisites for the workflow study.

Start with the [check contracts](contracts/checks.md), [scoring rubric](contracts/scoring-rubric.json), and [study instructions](study/README.md). The [verification report](verification/evidence-report.md) records repaired issues, audited scope and remaining requirements. All verification reports and private mappings must stay out of participant/evaluator context.

The controlling plan is [first_evaluation_plan.md](../first_evaluation_plan.md). Subsequent material revisions must update hashes and oracle versions and rerun the independent audit. Preserve previous scored-run inputs and never silently change answers after seeing results.
