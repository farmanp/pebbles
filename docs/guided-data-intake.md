# Guided CSV intake — M3 first slice

Implemented 2026-11-13. Start **New investigation → Import a CSV**. Upload an ordinary UTF-8 comma-separated CSV, map user ID, variant and binary outcome, name control/treatment values, and confirm experiment identity, metric meaning, population, observation window and design. Validate the mapping, inspect counts by arm, then run.

## Scope and behavior

- One row per user, two arms, one binary outcome (0/1 or true/false, case-insensitive with surrounding whitespace stripped for outcome parsing). Up to 100,000 rows and 20 MB. At least two users per arm. Other columns remain in the original source but are not analyzed.
- Missing values, duplicate users, unknown variants, nonbinary outcomes, duplicate/empty headers, malformed row lengths and blank records block analysis. No rows are silently dropped or deduplicated. Invalid UTF-8 is rejected; BOM and original source bytes are preserved.
- Confirmed fixed-horizon independent-user binary designs receive descriptive rates and a conditional 95% Newcombe/Wilson difference interval. Clustered, sequential and unknown designs are unsupported. Higher/lower is not automatically better, and no practical-benefit threshold is inferred.
- Pebbles creates source.csv, import.json and inventory.json internally. Original filename, mapping recipe version, declarations and source fingerprints are saved with the run and exports. No event timestamps, exposure records or missing outcomes are fabricated.
- Original plan, randomization/assignment implementation, production completeness, guardrails and cost review remain unresolved. CSV ingestion cannot identify omitted users without reference evidence. Shipping remains blocked for this snapshot path.
- Attach a run to an experiment workspace. Open the run and choose **Import corrected CSV with this mapping** to upload a replacement CSV, reconfirm scope, select the workspace and explain the correction. This creates a child run and reuses the existing comparison/follow-up system. Originals remain unchanged. File naming alone does not count as a changed analytical setting.
- Mapping reuse is from a saved run, not a standalone shared recipe catalog. This slice does not import a separate analyst readout/reference, guardrails or original plans through the wizard. Existing prepared-package routes retain those capabilities.

## Problem tree and remaining milestone gates

OP-2 records explicit meaning and scope; OP-3 validates row integrity; OP-4 supports reproducible calculation; OP-5 rejects unsupported designs; OP-6 preserves source/mapping/revision history; OP-7 removes manual package authoring. OP-1 usefulness remains untested with humans.

This completes the bounded import mechanics, not the entire M3 real-export acceptance criterion. No representative company export or human analyst session has run. M4 reviewed recommendation and decision handoff remains the next major build milestone; original-plan/reference intake can be expanded based on actual export friction.

## Computer Use evidence

Uploaded the controlled Cookie Cats missing-user CSV (85,189 rows), mapped userid/version/retention_7 and gate_30/gate_40, and recorded retrospective exercise assumptions. Unknown design correctly disabled running. With the supported exercise design declared, the UI generated and saved the investigation without any hand-authored special files.

Created a workspace, attached the run, reopened it, reused its mapping, uploaded the 90,189-row reference as corrected evidence, and ran a linked revision. Treatment users increased from 40,489 to 45,489 while positives stayed 8,279. Difference changed from +1.427 pp (95% interval +0.892 to +1.963) to −0.820 pp (−1.328 to −0.312). Shipping stayed blocked. Reopened the workspace after server restart and observed both results and lineage. Final rerun used reviewed input handling and settings comparison.

This is an AI-operated controlled demonstration, not recovered production evidence, independent defect discovery, or a human pilot. Earlier 3,800-user pilot packets are different fixtures; this walkthrough uses the 5,000-user public controlled case.

Tests cover CSV structure, invalid/missing/duplicate values, unsupported design and required confirmation, source BOM hashes, mapping changes versus filename-only changes, HTTP preview/import/revision, immutable originals and export lineage. Review found BOM stripping and silent blank records; both were fixed.

Final verification: **62 tests passed**. Source bytes and hashes matched both uploaded files. Original run `c773c060-d274-4c58-a211-76d267c7ca68`; final child `efa952e1-0426-4dad-845b-a5e19b91e577`. Final browser comparison showed unchanged analysis settings. [Screenshot](../pilot-self-try/guided-intake-comparison.jpg).
