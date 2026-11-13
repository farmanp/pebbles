# Pebbles analyst workflow roadmap

## Latest status — M4 local reviewed decision and handoff, 2026-11-13

M4 now records an exact-run recommendation, explicit unresolved-evidence acknowledgement, immutable reviewer response and downloadable evidence/history packet. Additional attached evidence flags older reviews for renewal. Computer Use exercised saving, review, export, restart persistence, renewal and a fresh reviewed decision; 65 tests passed. [Behavior, evidence and limits](reviewed-decisions.md).

OP-1/5/6/7 now connect investigation to documented review and handoff. M1/M2, M3 bounded CSV intake and M4 local mechanics are implemented. Representative real-export acceptance and human analyst evaluation remain outstanding; this is not authenticated team approval or production readiness. Older sections below preserve historical checkpoints.


## Latest status — M3 guided CSV intake, 2026-11-13

M1 workspace and M2 evidence revisions are implemented. M3 now has a bounded guided CSV path: map columns, confirm meaning/design, preview validation and run without hand-authoring package files. Source and versioned mappings are preserved; corrected CSVs reuse mappings and create linked revisions. OP-2/3/4/5/6/7 are connected through this flow. [Behavior, Computer Use evidence and remaining limits](guided-data-intake.md).

M3's real-company-export acceptance and OP-1/7 human evaluation remain unfulfilled. Separate readout/reference import through the wizard and broader schemas remain missing. M4 reviewed decision and handoff is still unbuilt. Older sections below are historical checkpoints and baseline plans, not current build status.


**M2 progress, 2026-11-13:** evidence revision creation, parent/child lineage, rerun comparison and tracked-finding rechecks are implemented within the existing supported package formats. Computer Use verified a corrected population case and persistence across restart; 55 tests pass. See [M2 implementation record](evidence-revisions.md). Guided intake, reviewed decisions and human evaluation remain outstanding. Baseline tables below describe the pre-build prioritization.

**Progress update, 2026-11-13:** M1's first slice is implemented and verified through Computer Use: stable experiment workspaces, attached runs, finding follow-ups, requests, owner labels, workflow states and persistent history. See [implementation record](investigation-workspace.md). The tables below preserve the baseline used to prioritize this roadmap; M1 entries are now built within the documented local scope. M0 human rehearsal and M2–M5 remain outstanding.

Status: proposed build sequence, 2026-11-13. This document plans work; it does not claim the missing features are implemented. Priorities reflect the current analyst-first scope and should be revised with pilot evidence. Milestones are dependency-based, not calendar commitments; staffing and delivery estimates have not been established.

## Outcome and scope

Enable a product data scientist or experimentation analyst to take an existing experiment from a questionable readout to a traceable, reviewed recommendation:

**Import → establish definitions and scope → inspect → investigate → request or correct evidence → rerun and compare → review → record and share the decision.**

Success includes a justified hold, inconclusive result or rejection. A recommendation to ship is not the only successful outcome. Pebbles initially sits alongside the system that assigns users and delivers variants. It does not need to replace that system to complete this workflow.

## Current evidence boundary

The local prototype runs file-based investigations, bounded treatment/control analysis, binary guardrails, conditional decision summaries, selected discrepancy checks, source previews, saved runs and exports. Cookie Cats replay and controlled cases have executed. Two pilot packets were rerun through Computer Use; their UI and fresh HTML/Markdown/JSON explanations were checked for consistency. The latest recorded regression run passed 50 tests.

**No human pilot or scored analyst study has run. No representative company export has been evaluated.** Automated correctness checks and AI walkthroughs do not establish analyst usefulness, general defect discovery or production readiness.

Evidence: [final walkthrough](../pilot-self-try/FINAL-PILOT-RECHECK.md), [revision record](../evaluation/analyst-pilot-v1/verification/ui-revision-2.json), [evaluation kit](../evaluation/analyst-pilot-v1/README.md), [statistical scope](../STATISTICAL_METHOD.md).

## Problem-tree map

| Branch | Analyst question | Roadmap responsibility |
|---|---|---|
| OP-1 — defensible decisions | Can I justify my recommendation? | Review, decision record and user-value evaluation |
| OP-2 — explicit, evolving definitions | What exactly are we measuring, and did it change? | Versioned import mappings, metric definitions and analysis declarations |
| OP-3 — assignment/exposure integrity | Are the right units and observations represented? | Intake validation, missing-evidence requests and integrity findings |
| OP-4 — reconciliation | Why do these results disagree? | Evidence tracing, discrepancy investigation and comparison of reruns |
| OP-5 — valid conclusions | Does the evidence support benefit, harm or uncertainty? | Supported inference, guardrails and decision prerequisites |
| OP-6 — preserved reasoning | Can someone reconstruct this later? | Immutable analysis snapshots, revisions and decision history |
| OP-7 — integrated workflow | Can I complete this task without reconstructing everything elsewhere? | Experiment workspace, investigation queue, import and review flow |

These are increments against the [active tree](../OPPORTUNITY_TREE.md), not completion of the original broader platform checkpoints.

## Feature inventory: built versus missing

“Built, bounded” means implemented within the current supported formats and statistical assumptions, not general platform parity.

| Capability | Current state | Missing work | Tree | Priority |
|---|---|---|---|---|
| Experiment workspace | Partial: local run history | Stable experiment identity, linked runs, owner and investigation status | OP-6/7 | M1 |
| Data intake | Built, bounded: packet upload and Cookie Cats adapter | Guided mapping from an ordinary export, validation preview, reusable import recipe | OP-2/3/7 | M3 |
| Metric/plan definition | Partial: explicit supported metric versions and declarations | Reusable definitions, change history and confirmed import semantics | OP-2/5/6 | M3; broader catalog later |
| Treatment/control analysis | Built, bounded: binary outcomes and stated independent-user assumptions | Design/metric eligibility checks at import; new methods only when evidenced needs arise | OP-5 | M3; expansion later |
| Integrity checks | Built, bounded: supported record checks, allocation diagnostic and reference reconciliation | Broader schemas, live ingestion and production completeness evidence | OP-3 | M3; monitoring later |
| Discrepancy explanations | Built, bounded: denominator, metric and population cases | Track hypotheses, evidence requests, resolution and unresolved causes | OP-3/4/7 | M1 |
| Rerun comparison | Partial: independent runs preserved | Parent/child runs; data, definition, method, finding and decision diffs | OP-2/4/5/6 | M2 |
| Guardrails and recommendation | Built, bounded: binary guardrails and conditional summary | Analyst recommendation record, review, acknowledgement of unresolved blockers | OP-1/5 | M4 |
| Reports and evidence | Built: previews, hashes, local saved runs, HTML/Markdown/JSON | Decision packet spanning investigation history and reviewed recommendation | OP-1/6/7 | M4 |
| Collaboration | Missing as a multi-user service | First: local named owner/reviewer and exported handoff. Later: authenticated roles, comments and notifications | OP-1/6/7 | M1/M4; service later |
| Experiment planning | Partial declarations only | Hypothesis workflow, power/duration estimation and pre-launch review | OP-1/2/5 | Later |
| Assignment and delivery | Missing | Flags/SDKs, targeting, bucketing, layers and variant QA | OP-3/7 | Deferred platform expansion |
| Live operations | Missing | Ramp, pause, stop, rollback and continuous alerts | OP-3/5/7 | Deferred platform expansion |
| Knowledge library | Partial: saved investigations | Searchable outcomes, linked hypotheses and cumulative learning | OP-1/6/7 | After workflow validation |

## User flows and gaps

| Flow | What works today | Completion gap | Milestone |
|---|---|---|---|
| Start with a real experiment | Select prepared evidence files | Identify experiment, map ordinary data and confirm scope | M1 identity + M3 import |
| Inspect results | Run checks, inspect source files, read effect and blockers | Maintain investigation context across sessions | M1 |
| Investigate disagreement | Compare claim/export/reference and inspect findings | Record a hypothesis, request evidence, assign follow-up and track progress | M1 |
| Resolve and rerun | Upload changed files as another run | Link the correction to its finding; show exactly what changed and why | M2 |
| Recommend and review | Read conditional machine summary, export it | Separate analyst judgment, reviewer response and unresolved blockers | M4 |
| Preserve and share | Reopen individual runs and export results | Export a coherent experiment-level decision history | M4 |
| Plan, launch and monitor | Outside current product scope | Full operational experimentation lifecycle | Deferred |

## Ordered roadmap

### M0 — Unscored analyst rehearsal: validate comprehension

**Priority: now, alongside M1 planning.** Use the existing kit with one representative analyst. Record loading trouble, explanation confusion, unsupported confidence, assistance and rubric ambiguity. Do not count either AI walkthrough as this session. Do not infer efficacy from a single pilot.

Exit: an actual session record, submitted responses, unresolved issues and agreed protocol changes. Resolve material misunderstanding before a scored comparison. This is a learning gate, not a requirement to stop all engineering while recruiting. Tree: OP-1/7, with OP-3/4/5 reasoning evaluated.

### M1 — Investigation workspace: turn a finding into actionable work

**First implementation milestone.** Build a stable experiment page containing its runs, findings and investigation log. Each follow-up has an owner label, status, relevant evidence, next request and notes. Initial storage can remain local; named labels are not authenticated identities.

Minimum flow: open an experiment → select a blocking finding → record what is known and unknown → create an evidence request → record who will obtain it → resume later. Users can export/copy a request; Pebbles does not send messages automatically.

Statuses: open, waiting for evidence, ready to recheck, resolved, dismissed with rationale. These are human workflow states, separate from check outcomes. A dismissed task must not convert a failed check into a pass or remove a shipping blocker.

Exit: the analyst can close and reopen the app without losing investigation context; every follow-up links to its originating run and finding; a changed status cannot silently change the scientific conclusion. Trace all transitions with timestamps. Tree: OP-3/4/6/7.

### M2 — Evidence revision and comparison: make resolution observable

**Depends on M1 identity and finding links.** Attach additional or corrected evidence to the same experiment, state the reason, and create a new immutable run. Compare source hashes, population/count changes, definitions, analysis settings/method version, findings, intervals and recommendation blockers. Distinguish changes caused by new data from changed assumptions; do not assert a causal explanation when several inputs changed together.

Minimum flow: supply requested evidence → review input changes → rerun → compare old/new findings → accept a documented resolution or keep investigating. New evidence that contradicts an earlier resolution reopens the issue or flags it for review. Never overwrite the original run or claim rerunning proves completeness.

Exit: use the denominator and missing-user cases to demonstrate correction → new run → visible effect reversal → linked resolution. An unrelated/new blocker remains visible. Old decisions are marked as based on older evidence, not silently updated. Tree: OP-2/3/4/5/6/7.

### M3 — Guided real-data intake: remove the custom-packet burden

**Depends on M1/M2 evidence and version model.** Start with one user-level CSV schema for a supported binary outcome, selected against a real analyst export. Map experiment/variant/unit identifiers and outcome columns; confirm randomization unit, time window, population and metric meaning. Show rows, missing values, duplicates and counts by arm before running. Import a reported readout and optional reference as separately labeled evidence. Generate the internal inventory and hashes rather than asking the analyst to author them.

Keep missing prerequisites explicit. A snapshot does not supply exposure timestamps, a dated plan or proven randomization. Reject or route unsupported clustered, sequential and continuous-outcome designs rather than applying the binary method silently. Save confirmed mappings as a versioned reusable recipe.

Exit: an analyst imports one representative real export without manually producing Pebbles JSON, sees intelligible validation errors, and can reproduce the analyst readout or explain the disagreement. Log every manual transformation. A synthetic rehearsal can verify import mechanics but cannot satisfy the real-export validation criterion. Tree: OP-2/3/4/5/7.

Build one read-only platform/warehouse connector only after identifying the actual source and repeated import friction. Connector choice and schema are open decisions; do not build several speculatively. Mapping design can proceed alongside M1, but implementation should reuse M2 version semantics.

### M4 — Reviewed decision record: complete the analyst handoff

**Depends on M2; use M3 for real-data acceptance.** Separate Pebbles' evidence assessment from the analyst's recommendation and the team's recorded decision. Capture ship/hold/stop/iterate, rationale, referenced run, acknowledged assumptions/blockers, reviewer label and review outcome. A human may record disagreement with Pebbles; that must never relabel a failed validity check as verified.

Minimum flow: prepare recommendation → include supporting evidence and unresolved issues → hand off for review → record review → freeze a decision snapshot → export its evidence and history. In the local version this is an explicitly recorded review, not an authenticated approval service or deployment action.

Exit: another analyst can reconstruct the decision from the exported packet; reviewed evidence/version is unambiguous; subsequent reruns show that a review needs renewal. UI, HTML, Markdown and JSON preserve the same caveats and provenance. Tree: OP-1/5/6/7.

### M5 — Validate the complete workflow before expanding scope

Run the prepared 4–6-analyst comparison after the unscored pilot and protocol freeze. Measure justified conclusions, false assurance, assistance and time with failures/timeouts visible. Follow with real-company investigations to assess data preparation and resolution work that Cookie Cats cannot represent. The small controlled comparison is descriptive; it does not establish broad market demand or production safety.

Exit: a documented proceed/revise/stop decision grounded in actual sessions and real-export experience. Investigate any unsupported shipping assurance before broader use. Choose subsequent integrations, metric types and collaboration features from observed blockers. Tree: OP-1/7, validating the combined OP-2–OP-6 workflow.

## First build slice

Start M1 with one vertical slice: **create an experiment → attach an existing run → open a finding → record an evidence request and owner → mark waiting → reopen and resume.**

Introduce stable experiment and follow-up identities while retaining immutable existing run IDs. Legacy runs remain accessible and may be attached explicitly. Do not infer experiment identity from mutable display names. Keep the UI to one experiment workspace and one finding detail panel. This is sufficient to expose the missing workflow without prematurely building a team administration product.

M1 is first because it turns existing diagnosis into useful work and supplies the identity model needed by reruns and review. M2 follows because resolution must be demonstrated rather than asserted. M3 then removes import friction; M4 closes the decision loop. Pilot feedback may move M3 earlier if file preparation dominates the task.

## Definition of a complete first analyst workflow

On a supported real experiment, an analyst can import ordinary data, confirm meaning and scope, inspect trustworthy or blocked analysis, investigate findings, request evidence, revise and compare runs, document review, and share a reproducible recommendation. Missing evidence remains missing; a valid endpoint can be “cannot decide yet.”

This is analyst-workflow completeness, not production service readiness. Shared deployment additionally needs authentication, authorization, tenant isolation, secure connector credentials, retention controls, backup/recovery and operational support. Full platform parity additionally requires assignment/delivery, live monitoring and rollout operations. Those are separate investments after evidence of user value.
