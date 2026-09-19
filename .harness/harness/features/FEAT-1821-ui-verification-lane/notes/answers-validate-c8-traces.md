# Answers — FEAT-1821 validate c8: SC-04 gap + replayable evidence amendment — 2026-09-19

## Ruling 1 — SC-04 is not waived; it gets a gate rule and its fail-first.
`ui_contract.py gate` refuses any `toHaveScreenshot(` in the package's e2e specs when no Checks row carries method `pixel-baseline` (main-session-direct, T-01). Test-first with a mutant; the red run is pinned in the receipt. This is the criterion-mapped SC-04 fail-first QA asked for.

## Ruling 2 — amendment: replayable evidence for interaction checks (operator, 2026-09-19).
The operator wants to SEE that the interaction tests do what they claim; a still shows where a test ended, not what it did. Playwright traces (`trace.zip`, opened with `npx playwright show-trace`) give a per-action filmstrip, DOM snapshots and the failing assertion. Videos were considered and rejected: heavier, not inspectable.

Contract (DESIGN-owned, no ids hardcoded in tooling): the `## Checks` section gains an optional `### Traces` sub-table with one column `Check ID`; every listed id must be a listed check. FEAT-53's DESIGN.md lists C3-KEYBOARD, TBL-DESKTOP, VIS-PROTOTYPE, A11Y-AXE.
Runner (T-03 owner, team): record a trace for those checks at every applicable project, written to `runs/<run-id>/ui/traces/<check>--<project>.zip`; each results record for a traced check carries `trace: <repo-relative path>`. Traces stay out of git ONLY for non-listed checks (unchanged ignore rules; the listed ones are committed with the bundle).
Gate (T-01, direct): manifest exposes `traced_check_ids`; every applicable record of a traced check must carry a `trace` path that exists, is non-empty, is a zip, and sits under the run's ui/ dir — else FAIL by name.
Reviewer (T-05, direct): Mode B must open the trace for every traced check and cite the step it judged; a traced check graded from its still alone is a FAIL finding. Mutant-checked clause.
Evidence for the operator: the briefing names the trace paths and the one-line command to open each.

## Budget
Rework: the fix loop after this amendment gets rounds=9, minutes=405 (one more round). Cycle ceiling 10→12 (amend + one eng run + one validate would land exactly on 10 with no reserve; raise recorded here with reason). Approval resets on add-tasks; Main re-signs from this note.
