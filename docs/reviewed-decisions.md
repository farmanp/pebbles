# Reviewed decision and evidence handoff — M4 local slice

Implemented and verified 2026-11-13. In **Experiment workspace**, attach the relevant runs and use **Recommendation and review**.

## Workflow

1. Select an exact evidence run. Read its machine assessment and supporting evidence; acknowledge each listed blocker, unresolved assumption, unevaluated area and unresolved finding.
2. Enter an analyst name, ship/hold/stop/iterate recommendation and rationale. Save an immutable recommendation snapshot. A recommendation may disagree with Pebbles, but it cannot relabel a failed check or remove blockers.
3. Inspect the saved recommendation and source run. Record reviewer name, agree/request changes/disagree response, rationale and explicit review acknowledgement. Each snapshot accepts one review; subsequent changes require a new recommendation.
4. Download the decision and evidence ZIP. It contains a readable HTML/Markdown summary, machine-readable frozen decision/review/context, prior decision records, all runs attached when the recommendation was created, their source evidence and reports, and a SHA-256 manifest. This is a local download for user-controlled sharing, not an automatic message.
5. Attaching any additional run, including a child revision, flags earlier records as needing renewal. Pending reviews against older workspace evidence are rejected. Reviewed records stay preserved; their newly exported packet is visibly labeled stale and lists newer run IDs without pretending those inputs were reviewed. Previously downloaded files remain point-in-time artifacts and cannot update themselves.

## Integrity and limits

Workspace SQLite transactions protect snapshot and review writes. The recommendation freezes the exact run assessment, obligations, input fingerprints, investigation context and canonical report fingerprints for all then-attached runs. Exports reject changed JSON reports or source bytes. Readable run reports are regenerated from verified JSON, preventing a separately edited HTML/Markdown file from silently changing the handoff. Original run artifacts are never overwritten by recommendation/review actions.

Follow-ups, revision comparisons and activity history are captured as they stood at recommendation time. Later workflow notes do not silently rewrite that context. A new recommendation can capture updated context. Additional-run invalidation is deliberately conservative; it does not infer which branch is authoritative.

Analyst/reviewer names are local, unauthenticated labels. This is a recorded review, not authenticated team approval or deployment authorization. Ship does not execute deployment; stop does not stop a running experiment. No real-team decision or analyst efficacy is claimed. The complete ZIP contains source data; the UI states its scope before download. Back up the workspace database and saved runs together.

## Computer Use verification

Used **Decision handoff · AI walkthrough** (`ca6559a7-1b94-4aba-ab10-9eacf8f42d57`). Attached the incomplete Cookie Cats run. Attempting to save without blocker acknowledgement was visibly rejected. Acknowledged all items, saved HOLD, recorded an agreeing demo review and downloaded the ZIP. Pebbles' assessment remained blocked.

After a server restart, reopened the saved review and successfully exported. Attached the corrected CSV run; observed **Review needs renewal** in the UI and in a second downloaded packet, with the original reviewed evidence preserved. Created a fresh STOP recommendation against the corrected run, recorded an agreeing demo response and downloaded a fresh packet. Reloaded and reopened the workspace; recommendation/review persisted.

Final decision: `4767164b-8691-40c3-9064-6cbe0b999db1`. Its verified ZIP contains 16 files, both evidence runs and the prior HOLD decision, with every manifest hash matching. [Final handoff](../pilot-self-try/decision-handoff-final.zip) · [Screenshot](../pilot-self-try/reviewed-decision.jpg) · [Stale handoff](../pilot-self-try/decision-handoff-stale.zip).

65 tests passed. New coverage checks required acknowledgements, valid run references, immutable reviews, human disagreement without machine-status changes, stale review rejection, evidence tampering, regenerated readable reports, bundle contents and hashes. Independent review found unchecked readable-report copying; fixed by rendering from verified JSON. No human pilot or scored analyst evaluation ran.

## Problem tree

- **OP-1:** explicit recommendation, rationale and reviewer response.
- **OP-5:** machine validity and unresolved blockers remain separate from human judgment.
- **OP-6:** exact evidence snapshot, prior reasoning and review survive handoff and later revisions.
- **OP-7:** investigation → recommendation → review → export → renewed review in one local workflow.

M1/M2, M3's bounded CSV intake and M4's local decision handoff are built. The remaining acceptance gates are representative-company export validation and human comprehension/usefulness evaluation (M0/M5). Guided original-plan/readout/reference intake and broader statistical designs remain limited. Authenticated collaboration and production operations are separate future work.
