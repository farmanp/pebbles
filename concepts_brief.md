# Pebbles concept brief

Author: Farman Pirzada
Date: 2026-11-12
Status: proposed concept; customer demand and all product evaluations unvalidated. No implementation authorized by this document.

## The problem and first user

A product data scientist or experimentation analyst must decide whether a reported A/B result supports a shipping recommendation. The working hypothesis is that reconstructing definitions, records, calculations and limitations across files costs consequential time. This pain has not yet been established through customer research.

Pebbles would review the evidence an analyst can supply and explain which conclusions that evidence supports. Its first workflow accepts a local package containing experiment configuration, a scorecard, metric definitions or SQL, permitted assignment/exposure/outcome exports, and notes. It returns supported calculations, discrepancies, unanswered questions and targeted requests for more evidence. The analyst retains the shipping decision.

The proposed benefit is less manual reconstruction without losing the distinction between observed records and real-world behavior. Existing analyst workflows and diagnostics are the comparison baseline. Detecting a familiar anomaly does not establish differentiation.

## The smallest product hypothesis

A deterministic local evidence reviewer can reduce total analyst effort while preserving or improving conclusion quality. The first supported calculation is a versioned, user-level checkout conversion metric in a fixed window. The first consequential defect is a scorecard using exposure-event rows as the denominator when the supplied definition requires distinct exposed users.

A legitimate repeat encounter creates the opportunity for this calculation error; the repeat encounter itself is not proof of a tracking or delivery defect. The original fixture adds a new exposure ID for the same user, so it does not demonstrate duplicate event ingestion.

The workflow is: inventory admitted files and provenance → identify check prerequisites → compute supported checks → reconcile sources → present an evidence-scoped report. Use one local process, ordinary files, deterministic calculations and templated findings. No assignment service, production SDK, warehouse connector, metric-registry service, database publishing workflow or LLM is needed for the first evaluation.

## What a finding means

A **check** is one explicit proposition evaluated under a versioned rule, such as “the reported treatment denominator equals the distinct exposed users in this supplied export under metric v1.” Each finding includes check ID/version, proposition, evidence references with file/row or field locators, source fingerprints, relevant population/window/revision, calculation, observed and expected values when defined, assumptions, outcome, limitations, and the smallest additional evidence needed.

| Evidence outcome | Meaning | Example |
|---|---|---|
| Verified | The named proposition is supported by admitted evidence and the stated rule. | Three distinct treatment user IDs occur in the supplied exposure records. |
| Failed | Sufficient comparable evidence contradicts the named proposition. | The scorecard denominator is four while the agreed distinct-user calculation is three. |
| Insufficient evidence | The proposition cannot be determined from admitted evidence. | Event records exist but the intended denominator definition is absent. |

No overall “verified experiment” badge is allowed. Input completeness is separately recorded as declared or unknown, with the declaration's origin; a declaration is not independent proof. Matching arithmetic cannot establish causal validity, actual rendering, production instrumentation correctness, unlogged actions or historical targeting stability.

Execution state is separate: completed, blocked by invalid/unsupported input, or errored. A check that does not execute has no evidence outcome; its row records the affected proposition and operational cause. Missing evidentiary prerequisites can produce a completed Insufficient evidence result. A parser crash cannot. Unsupported SQL must be exposed as an execution limitation, not an experiment defect.

## First evidence test

The [first evaluation plan](first_evaluation_plan.md) specifies E00 clean control and E01–E05: a planted calculation defect, summary-only evidence, missing definition, contradictory sources and absent implementation evidence. It also requires focused temporal/revision/error probes. Every package has a separately written oracle of required and forbidden claims before a prototype is built.

Two hypotheses are tested separately:

1. **Technical:** Pebbles reproduces supported values, detects the planted discrepancy, preserves provenance, and refuses unsupported assurance across missing or conflicting evidence.
2. **Workflow:** relevant analysts reach equally defensible conclusions with less total effort, including export selection, packaging, mapping, review and correction.

Neither establishes customer demand or willingness to switch. The comparison uses each analyst's normal tools, with the same evidence availability and no hidden oracle. Matched case families and counterbalanced methods avoid exposing the same analyst to the same case twice.

## Alternatives and trade-offs

| Alternative | What it can test | Decision for this phase |
|---|---|---|
| Existing workflow plus a structured checklist | Whether clearer evidence questions solve most of the problem | Retain as a low-cost alternative; choose it if automated recomputation adds little. |
| Human-produced evidence report | Whether report structure helps interpretation | Valid preliminary study if explicitly disclosed; measure preparer labor and never call it automated savings. |
| Deterministic local evaluator | Repeatable calculations, admissibility and provenance | Preferred bounded prototype after package/oracle readiness. |
| Full experimentation platform or integrations | Operational assignment and telemetry workflows | Defer; these solve a broader problem than supplied-file review and add untested dependencies. |

## Risks, safeguards and limits

The greatest risk is confident overstatement: evidence from an export can support a calculation while leaving completeness, comparability or production behavior unknown. Explicit check prerequisites, forbidden-claim oracles and independent scoring are mandatory. Conflicting sources must be shown side by side; neither becomes authoritative because it is called raw.

A second risk is shifting work into packaging. Measure preparation and corrections in both methods; stop if preparation consumes the investigation benefit. A third is excessive automation scope. Begin with JSON/CSV/JSONL, an explicit metric schema and a narrow supplied SQL example; unsupported semantics remain visible. Treat SQL and notes as evidence, never as instructions to execute arbitrary code.

Proposed local evaluation envelope: one worker; at most ten files, 50 MB uncompressed and 100,000 event rows per package; 2 GB process memory and 60 seconds per run on a recorded machine. These are planning limits, not measured capacity. No network access or writes to source evidence. Keep source snapshots immutable; each run writes new artifacts keyed by input, contract and evaluator versions. Changed definitions trigger a new run, never silent reinterpretation of old findings.

Synthetic data only in this phase. Real-data access, privacy, retention, security and permissions require a later scoped decision. No claim of production readiness follows from a synthetic pass.

## Cost, sequence and decision

Proposed cap: ten working days after staffing is available, 60 builder hours and 16 evaluation/reviewer hours, six analysts up to 90 minutes each, and $600 external spending excluding internal labor. These are proposed planning defaults, not an approved budget or recruitment claim. Preparation precedes implementation; a technical rehearsal remains possible if participants are unavailable, but workflow value stays Not evaluated.

Sequence: settle package/check contracts and independent oracles → create blinded cases and error probes → implement the smallest deterministic slice in a separately authorized phase → verify correctness and claim boundaries → compare analyst workflows → decide proceed, revise, narrow to a checklist/report, or stop. Correctness is a gate; speed cannot compensate for false assurance.

Open execution decisions are participant availability, independent oracle/scoring roles, local machine capacity and actual preparation costs. Resolve them before the relevant evaluation begins; the draft supplies bounded defaults so those decisions do not imply a broad platform build. The expected next artifact is the frozen evaluation dataset and rubric, not a production integration.

## Source basis and review provenance

Current scope comes from `planning/review-input.md` and `planning/source/user-evidence-boundary.txt`; it supersedes the original foundation's platform sequence. The original BRD contributes dataset contracts and exact arithmetic; the technical specification contributes versioning, test traceability and replay principles; the opportunity tree separates product value from technical success. Its candidate integrations and original G0–G5 gates are not commitments here.

The included eight-user fixture is an arithmetic seed. It lacks E01–E05 scorecards/package oracles and does not establish inference calibration. Its checker ignores temporal and revision boundary cases. The parent agent ran its four existing consistency tests successfully; this is source-fixture consistency only. All proposed Pebbles evaluations remain unrun.

Six independent fresh-context Goldfish lens reviews informed this synthesis; statuses, read attestations and finding dispositions are in [the review report](planning/goldfish_review_report.md). The synthesis is a planning draft, not a claim that a later implementation satisfies an implementation-readiness standard.
