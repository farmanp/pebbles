# Analyst workspace redesign

Approved scope: Experiments → Investigation → Decision, retaining existing functionality and data.

Design: white work surfaces on cool grey (#f3f5f8), dark navy text (#23344a), indigo actions (#4358bb), amber unresolved evidence (#946416), green verified evidence (#286759). Avenir Next / system sans for navigation and prose; tabular numbers for estimates. Left alignment, compact 28px page titles, generous separation between result and supporting work. No decorative hero or metric-card grid.

Experiments is a searchable queue with run count, unresolved work and review state. Investigation places the selected run, rate comparison, uncertainty and blockers above evidence, findings, revisions and follow-ups. Decision shows recorded judgments first and opens recommendation forms on demand. Existing handlers/data contracts remain; layout composition moves the existing functional forms into task-specific sections. Older full reports remain accessible. Responsive stacking and keyboard focus must work.

Validation: JS syntax and existing regressions, then Computer Use list → investigation → evidence → decision → review/handoff, plus responsive visual inspection. No analyst-value claims from AI operation.

## Implemented and verified

The app now opens to the experiment queue. Select an experiment for Investigation and Decision tabs. Investigation shows the selected run's result, rates, interval and blockers, followed by expandable findings and task-based evidence work. Decision shows the latest record first, collapses earlier records and opens the recommendation form on demand. Search, task state, source previews, full reports, corrected CSVs, package revisions, follow-ups, reviewed decisions and handoff downloads remain available. Workspace routes survive reload; the default run is explicitly labeled last attached, not authoritative.

Layout uses a side navigation at wide widths and a top navigation in the observed 728px browser. Package imports remain accessible at narrow widths. The browser was visually inspected at its current narrow viewport; no claim of a device-matrix test is made.

Computer Use exercised experiment search; original/corrected run selection; source import.json preview; full report and back navigation; corrected CSV entry; creation of an I04 evidence request; earlier stale decision inspection; recommendation form and exact-run blocker preview; handoff ZIP download; and reload persistence. It did not repeat a full CSV upload or submit a new decision in this redesign pass. Prior backend execution remains covered by existing tests.

65 regression tests passed; changed JavaScript passed syntax checks. Independent review found and fixed reference-versus-export headline mixing, stale run content during loading/failure, delayed decision preview crossing form instances, and hidden package navigation on narrow screens. Browser work caught and fixed a route name collision and the initial earlier-record DOM wrapping error. The downloaded decision packet's manifest fingerprints all matched.

Screenshots: [Experiments](../pilot-self-try/redesign-experiments.jpg), [Investigation](../pilot-self-try/redesign-investigation.jpg), [Decision](../pilot-self-try/redesign-decision.jpg).

Problem tree: OP-7 improves navigation and reduces persistent form clutter; OP-1/5 keep result versus decision distinct; OP-3/4 retain investigation/evidence work; OP-6 retains exact run links, old decisions and exports. This is an AI-operated usability and functionality check, not a human analyst evaluation. No analytical outcomes or saved decision records were rewritten.
