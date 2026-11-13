# Frozen evaluation check contract 1.0.0

Prepared for review; behavioral rules and thresholds are pinned before results. R0 is Not yet evaluated: independent oracle review and matched-difficulty dry run remain pending. Changing this contract requires a versioned reason and affected-package/oracle regeneration before scoring.

## Metric and record semantics

Experiment checkout-button, revision 1; user_id unit; control/treatment; UTC interval [2026-01-01T12:00:00Z, 2026-01-02T12:00:00Z). A valid assignment is within this interval. Exposure must match experiment, revision, user and assignment arm, be within this interval and at or after assignment. v1 denominator is distinct qualifying exposed users; numerator counts those users with any purchase attributed by user_id to the unique valid assignment (inheriting its arm/experiment/revision under an explicit supplied mapping) strictly after first qualifying exposure and before the exclusive end. v2 independently labels assigned users and purchases strictly after qualifying assignment before end. Never substitute versions. Outcome records contain user_id and timestamp, not fabricated scope fields: the versioned definition explicitly declares this assignment join. Without that declaration, do not infer intended attribution from fixture knowledge. Eligibility is the explicit synthetic assignment rule; no claims about historical targeting. Unknown identity, eligibility, time or attribution semantics blocks the affected evidentiary conclusion as Insufficient evidence.

New event ID for the same user is a legitimate repeat. Identical payload/event-ID replay counts once and gets an informational note. Conflicting payloads for one event ID block affected metric execution as blocked-invalid-input with null evidence outcome; preserve unaffected completed checks. Orphans, mismatched revisions/arms and crossovers are cited and excluded from the explicitly labeled valid subset. Conflicting assignments for a user make that user's anchor/arm unresolved; do not select an assignment arbitrarily. Missing fields needed to parse a supplied record are invalid input; absent artifacts/prerequisite semantics give completed Insufficient evidence. An orphan in an export of unknown completeness proves no production root cause. Empty supplied records yield zero observed users and undefined zero-denominator rate, not zero real-world activity.

Counts use exact integers; rates use exact rational numerator/denominator (null for undefined). Three-decimal displayed percentage tolerance is absolute 0.000005 on a 0–1 rate, inclusive. No inference, significance, confidence interval, power, SRM calibration or causal calculations are scored. Supplied SQL is evidence only; the bounded COUNT row-versus-distinct-user recognition is supported, arbitrary SQL execution prohibited. Unsupported SQL analysis is blocked-unsupported-operation, not a failed experimental claim.

## Finding and execution contract

Every planned check has a record: check_id/version, exact proposition, scope, prerequisites, evidence references (artifact ID, relative path, row/JSON pointer, SHA-256), calculation/reason, expected/observed when defined, execution_state, evidence_outcome, limitations and next_evidence_request (what decision it unlocks and analyst/other-team provider). State scope beside outcome under the question headings below. No overall analytical pass badge or percent passed.

Execution states: Completed, blocked-invalid-input, blocked-unsupported-operation, errored. Only Completed has an evidence outcome: Verified, Failed, Insufficient evidence. Noncompleted outcome is null. Run state Completed/partial/failed is separate from gates Not yet evaluated/pass/fail/blocked. Partial retains completed findings and prominently enumerates uncompleted checks. Parse errors include file/line if available; exceptions include diagnosis without interpreting them as evidence. Unknown optional provenance narrows only dependent checks.

Package inventory requires artifact_id, relative_path, type/schema_version, sha256, source, export_timestamp or unknown, grain or unknown, population/filter/window, experiment/revision when known, completeness declared/unknown and declaration_source. Preserve source files; explicit mappings only. Unsupported package versions are rejected visibly.

## Check catalog

### C01 — What records are present?

**Proposition:** Counts of supplied rows and distinct users are correct.

**Prerequisites:** Parseable records and documented fields; no metric definition needed for explicitly labeled record facts.

Alias: `record_counts`; version 1.0.0.

### C02 — What does the declared metric calculate?

**Proposition:** Exact numerator, denominator and rational rate follow the supplied versioned definition.

**Prerequisites:** Explicit identity, eligibility, assignment, window and attribution semantics; required event exports; no unresolved relevant event-ID conflict.

Alias: `metric`; version 1.0.0.

### C03 — Does the supplied SQL use the intended denominator?

**Proposition:** The supported simple SQL denominator uses distinct qualifying users when the definition requires them.

**Prerequisites:** Definition and recognizable bounded COUNT(*) versus COUNT(DISTINCT user_id) SQL; never execute SQL.

Alias: `sql_denominator`; version 1.0.0.

### C04 — Do displayed scorecard fields agree arithmetically?

**Proposition:** Each nonnegative integer numerator is <= denominator and its displayed rate matches its own fields.

**Prerequisites:** Scorecard numerator, denominator, rate and declared rounding. Zero denominator requires undefined rate.

Alias: `arithmetic`; version 1.0.0.

### C05 — Does the scorecard match the declared calculation?

**Proposition:** The reported fields equal the metric calculation over comparable scoped evidence.

**Prerequisites:** C02 completed with supported calculation, scorecard, and established shared analytical scope. Missing definition or unresolved comparability gives Insufficient evidence.

Alias: `scorecard_agreement`; version 1.0.0.

### C06 — Do these two displayed counts equal each other?

**Proposition:** The explicitly cited numbers in two supplied artifacts are equal.

**Prerequisites:** Two readable fields; comparability is NOT a prerequisite for literal numeric equality. Inequality is Failed without deciding which source is correct.

Alias: `literal_counts`; version 1.0.0.

### C07 — Can these sources be compared semantically?

**Proposition:** Sources describe the same population, filters, window, snapshot and metric.

**Prerequisites:** Provenance establishing those dimensions; unknown scope gives Insufficient evidence, not an assumed match.

Alias: `comparability`; version 1.0.0.

### C08 — Which supplied records qualify or conflict?

**Proposition:** Record references and scoped exclusions/replays follow the pinned identity and timing rules.

**Prerequisites:** Parseable relevant event and assignment fields; label unknown completeness separately.

Alias: `event_integrity`; version 1.0.0.

### C09 — Was treatment actually rendered correctly?

**Proposition:** Supplied implementation/render evidence establishes the named delivery behavior.

**Prerequisites:** Relevant implementation/render evidence; analytical agreement alone always Insufficient evidence.

Alias: `delivery`; version 1.0.0.

### C10 — Do these exports establish production completeness?

**Proposition:** Independent evidence establishes capture of the specified production population.

**Prerequisites:** Independent capture/completeness evidence. A declared synthetic scope is not proof of production completeness.

Alias: `completeness`; version 1.0.0.

### C11 — What does this evidence justify?

**Proposition:** Report makes no unsupported production, inference, causality, shipping or experiment-wide assurance.

**Prerequisites:** Report text and admitted evidence; this is a report-quality assertion, not a new experiment success badge.

Alias: `claim_boundaries`; version 1.0.0.

### C12 — Which checks executed?

**Proposition:** Execution failures are visible with affected propositions and no fabricated outcomes.

**Prerequisites:** Planned coverage inventory and operational records; missing evidence is distinct from parser/unsupported/error states.

Alias: `operational_state`; version 1.0.0.

### C13 — Are results reproducible and immutable?

**Proposition:** Identical/reordered inputs yield identical canonical findings; changed definitions create new runs without altering prior evidence.

**Prerequisites:** Paired run artifacts, versions and hashes; exclude only run ID/timestamps/runtime/machine metadata from canonical comparison.

Alias: `replay_versioning`; version 1.0.0.
