# Request → received evidence → rerun

Goal: close the workflow gap without implying unsupported evidence has been verified.

Received evidence is an immutable UTF-8 file attached to an existing follow-up with filename, content hash, receipt note and timestamp. Supported intake: .csv, .json, .txt, .md, .sql; at most 1 MB per file and 10 receipts per request. Corrected outcome CSVs can reopen the original/successive CSV mapping for validation and a linked rerun. Other evidence is saved for manual review, with that limitation explicit. Original findings and files remain preserved. Request lineage includes descendant rechecks, so corrected findings reopen the original request instead of offering an accidental duplicate.

The server validates request/receipt/parent linkage and exact received CSV bytes before saving the rerun. Original obligations and machine blockers remain unchanged by receipt or manual workflow status. Frozen decision handoffs retain received evidence, including named files and hashes.

After rerun show a full-width summary: receipt/reason, before/after result, machine shipping assessment changed or unchanged, original request recheck, remaining blockers, and explicit statement that a saved human recommendation is not automatically changed. Technical comparisons stay expandable.

Problem tree: OP-3/4 investigation and reconciliation; OP-5 analytical boundaries; OP-6 immutable evidence/lineage; OP-7 continuity; OP-1 decision consequences.

Implementation plan:
- Add receipt validation/storage and handoff coverage; test invalid links, wrong bytes, original preservation and hashes.
- Add receive/open/rerun controls, lineage-aware request links and contextual CSV preloading.
- Add prominent rerun-impact summary without inferring resolution from upload.
- Run automated regression checks and Computer Use against the actual app, then publish through protected main.

Verification: automated tests cover invalid request/receipt/parent links, wrong CSV bytes, immutable original report, receipt hash, >64 KB supporting files, received-file inclusion in frozen handoffs, revision-aware request navigation, unchanged blockers and analytical conclusion changes. Computer Use completed original I03 request → receive corrected CSV → validate saved file/mapping → rerun → original request. Synthetic result changed +10 pp (higher) to -5 pp (lower); shipping stayed blocked and I03 stayed insufficient evidence. A supporting TXT plan was separately received and explicitly labeled manual review required. No human analyst study ran.

Receiving additional files invalidates older recommendation/review currency even before rerunning. Frozen exports list newer excluded receipts without silently incorporating them. Navigation guards prevent a delayed receipt action from reopening a workspace after the analyst leaves.
