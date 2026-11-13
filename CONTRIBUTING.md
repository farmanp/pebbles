# Contributing

Use Python 3.11+ and Node.js 22 for browser-script syntax checks. Runtime Python dependencies are standard-library only.

```sh
python3 scripts/setup_fixtures.py --with-public-data
python3 -m unittest discover -s tests -v
for file in pebbles/static/*.js; do node --check "$file"; done
```

Work on a short-lived branch and submit a pull request against main. Keep changes scoped; include purpose, validation and effects on saved evidence or decisions. CI must pass before merging. GitHub enforces pull requests, up-to-date passing Python 3.11 and 3.13 CI checks, resolved conversations and linear history on main, including for administrators. Force pushes and branch deletion are blocked. No independent approval is required while this is a solo-maintainer project. The owner may self-review until another maintainer is available; do not represent that as independent review.

Keep evidence outcomes separate from workflow states. Never turn absent evidence into a pass, overwrite old runs, or treat a recorded reviewer name as authenticated approval. Preserve numerical and explanation parity across the UI and exports. Test substantive behavioral changes; use Computer Use for UI flows and describe exactly what was exercised.

Do not commit analyst exports, local workspace databases, secrets, private handoff bundles or downloaded third-party datasets. Fixture generators and pinned provenance belong in Git. The pilot's facilitator keys are evaluation material, not runtime inputs; keep them hidden from participants.

## Keep changes readable

- Give each function one responsibility. Separate input validation, calculation, policy and presentation when they change for different reasons.
- Use descriptive names and ordinary multiline control flow; do not compress branches or multiple statements onto one line.
- Reuse shared rules and calculations. Extract helpers for a concrete responsibility or repeated behavior, without adding generic frameworks for one caller.
- Keep decision precedence explicit: harmful evidence still argues against shipping when other evidence is missing; missing or uncertain evidence never establishes safety.
- For decision refactors, verify complete output parity (including explanations and blocker order), not just the final status. Cover invalid inputs and threshold boundaries.
