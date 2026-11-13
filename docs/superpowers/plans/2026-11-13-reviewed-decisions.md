# Reviewed Decision and Handoff Implementation Plan

**Goal:** Record and review a recommendation against an exact run, preserving blockers and exporting the evidence/history needed for handoff.
**Architecture:** Append-only decision snapshots in the local workspace database, one immutable review per recommendation. New recommendations supersede through explicit new records, not edits. Any newly attached run makes previous reviews need renewal. Local author/reviewer labels are not authenticated approvals. ZIP export contains frozen decision/context, reviewed run reports and source evidence, history runs and a manifest, plus readable HTML/Markdown summaries.
**Tech Stack:** Existing Python stdlib, SQLite and browser JavaScript.

- [x] Add decision create/review actions with mandatory rationale and explicit acknowledgement of all saved blockers/assumptions; never mutate reports. Test invalid references, frozen snapshots, stale review prevention and immutability.
- [x] Add workspace recommendation/review panels, blocker preview and renewed-review status. Provide handoff export for reviewed records.
- [x] Add downloadable evidence bundle and test lineage/content and escaping.
- [x] Run regression checks and Computer Use create → inspect blockers → recommend → review → export → reopen → newer evidence needs renewal. Update OP-1/5/6/7 and roadmap with observed limits.
