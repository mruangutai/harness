# FEAT-1821 fix-c6 frontend receipt

## BLUF
The required smoke run discovered 23 tests and wrote a valid 23-record results bundle, but the change does not meet the unconditional-evidence acceptance: 10 records have no screenshot because their tests reached the 30-second test timeout before `finally` could capture. The real UI gate therefore contains `no screenshot evidence` and exits 1.

## Source change
- `.claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts`: encompass initial load and predicates in the existing capture `finally`.
- `.claude/skills/harness/bin/dashboard/client/e2e/contrast-hatch.e2e.spec.ts`: move both checks' sole capture to an outcome-independent `finally`.
- `.claude/skills/harness/bin/dashboard/client/e2e/geometry.e2e.spec.ts`: bound every C1 header expectation at 1s, well below the 30s test budget.
- `.claude/skills/harness/bin/dashboard/client/e2e/tables-a11y.e2e.spec.ts`: replace branch-local captures with one check-scoped `finally`.

## Commands and evidence
1. `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=fix-c6-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list`
   - Exit 0. Output ended `Total: 23 tests in 6 files`.
2. `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=fix-c6-smoke npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui`
   - Exit 1, 22 failed / 1 passed after 1.7m. It collected and started all 23 tests; no collection, import, fixture, or config-load error was printed. Existing predicate failures were present. Ten tests hit the 30s test timeout; their subsequent `page.addStyleTag: Target page, context or browser has been closed` capture errors are the unresolved evidence failure.
3. Results audit of `runs/fix-c6-smoke/ui/results.json`
   - Schema `harness-ui-results/1`; feature/run correct; 23 records; `missing_check_ids: []`; duplicate project/check records: 0.
   - 31 screenshot references are existing RIFF/WebP files (the `file` scan reported every reference as `RIFF (little-endian) data, Web/P image`).
   - 10 records have zero screenshot references, so the required every-record non-empty WebP/header proof fails.
4. `python3 .claude/skills/harness/bin/ui_contract.py gate --design .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --results .harness/harness/features/FEAT-53-metrics-dashboard/runs/fix-c6-smoke/ui/results.json --feature FEAT-53-metrics-dashboard --run-id fix-c6-smoke --served-bundle-commit c21310c82d8b86562a58fc361496e13e01b0fde9 --repo-root . --client-package .claude/skills/harness/bin/dashboard/client --changed .claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts --changed .claude/skills/harness/bin/dashboard/client/e2e/contrast-hatch.e2e.spec.ts --changed .claude/skills/harness/bin/dashboard/client/e2e/geometry.e2e.spec.ts --changed .claude/skills/harness/bin/dashboard/client/e2e/tables-a11y.e2e.spec.ts`
   - Exit 1. Combined output began `UI GATE: FAIL` and includes the forbidden `no screenshot evidence` reason (including C4-HATCH, C1-HEADER-GEOMETRY, A11Y-AXE, C3-KEYBOARD, and TBL-DESKTOP records), alongside honest predicate failures.

## Cleanup
Cleanup is blocked by the frontend domain guard: it denied removal of the FEAT-53 run directories as outside this role's write domain. The listed throwaway bundles and client scratch directory remain for the lead/main agent to remove.
