# Pinned code review — FEAT-1821 — c0

**BLUF:** FAIL at Stage 1. The independent Python evidence gate accepts a DESIGN contract whose required inspection evidence manifest has been removed, contrary to SC-05 and T-01. Stage 2 was therefore not entered. Review head is exactly `711ba16227eda39ddb397ed574e4ca199fbc5984`.

## Stage 1 — spec compliance: FAIL

### F-01 — high · substance · T-01 / main-session-direct

`ui_contract.py:229` calls `load_manifest(design)` without `require_predicates=True` or `require_inspection_evidence=True`, although those enforcement switches exist at `ui_contract.py:84-86` and the reporter uses them at `dashboard/client/ui-manifest.ts:14`. A DESIGN change that retains check rows but deletes `### Inspection evidence` therefore passes the independent gate when results are otherwise green: measured against the pin by removing that section from a temporary DESIGN copy and converting only the intentional product RED records to green; `gate(...)` returned `PASS []`. QA can consequently trust generic screenshots with no signed route/state/interaction manifest. This violates SC-05 and T-01. Fix: enable both requirements in `gate` and add gate-level mutants for removed manifest and empty predicate. Owner: T-01, main-session-direct.

### Inspection SCs

- SC-07 satisfied: `playwright.config.ts:6-24` pins viewports/rendering inputs and the fixture/specs supply the named states.
- SC-08 satisfied: `.omp/agents/harness-ui-reviewer.md:41-76` requires pinned results/WebPs, complete accounting and declared capture context, configured-lane-only reruns, and FAIL on absent/stale/mismatched evidence.
- SC-09 satisfied: `DESIGN.md:860-934` carries exact-title executable rows and inspection-only qualitative manifests.
- SC-12 satisfied: `.github/workflows/tests.yml:84-90` installs Chromium from the dashboard package immediately after its `npm ci` with the signed command.

### Assessed and dismissed

- The FEAT-53 bundle's 22 failed predicates are intentional product RED, not FEAT-1821 defects; `results.json:1083-1087` honestly records failed status and no reporter errors.
- Failure screenshots are preserved: `feat-53.e2e.spec.ts:93-105` captures after guarded interaction, while `ui-evidence.ts:8-28` validates and writes before attaching.
- The seven probes are real two-stage checks: `ui-reporter.probe.spec.ts:68-86` reads reporter-emitted JSON then invokes the Python gate; cases are at lines 88-123.
- Missing/duplicate/title/empty/accounting and stale-pin paths otherwise fail closed at `ui_contract.py:247-302`; applicability is checked per check/project at lines 262-285.

## Stage 2 — not entered; mandatory mechanical audit recorded

Protocol stops code-quality judgement after Stage 1 failure. The canonical grader nevertheless reports `fail` over `23d6745b888b492b92ae61e5dcaa5992c066f9c4..711ba16227eda39ddb397ed574e4ca199fbc5984`:

- `ui_contract.py:61` `_table_after`: cyclomatic 9, cognitive 15, ABC 25.7, grade 3, driver all three — high.
- `ui_contract.py:138` `_inspection_evidence`: cyclomatic 19, cognitive 42, ABC 34.0, grade 1, driver cognitive — high.
- `ui_contract.py:213` `gate`: cyclomatic 47, cognitive 62, ABC 97.0, grade 1, driver all three — high.
- `ui_contract.py:306` `_screenshot_reasons`: cyclomatic 9, cognitive 11, ABC 17.1, grade 3, driver cyclomatic+cognitive — high.

These are independently gating mechanical findings under T-01/main-session-direct. Grade-2 records also exist but do not alter `code_grade: fail`: `load_manifest` and CLI `main` in `ui_contract.py`, plus test orchestrator helpers, are cohesive parsing/orchestration functions; their reasons would be required only if the aggregate were `grade_2`.
