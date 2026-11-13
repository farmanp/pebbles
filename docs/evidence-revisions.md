# Evidence revisions and rerun comparison — M2

Implemented and verified 2026-11-13. In **Experiment workspace**, select an experiment and use **Revise evidence and rerun**. Choose an attached parent run, enter a correction reason and revision name, then upload a complete revised evidence package including a valid inventory.json. Click **Run evidence revision**.

## Behavior

- Each revision creates a new run with its own saved evidence and reports. The original run and files are preserved. Experiment, parent run and reason are recorded in the new JSON, HTML and Markdown exports.
- This initial interface replaces the entire evidence package; it does not merge partial uploads or repair inventory hashes. Existing user-entered analysis settings are retained. Otherwise the new package configuration supplies the settings. Confirm that the chosen parent and new evidence describe the same experiment; Pebbles cannot independently establish that identity from arbitrary files.
- The experiment comparison shows added/removed/changed file hashes, before/after check outcomes, effect estimates and intervals, population counts, analysis settings/method versions, shipping status and blockers. Details retain both old and new values. Multiple simultaneous changes do not establish which change caused a result difference.
- For controlled reference comparisons, distinguish **reported claim**, **supplied export** and **supplied reference**. Repairing an export can resolve disagreement without changing the reference-based conclusion.
- Tracked findings linked to the parent (or previously rechecked against it) receive a new recheck record. Verified checks become **ready to recheck** for human review; they are not automatically resolved. Failed, missing, unknown or uncompleted checks reopen the follow-up. The original check outcome remains visible.
- Human closure still requires a rationale and does not change analytical findings. A subsequent adverse or missing recheck reopens a previously closed follow-up. Branches are retained as separate comparisons; the latest processed recheck is shown on the follow-up, not claimed to be universally authoritative.
- No reviewed shipping-decision workflow is claimed. M4 remains separate. Existing archived reports are not rewritten.

## Executed Computer Use walkthrough

Used the existing “Cookie Cats · workspace walkthrough” experiment and parent run `0a47a51f-033e-4251-9a0c-4335b78a9275`. Prepared a separately labeled controlled correction: restored the 3,800 omitted gate_40 users from the supplied reference, regenerated the reported treatment denominator, and updated inventory fingerprints. The original study packets were not changed. This is fixture repair for the demonstration, not recovered production evidence or proof of the upstream cause.

Through the browser, selected the parent, entered the reason/name, uploaded all seven corrected files and ran the revision. New run: `ade655ec-b60b-4013-9f76-79e1a507c660`.

Observed:

- Treatment export users changed **30,769 → 34,569**; retained users stayed **6,291**.
- P02 readout reproduction and P06 discrepancy checks changed **Failed → Verified**.
- The reported claim changed **higher retention → lower retention**.
- The supplied-reference estimate remained **−0.818 percentage points**, with interval **−1.401 to −0.236**.
- Shipping status remained **blocked → blocked**, with missing plan, instrumentation, guardrail and business-review evidence still listed.
- The tracked P06 follow-up became **ready to recheck**, while its original outcome remained Failed. The request for upstream explanation remained recorded; no human resolution was asserted.
- Reloaded the page, reopened both original and revised runs, then restarted the server and reopened the comparison. Lineage, comparison and follow-up state persisted.

[Saved comparison screenshot](../pilot-self-try/revision-comparison.jpg).

## Verification and limits

55 automated tests passed. Coverage includes removed/uncompleted checks not counting as resolution, follow-up regression reopening, duplicate/lineage checks, immutable original results, ordinary snapshot and primary-analysis effect/interval summaries, HTTP revision creation and exports, and persistence across server restart. Verified saved original evidence hashes and new export lineage after the browser run. Independent review identified two effect-display gaps, both fixed and covered.

The browser exercise is an AI-operated demonstration, not a human analyst study. No participant results or efficacy claims were added. Full-package import remains a deliberate limitation until M3 guided intake. New decision review and authenticated collaboration are not implemented.

## Problem tree

**OP-2:** changed definitions/settings are visible. **OP-3/4:** compare evidence populations and check whether discrepancies persist. **OP-5:** distinguish check resolution from a changed inference or supported shipping decision. **OP-6:** preserve parent/child evidence and reasoning. **OP-7:** complete request → revised evidence → rerun → comparison → review in one workspace. **OP-1:** the analyst can inspect the basis for a recommendation; usefulness still needs human evaluation.
