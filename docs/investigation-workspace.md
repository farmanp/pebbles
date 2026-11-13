# Investigation workspace — M1

Implemented 2026-11-13. Open **Experiment workspace** in the sidebar. Create an experiment, attach an existing run, choose a finding and record an evidence request, owner and notes. Save a follow-up status and return through the experiment list later. No message is sent to the named owner.

## Model and boundaries

- Experiments have stable generated IDs; duplicate display names do not merge experiments. Runs are attached explicitly, including older runs.
- Follow-ups link to an exact attached run and check ID, retaining the original question and check outcome. One follow-up per finding per experiment prevents accidental duplicates.
- Statuses: open, waiting for evidence, ready to recheck, resolved, dismissed. Resolved/dismissed require a rationale. They record human workflow judgments, not a verified resolution of the scientific issue.
- Requests, owner labels, notes and state changes persist in `workspace.sqlite` beside the run directories. SQLite transactions protect updates; revision checks reject stale follow-up edits. Each successful change records its timestamp and submitted details.
- Workspace metadata never writes to analytical run files. A task status cannot change a failed check, inference or shipping blocker.
- Owner labels are local, unauthenticated metadata. This is not a multi-user approval service. Rerun diffs and decision review remain M2/M4.
- Explicit Save is required. Unsaved edits do not persist when navigating away. Back up `workspace.sqlite` together with the original run directories; workspace links depend on those run IDs.

## Verification

52 automated tests passed, including persistence across separate database connections, distinct experiment IDs, valid attached-run/finding checks, duplicate protection, stale-write rejection, required rationale and unchanged analytical results.

Computer Use walkthrough completed: created “Cookie Cats · workspace walkthrough,” attached run `0a47a51f-033e-4251-9a0c-4335b78a9275`, tracked P06, requested the complete gate_40 export/query/population definition, assigned a demo owner, saved “waiting for evidence,” reloaded the page, reopened the experiment and verified the request and notes persisted. Open source run still displayed the 3,800 missing users, reversed retention conclusion and blocked shipping status. [Screenshot](../pilot-self-try/workspace-resumed.jpg).

This walkthrough created demo workflow metadata only. It is not a human analyst study and no evidence request was transmitted.

## Problem tree

OP-3/OP-4: integrity and reconciliation findings become explicit follow-up work. OP-6: exact run links and timestamped history survive returning later. OP-7: investigation context stays in the app. OP-1/OP-5: workflow progress remains distinct from evidential validity and decision readiness.

M2 is now implemented: [evidence revisions and rerun comparison](evidence-revisions.md) preserves originals and shows whether new evidence changes a finding. The M1 verification above remains a historical checkpoint.
