# Goldfish Review Report

Author: Farman Pirzada
Date: 2026-11-12
Mode: BRAINSTORM
Target: [review-input.md](review-input.md), entire document, with all 14 non-generated files in [source reading manifest](reviews/source-read-manifest.md).
Outputs: [concept brief](../concepts_brief.md) and [first evaluation plan](../first_evaluation_plan.md).

## Reviewer status

All six actual reviewer executions completed. Each was launched using `fork_turns: none`, supplied absolute persona/standard/target/source paths, and instructed not to read other reviews or generated briefs. Two reviewers ran concurrently in three waves. No reviewer was simulated by the synthesizer, and no failed launch was counted as a clean review. The reviewers were read-only; the synthesizer saved normalized reports retaining findings, recommendations and read attestations. Fresh conversation context does not establish exclusion of host instructions or filesystem isolation; those were not separately tested.

| Reviewer | Persona | Supplied standard | Status and report |
|---|---|---|---|
| egm-design | design_critic.md | heilmeier-standard.md | Completed — [report](reviews/egm-design.md) |
| egm-codebase-details | codebase_details.md | re-implementation-standard.md | Completed — [report](reviews/egm-codebase-details.md) |
| egm-zoom-out | zoom_out.md | zoom-out-standard.md | Completed — [report](reviews/egm-zoom-out.md) |
| egm-comprehension | comprehension.md | feature-spec-standard.md | Completed — [report](reviews/egm-comprehension.md) |
| egm-implementation-readiness | implementation_readiness.md | implementation-readiness-standard.md | Completed — [report](reviews/egm-implementation-readiness.md) |
| egm-structural | structural.md | feature-spec-standard.md | Completed — [report](reviews/egm-structural.md) |

Persona and standard roots are recorded in the shared manifest. Every reviewer attested reading its persona, every supplied standard, target and all non-generated source files. Zoom Out also searched for reuse and found no application implementation outside planning. The source checker is reusable fixture scaffolding, not product validation. Review completion does not mean any Pebbles evaluation has run or any standard has been certified satisfied by implementation.

## Prioritized consolidated findings and dispositions

There are **three consolidated blockers and seven major findings; no standalone nits**. Severity reflects readiness to execute a trustworthy evaluation, not a reason to stop drafting. “Addressed in plan” means a concrete proposed resolution is written; it does not mean the requirement is implemented or tested.

### F01 — Missing package and oracle suite — Blocker

**Lenses:** all six. **Affected scope:** target Proposed first evaluation; BRD Golden dataset/G0; golden fixture files/checker.

The tiny fixture lacks scorecards, SQL, inventories, omissions and case-level claim oracles. Its checker does not enforce timestamps/revisions. A repeat encounter has a distinct event ID and is not necessarily a defect.

**Disposition: addressed in plan, execution outstanding.** The plan defines E00–E05, exact E01 row-denominator defect (2/4 versus 2/3), clean repeat control, boundary probes, independent hidden oracles, preparation requirements and readiness gate R0. Existing fixtures remain arithmetic seeds. No claim of E01–E05 readiness or passing product tests is made.

### F02 — Claim eligibility, status and interpretation contract — Blocker

**Lenses:** all six, especially Design, Codebase Details, Comprehension and Structural. **Affected scope:** target Current user intent; evidence boundary §§2–4; original core model.

Three labels without evidence prerequisites permit unsupported assurance, guessing missing definitions and treating execution failures as experiment defects. Readers may interpret a green status as shipping approval.

**Disposition: addressed in plan, validation outstanding.** Both artifacts define per-check propositions/prerequisites/provenance and separate evidence outcomes from execution states. No overall badge; E03 missing meaning remains unresolved; E04 distinguishes literal disagreement from source truth; E05 delivery unknown. R1 checks forbidden claims; R2 tests participant interpretation. Additional requests are narrow and decision-relevant.

### F03 — Original platform architecture conflicts with current question — Blocker

**Lenses:** Structural (blocker), Design, Zoom Out and Implementation Readiness (major). **Affected scope:** original service boundaries, G0–G5, opportunity-tree CP-1–CP-5.

Carrying original assignment, registry, inference and production execution gates forward would test a different product and create unnecessary dependencies.

**Disposition: accepted and scoped out.** Brief proposes local deterministic intake/check/report flow. Plan creates R0–R3 and explicitly defers old platform gates and integrations. Original source files remain unchanged. A future code plan is separate; this draft is not falsely presented as a complete zero-decision implementation specification.

### F04 — Workflow study confounds and incomplete cost accounting — Major

**Lenses:** all six. **Affected scope:** target comparison; OP-1/CP-P; evidence boundary §5.

Repeated underlying cases teach answers; facilitator labor and preparation may hide costs; small synthetic samples cannot establish general efficacy.

**Disposition: addressed in proposed protocol; residual limits explicit.** Twelve independently authored matched forms, six analysts, two different conditions per analyst, no counterpart repetition, balanced first-method order and hidden oracles. Preparation, mapping, report labor, assistance, onboarding and timeouts are recorded. Difficulty/order confounds remain and are disclosed; results are exploratory. Technical coverage is not counted as independent user evidence.

### F05 — Contradictions and orphan records do not prove source truth — Major

**Lenses:** Codebase Details, Comprehension, Implementation Readiness, Structural, Zoom Out. **Affected scope:** E04; BR-D02/03; exposure contracts.

A scorecard/export mismatch can reflect filters or snapshot differences. Missing assignment in a partial export does not prove unassigned production activity.

**Disposition: addressed in case oracle.** E04 reports both values/provenance, fails only literal agreement, and leaves comparability/root cause insufficient. Orphan/revision probes require package-scoped language. Unknown completeness stays explicit.

### F06 — Temporal, identity and SQL semantics are underspecified — Major

**Lenses:** all six. **Affected scope:** definitions, manifest, checker; SQL-or-definition intake.

Set arithmetic hides time/revision bugs; arbitrary SQL support expands scope; a different denominator may be a different estimand rather than an error.

**Disposition: narrowed and specified.** Plan pins UTC interval inclusivity, strict purchase-after-exposure rule, identity/revision/arm matching, replay versus repeat handling and undefined zero-denominator rate. It inspects supplied SQL as evidence and uses structured definitions for deterministic recomputation; arbitrary SQL execution/equivalence is excluded. Focused probes test promised rules; inferential checks are deferred.

### F07 — Provenance and version changes can rewrite history — Major

**Lenses:** Structural, Implementation Readiness, Codebase Details and Design. **Affected scope:** technical core model/artifacts; BR-D05/D09; source metadata.

Corrected input or updated interpretation must not silently relabel old findings. Declarations cannot become proof of completeness.

**Disposition: addressed with lightweight files.** Immutable original evidence, hashes and rule versions; corrected evidence produces new linked runs; unsupported versions reject explicitly; rollback selects old versions without overwrite. No database migration or registry service assumed.

### F08 — Resource bounds and untrusted supplied content — Major

**Lenses:** Design; Structural and Codebase Details overlap. **Affected scope:** package/SQL intake and operational error behavior.

Local files alone do not bound memory/runtime or prevent arbitrary SQL access. An LLM is not necessary for exact arithmetic and can add unsupported prose claims.

**Disposition: accepted bounded default.** Proposed ten-file/50 MB/100,000-row/2 GB/60-second single-worker envelope, no network or source mutation, no arbitrary supplied SQL execution, visible operational errors and deterministic templates. Optional LLM token cap was not adopted because no LLM is proposed. Capacity remains unmeasured.

### F09 — Value may come from a simpler checklist or report — Major

**Lenses:** Zoom Out, Comprehension, Design, Structural; remaining lenses offer concierge alternative. **Affected scope:** product hypothesis and alternatives.

Known anomaly detection alone is not differentiated value. A checklist may solve the same problem; concierge can test readability but cannot prove automation savings.

**Disposition: alternatives retained with explicit trade-offs.** Brief compares existing workflow/checklist, concierge and deterministic evaluator. Plan uses ordinary analyst tools in baseline, accounts for human report labor if concierge is used, and recommends narrowing/stopping if preparation erases value. Discovery testimony, if collected, remains exploratory.

### F10 — Budget, staffing, thresholds and stopping criteria absent — Major

**Lenses:** all six proposed bounds; Design raised explicit economics finding. **Affected scope:** target unspecified resources; Heilmeier cost/timeline/exams.

Reviewer proposals varied from three to six analysts, five to ten days and 20%–25% improvement. They are suggestions, not evidence or agreements.

**Disposition: reconciled by synthesizer into one proposed plan.** Six analysts × 90 minutes, ten working days excluding recruitment delays, 60 builder plus 16 evaluation/reviewer hours, $600 external cap excluding labor. Proposed R3: no quality degradation, zero critical overclaim/incomplete critical tasks, median effort ratio ≤0.80 and 4/6 lower effort. R1/R2 safety gates cannot be offset by time. Missing participants leave workflow unevaluated. Owners, stop/revise/narrow/proceed decisions and minimal dependency sequence are explicit. Resource availability remains unresolved logistics.

## Coverage of individual reviewer findings

| Report finding IDs | Consolidated disposition |
|---|---|
| Design 1–7 | F02, F01, F03, F08, F08, F04, F10 respectively |
| Codebase Details 1–6 | F02/F07, F01/F06, F02/F08, F05, F01, F04 respectively |
| Zoom Out 1–6 | F01, F03, F09, F04, F01/F06, F02/F05 respectively |
| Comprehension 1–6 | F02, F01, F04/F09, F05, F02, F04 respectively |
| Implementation Readiness 1–6 | F01, F03/F07, F07, F06, F05, F04 respectively |
| Structural 1–5 | F03, F02, F07, F01/F06, F06/F08 respectively |

All reports' alternative/budget/acceptance suggestions are represented by F09/F10 and the final plan; conflicting proposed defaults are reconciled rather than simultaneously imposed. Recommendations requiring a full platform, arbitrary SQL support, production migration or inference validation remain deferred, with the current scope rationale. No reviewer finding is treated as empirical customer evidence.

## Verification and remaining work

Synthesis checked local document links, case arithmetic and schedule balance. The six reviewers assessed the original concept independently, not the final synthesized artifacts; no independent post-synthesis approval is claimed. Parent-run source checker: four tests passed, limited to original fixture consistency. E00–E05, probes, prototype and analyst comparison remain unrun. Next work is evaluation-material readiness, subject to the plan's explicit bounds; no code implementation occurred in this drafting phase.
