# Pebbles — active opportunity tree

## Analyst workspace UX — three views, 2026-11-13

Experiments, Investigation and Decision now separate the working flow. Forms open on demand; selected-run results and blockers lead the investigation; earlier reviews remain accessible. Computer Use verified navigation, evidence preview, follow-up creation, history, form access and handoff download. 65 regression tests passed. This advances OP-7 while preserving OP-1/3/4/5/6 boundaries; human evaluation remains outstanding. [Design and verification](docs/analyst-workspace-redesign.md).


## Latest status — M4 local reviewed decision and handoff, 2026-11-13

M4 now records an exact-run recommendation, explicit unresolved-evidence acknowledgement, immutable reviewer response and downloadable evidence/history packet. Additional attached evidence flags older reviews for renewal. Computer Use exercised saving, review, export, restart persistence, renewal and a fresh reviewed decision; 65 tests passed. [Behavior, evidence and limits](docs/reviewed-decisions.md).

OP-1/5/6/7 now connect investigation to documented review and handoff. M1/M2, M3 bounded CSV intake and M4 local mechanics are implemented. Representative real-export acceptance and human analyst evaluation remain outstanding; this is not authenticated team approval or production readiness. Older sections below preserve historical checkpoints.


## Latest status — M3 guided CSV intake, 2026-11-13

M1 workspace and M2 evidence revisions are implemented. M3 now has a bounded guided CSV path: map columns, confirm meaning/design, preview validation and run without hand-authoring package files. Source and versioned mappings are preserved; corrected CSVs reuse mappings and create linked revisions. OP-2/3/4/5/6/7 are connected through this flow. [Behavior, Computer Use evidence and remaining limits](docs/guided-data-intake.md).

M3's real-company-export acceptance and OP-1/7 human evaluation remain unfulfilled. Separate readout/reference import through the wizard and broader schemas remain missing. M4 reviewed decision and handoff is still unbuilt. Older sections below are historical checkpoints and baseline plans, not current build status.


## Evidence revisions — M2 implemented, 2026-11-13

The workspace now accepts a complete corrected evidence package as a child of an attached run, records a reason, preserves originals, and compares file/settings changes, findings, effects, populations and shipping blockers. Verified rechecks go to human review; adverse or missing rechecks reopen follow-ups. OP-2–OP-7 are connected through this resolution loop; human value under OP-1 remains untested.

Computer Use restored 3,800 omitted users in a controlled revision: P06 Failed → Verified, reported benefit → harm, reference result unchanged, shipping blocked → blocked. Comparison and recheck state survived reload and server restart. 55 tests passed; independent review findings fixed. [M2 behavior and evidence](docs/evidence-revisions.md). M3 guided intake and M4 reviewed decisions remain unbuilt.

## Investigation workspace — M1 implemented, 2026-11-13

Create an experiment, explicitly attach saved runs, track a finding and evidence request with an owner, save workflow status/notes and resume later. Separate persistent workflow metadata and timestamped activity history preserve analytical results: marking a task resolved or dismissed does not clear failed checks or shipping blockers. This advances OP-3/4 follow-up, OP-6 provenance and OP-7 continuity, while preserving OP-1/5 decision boundaries.

52 automated tests passed. Computer Use exercised create → attach → track → waiting → reload → reopen → inspect original blocked result. No human analyst study has run. [Workspace behavior and verification](docs/investigation-workspace.md). M2 rerun comparison and M4 reviewed decisions remain unbuilt.

## Current roadmap — 2026-11-13

The [analyst workflow roadmap](docs/analyst-workflow-roadmap.md) maps current capabilities and gaps to OP-1–OP-7. Proposed sequence: **M0 analyst rehearsal → M1 investigation workspace → M2 evidence revisions and rerun comparison → M3 guided real-data intake → M4 reviewed decision record → M5 workflow evaluation**. M0 learning can run alongside M1 planning; these are proposed milestones, not completed work.

Latest technical evidence: both pilot packets rerun through Computer Use, new UI/export explanation parity checked, and 50 automated tests passed. See [final recheck](pilot-self-try/FINAL-PILOT-RECHECK.md). No human pilot or scored analyst study has run. Earlier sections retain their historical checkpoint counts; the latest technical status is stated here.

## Analyst evaluation kit — OP-1 / OP-7, prepared but unrun

The [pilot-v1 kit](evaluation/analyst-pilot-v1/README.md) now provides neutral matched cases, facilitator-only answer keys, scoring rules, counterbalanced allocation, a blank results workbook and a one-case handoff tool. Start with the unscored P00 rehearsal. No pilot or scored analyst sessions have run, and no speed or accuracy benefit is established.

The study tests **OP-1** (defensible decisions) and **OP-7** (usable workflow). Case reasoning exercises **OP-3** (population integrity), **OP-4** (reconciliation) and **OP-5** (decision validity). Versioned instructions, evidence and saved responses support **OP-2 / OP-6**. Technical packet checks establish consistency, not user value. This narrow Cookie Cats benchmark does not complete the original platform checkpoints.

Updated 2026-11-12. This is the working status of the original [opportunity tree](planning/source/pebbles_v0_1/03_OPPORTUNITY_TREE.md), which remains preserved. The first product is now an analyst's file-based evidence investigation. The original assignment-platform build sequence is not being silently declared complete.

**Current outcome:** an interactive local app loads experiment files, runs the investigator, explains findings, previews source evidence and reopens saved investigations. Start with `python3 -m pebbles.web` and open http://127.0.0.1:8848. The [executed synthetic defect report](demo/denominator-defect/report.html) shows reported 2/4 versus calculated 2/3 conversion. This is a product demonstration, not customer validation.

| Original branch | Current question | Work and evidence | Still unknown / next test |
|---|---|---|---|
| OP-1 / H1 — questions to defensible decisions | Does the investigation report reduce an analyst's reconstruction work? | Actual report with calculations, fingerprints, unresolved evidence and next requests; study materials prepared. | User review of this concrete workflow, then analyst comparison. No customer-value claim yet. |
| OP-2 / H2 — evolving definitions | Can a declared metric retain its meaning across a change? | v1/v2 calculations are explicit; new runs preserve prior outputs; version-change test passes. | Broader definitions and long-term dependency/environment replay. No published registry built. |
| OP-3 / H3 — assignment/exposure evidence | Can supplied records be distinguished and checked? | Unique-user versus event count, replay/conflict, orphan/exclusion and temporal rules implemented; clean repeat and defect cases exercised. | Actual SDK delivery and telemetry completeness remain outside exported-file evidence. |
| OP-4 / H4 — differing metric calculations | Can Pebbles independently recompute the supported metric and explain disagreement? | Deterministic local calculation and narrow SQL denominator inspection; exact rates checked across prepared forms. | General SQL equivalence, CSV/Parquet mappings and integrations deferred until a concrete need. |
| OP-5 / H5 — invalid conclusions | Can the report avoid unsupported assurance? | Missing definition and unknown comparability stay unresolved; rendering/completeness always unresolved in this scope. | Conditional assigned-user treatment-effect analysis now implemented; see the analysis milestone below. Human interpretation remains untested. |
| OP-6 / H6 — history after component change | Can prior evidence/results survive a change? | Source fingerprints, new output per run, replay and definition-change tests. | Adapter replacement and durable archival execution environment not demonstrated. |
| OP-7 / H7 — integrated workflow | Does one evidence packet travel intake → checks → report? | Interactive file loading, run action, plain-language summary, evidence preview, filters, exports and saved history; CLI retained. 39 tests pass; upload/run/preview/history exercised in browser. | Real-export usability and wider malformed/adversarial inputs. |

## Current checkpoint

The bounded **file-to-report prototype exists and has run**. Original CP-1–CP-5 include broader platform requirements and are not claimed passed. Evaluation-material auditing, product execution, and customer-value evidence are distinct:

- Materials: 18 prepared packets and private expectations independently checked.
- Product: interactive app and CLI investigate packets; 39 tests pass and actual saved results exist.
- User/analyst value: no scored analyst sessions have run.

Next: review the treatment-effect workflow with a representative export, then evaluate analyst understanding. The new decision summary combines binary guardrails and declared cost/risk review; production verification and analyst evaluation remain next.

## Treatment-effect analysis milestone — OP-5 / CP-3

**Question:** Did treatment improve the primary metric enough to matter, given trustworthy evidence and an appropriate study design?

The UI now compares treatment with control, calculates a 95% difference interval, and explains improvement, harm, below-goal, inconclusive, or blocked results. This is a bounded implementation of **OP-5 / H5** (avoiding invalid conclusions), connected to the original **CP-3 / G3** inference-calibration work. It is not completion of the broader original checkpoint.

- **OP-2:** save the metric version and study declarations, including the predeclared minimum worthwhile effect.
- **OP-3:** gate inference on record checks and an assignment sample-ratio diagnostic; production completeness and randomization remain declared assumptions.
- **OP-5:** compare the uncertainty interval with zero and the practical goal; never turn inconclusive into “no effect.”
- **OP-6:** preserve the input, plan, method version and result with each run; older runs remain unchanged.
- **OP-7:** expose this in the existing load → investigate → explanation workflow, including evidence and exports.

**Executed evidence:** 32 automated tests; actual browser execution of the improvement example; BR-D07-style null simulation and BR-D08-style known-effect coverage simulation, 2,000 trials each. Null zero-exclusion rate was 4.45%; interval coverage was 95.55% under the null and 95.50% under the known effect. Both meet the saved bounded protocol. See [method and limits](STATISTICAL_METHOD.md) and [results](evaluation/statistical/results.json).

**Remaining:** other sample-size/baseline regimes, sequential or clustered designs, continuous guardrails, broader multiple-metric designs, general metric/SQL support, and analyst evaluation. No analyst study has run; this is product execution and numerical validation, not customer-value validation.

## Guardrails and decision summary — OP-1 / OP-5

**Implemented:** a conditional shipping recommendation that explains supporting evidence, blockers, remaining assumptions and next steps. Three executed synthetic examples show support, unacceptable refund harm, and uncertain refund safety. The primary goal must be met, all declared binary guardrails must clear their harm limits, and an analyst must record an accepted cost/implementation review. Missing or inconclusive evidence does not become a safety pass.

| Branch | This increment | Still missing |
|---|---|---|
| OP-1 — defensible decisions | Primary benefit + guardrails + declared risk rationale produce an explained conditional recommendation. | Whether analysts find this useful and interpret it correctly. |
| OP-2 — explicit definitions | Versioned guardrail definitions, direction, harm limits and completeness/predeclaration attestations are saved. | Independent proof that the plan was fixed before results were inspected. |
| OP-3 / OP-4 — evidence integrity and calculation | Match guardrail scope and exact assigned population; reject missing, duplicate, nonboolean or conflicting observations; compute rates and adjusted intervals. | Reconstruct flags from production events and verify upstream capture. |
| OP-5 — valid conclusions | Distinguish within-limit, harmful, uncertain and blocked; adjust intervals across the declared guardrail family. | Wider statistical calibration, continuous metrics, sequential and clustered designs. |
| OP-6 — preserved reasoning | Save source fingerprints, plan, review notes and decision with each new run and exports. | Durable cross-environment replay. |
| OP-7 — usable workflow | Editable guardrail/review inputs and a decision summary above the primary analysis. | Real-export usability and analyst study. |

**Verification:** 39 tests, fresh independent review, browser execution of supported and harmful examples, and rerun primary calibration. A review-discovered import truncation bug was fixed: malformed or oversized required-guardrail plans cannot silently lose metrics. This is bounded product evidence, not full CP-3/G3 or customer-value validation. [Contract](docs/guardrails-contract.md) · [method](STATISTICAL_METHOD.md).

## First public-data comparison — Cookie Cats

**Executed:** 90,189 actual public CSV rows were run through Pebbles and compared with a pinned independent analyst notebook. Published retention rates, differences, z-test p-values and Wald bounds reproduce at display precision after matching the notebook's one-player exclusion. The all-user analysis is retained separately. Day-7 retention is lower at gate 40; the full-data interval is −1.328 to −0.312 percentage points. The shipping review remains blocked on absent original evidence.

- **OP-4:** a bounded CSV snapshot adapter, independent rate calculations, Wald/Newcombe method comparison and explicit population reconciliation now exist.
- **OP-3:** absent assignment/exposure/event logs and uncertain production completeness remain gaps; no fake timestamps were introduced.
- **OP-2:** the readout identifies its metrics, but original dated predeclarations and harm limits were not recovered.
- **OP-5 / OP-1:** numerical agreement is separated from a defensible production shipping decision. The public portfolio recommendation is not treated as the original company decision record.
- **OP-6:** raw files, notebook, pinned revision, hashes, exclusion details and saved results preserve the comparison.
- **OP-7:** the public comparison is runnable in the existing UI, with evidence preview and exports.

43 tests pass; the public comparison ran in the browser. This is the first public-data replay, not an analyst study. Next: obtain a representative organization's export plus original plan and instrumentation evidence, or expand public benchmarking across additional documented designs without claiming missing evidence is known. [Comparison and reproducibility notes](public_comparisons/cookie_cats/COMPARISON.md).

## Controlled discrepancy investigation — OP-3 / OP-4 / OP-5

**Implemented and executed:** Cookie Cats control plus three separate introduced-problem packets. The UI shows reported → supplied-export → supplied-reference calculations, evidence-based reasons, affected records, and whether the retention conclusion changes. A wrong denominator and missing non-retained users produce apparent positive results that reverse against the reference; a day-1/day-7 count mismatch changes inconclusive to negative. The control agrees. Shipping readiness stays blocked throughout.

- **OP-3:** exact missing/extra/changed-user reconciliation against a supplied reference. This does not independently prove production completeness.
- **OP-4:** diagnose denominator and metric-count mismatches; explicitly leave unsupported causes unresolved.
- **OP-5:** distinguish a changed statistical retention conclusion from unchanged, incomplete shipping readiness.
- **OP-2 / OP-6:** save declared metric, reported counts, evidence fingerprints and complete replay outputs; original public baseline is preserved.
- **OP-7:** evidence buttons, affected records, plain-language explanation, saved runs and exports.
- **OP-1 / OP-7 next test:** measure whether an analyst identifies the consequential defect and decision impact more accurately or faster. No analyst study has run.

49 tests pass; four cases executed, with the missing-user investigation and source preview exercised in the browser. The investigator uses selected evidence, not case labels or private expectations. This is a bounded engineered benchmark, not proof of general defect discovery. [Workflow, results and limits](docs/discrepancy-workflow.md) · [Executed case summary](evaluation/discrepancy/results.json).
