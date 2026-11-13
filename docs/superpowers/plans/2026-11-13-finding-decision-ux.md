# Finding actions and decision review

Goal: request evidence from a finding without selecting its context again; review unresolved evidence once without repetitive checkboxes.

Design: inline request disclosure on every finding, with exact run/finding IDs, editable suggested request and optional owner/notes. Already tracked findings link to their existing follow-up. Saving returns to that follow-up in the same experiment. No messages are sent. Decision composition defaults to the selected run and experiment owner. Group exact duplicate obligation text for display, retain all distinct evidence and original IDs, and use one required acknowledgment for the entire list. Changing runs resets acknowledgment. Backend validation, frozen snapshots, blockers and review semantics remain unchanged.

Alternatives: prefill the separate generic tracking form (still separates finding from action); semantic blocker merging (risks hiding distinctions). Use inline actions and exact-text-only grouping.

Problem tree: OP-3/4 investigate findings, OP-6 retain evidence links, OP-7 continuity, OP-1/5 defensible judgment without clearing blockers.

## Tasks
- [ ] Add contextual request rendering and existing-follow-up navigation; verify IDs, escaping, suggestions, duplicate prevention and save destination.
- [ ] Add grouped decision rendering and one explicit acknowledgment; verify all original IDs preserved and run changes reset consent.
- [ ] Run JS and Python checks, then Computer Use: request from finding, reopen it, compose recommendation on selected run, save and review. Publish through protected main after review.

Constraints: existing vanilla JS/Python, no dependencies, preserve unfinished tracking work, no statistical changes. Review focus: wrong-run actions, existing requests, failed saves, stale async previews, blocked decisions staying blocked.

## Verification record
Implemented both tasks. JS checks pass: contextual suggestions, exact-run duplicate detection, escaping, exact-text grouping, all obligation IDs, stale preview rejection and acknowledgment reset. Python suite: 71 passed. Computer Use on local static demo: saved I03 request from the corrected run, landed on the linked follow-up, reopened through the finding action; composed HOLD against selected corrected run, unchecked acknowledgment rejected, switching run reset acknowledgment, saved snapshot retained all nine original obligations, simulated review recorded with blocked assessment unchanged. This is UI verification, not evidence of human analyst efficacy.
