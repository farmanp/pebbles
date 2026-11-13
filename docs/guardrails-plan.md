# Guardrails and decision summary

Authorized scope: extend the existing file-based investigator and UI with guardrails and an explained conditional recommendation. Preserve old runs and the original problem tree.

Implementation: versioned binary per-user guardrail observations in guardrails.json, explicit same-experiment/window scope, one observation per assigned user per metric. The UI configures metric ID, direction and maximum acceptable harm in percentage points; study declarations and cost/implementation review notes are saved in the analysis plan. This avoids treating arbitrary aggregate counts or missing events as complete observations. Continuous metrics are deferred.

Use Newcombe/Wilson intervals with Bonferroni confidence adjustment across the declared guardrails (up to 10), compare harm-oriented bounds with the preset margin, and fail closed on unknown evidence or plan errors. This provides bounded approximate simultaneous guardrail intervals, not a new validation of all statistical regimes. Primary inference retains its separate 95% interval.

Decision: primary improvement + all required guardrails within limits + declared reviewed costs/risks with rationale supports a conditional analyst recommendation. Harm or a below-goal primary result argues against shipping; unresolved evidence and uncertainty block a recommendation. Never automatic deployment or independent proof of upstream data.

Steps: failing decision tests; evidence and inference implementation; input/result UI and reports; synthetic supported/harm/uncertain examples; integration and browser verification; problem-tree and method documentation. OP-1 decision, OP-2 contracts, OP-3/4 integrity/calculation, OP-5 conclusion, OP-6 saved reasoning, OP-7 workflow.
