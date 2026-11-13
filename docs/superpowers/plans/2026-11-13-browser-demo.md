# Browser Demo Implementation Plan

**Goal:** A public, interactive README demo requiring no installation.
**Architecture:** GitHub Pages static UI + Pyodide worker + existing Python request handlers and tab-local storage.
**Tech Stack:** Python stdlib, vanilla JavaScript, Pyodide 0.27.7, GitHub Pages.
**Spec:** docs/superpowers/specs/2026-11-13-browser-demo-design.md

## Constraints and review focus
No shared visitor data; no local secrets or public dataset redistribution. Keep local server protections intact. Verify initialization failures, nested-path assets, downloads, tab isolation and real computed results. Reload resets state, clearly disclosed.

## Tasks
- [x] Test the Python bridge: original/corrected results, fresh storage isolation, CSV preview, errors and binary handoff ZIP.
- [x] Implement webdemo/bridge.py with dispatch(storage, method, path, body) returning a JSON transport envelope using existing Handler methods.
- [x] Build webdemo/worker.js and bootstrap.js to initialize pinned Python, serialize calls, intercept fetch/downloads, and load unchanged application scripts after seeding.
- [x] Add scripts/build_web_demo.py with an explicit release-file allowlist and package-content tests. Add loading/error/session-lifetime UI.
- [ ] Add pinned Pages workflow and browser-demo tests to CI; verify locally through Computer Use.
- [ ] Merge through required CI, enable and verify Pages deployment, test public flow through Computer Use, then publish README demo link through a passing PR.

## Validation ledger
Browser runtime successfully seeded and calculated original +10 pp and corrected -5 pp. A newly run guardrail case produced refund harm and an against-shipping conclusion. Downloaded handoff ZIP verified (16 entries). Fresh review caught home-link reset, stale build output and worker constructor failures; all addressed. Local HTTP tests require loopback permission in the execution sandbox.
