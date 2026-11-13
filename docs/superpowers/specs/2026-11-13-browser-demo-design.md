# Browser demo

Visitors follow a README link and use the real Pebbles analyst UI without an install. Reuse the Python engine in a Pyodide worker and publish static assets on GitHub Pages. Each tab has an independent, temporary virtual filesystem; reload resets it. State the lifetime prominently and offer existing report/handoff downloads. Seed the existing synthetic original/corrected checkout investigation. CSV intake, investigation, findings, revisions and decisions use existing Python handlers, not canned API responses.

Alternatives considered: a hosted Python service needs per-visitor storage, quotas and ongoing operation; a read-only report does not fulfill the request to try Pebbles. Browser execution fits the public demo and keeps selected data off a shared backend. Initial runtime download is a tradeoff. Modern WebAssembly-capable browsers and an internet connection are required. Local installation remains the durable-workspace option.

Publish only explicitly selected source, static UI and synthetic fixtures. No Cookie Cats records, answer keys, local workspace files or credentials. Pin runtime and CI action versions. Do not weaken local server origin/token checks. Serve through a worker adapter that invokes request handlers in memory, without binding a socket. Catch runtime initialization errors with a useful retry and local alternative. Queue requests to avoid concurrent Python execution. Intercept API download links as well as fetch calls; account for the /pebbles/ Pages subpath.

Problem tree: OP-1/7 lower trial friction; OP-3/4/5 retain evidence checks, explanations and decisions. Deployment is not evidence of analyst effectiveness.
