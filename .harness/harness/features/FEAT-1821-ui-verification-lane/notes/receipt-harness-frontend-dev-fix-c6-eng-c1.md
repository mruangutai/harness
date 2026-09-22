# FEAT-1821 fix-c6 teardown-time capture receipt

## BLUF
The retry moves each vulnerable execution capture into Playwright `test.afterEach`, before fixture disposal. The sole configured lane listed 23 tests in 6 files and produced complete WebP evidence: all 23 records have at least one valid referenced WebP and no duplicate or missing record exists. The lane remains product-red (22 failed, 1 passed); capture itself did not fail.

## Source
- `e2e/geometry.e2e.spec.ts`, `e2e/colour-placement.e2e.spec.ts`, `e2e/contrast-hatch.e2e.spec.ts`, `e2e/keyboard.e2e.spec.ts`, and `e2e/tables-a11y.e2e.spec.ts`: resolve the current contract check from `testInfo.title` in file-local `test.afterEach` and capture exactly once per applicable check/project; removed the prior in-body/finally captures.
- `feat-53.e2e.spec.ts` was inspected but unchanged: its inspection flow captures each evidence label independently, and the prior bundle had no missing root-spec evidence. Geometry header locator waits retain their explicit 1s limits.

## Commands and proof
1. `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=fix-c6-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list`
   - Exit 0; `Total: 23 tests in 6 files`.
2. `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=fix-c6-smoke npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui`
   - Exit 1; 22 failed, 1 passed. All 23 checks started. Failure output contains existing predicates and timeout fallout, while each vulnerable test attached its `execution` WebP from teardown.
3. Results audit (`runs/fix-c6-smoke/ui/results.json`)
   - `harness-ui-results/1`; feature/run/served commit correct; 23 records; 12 listed, 23 applicable, 12 observed, `missing_check_ids: []`; 41 screenshot references; empty records `[]`; duplicate check/project records `[]`; invalid/missing/sub-13-byte/non-RIFF/non-WEBP evidence `[]`.
4. Gate command (exit 1):
   ```sh
   python3 .claude/skills/harness/bin/ui_contract.py gate --design .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --results .harness/harness/features/FEAT-53-metrics-dashboard/runs/fix-c6-smoke/ui/results.json --feature FEAT-53-metrics-dashboard --run-id fix-c6-smoke --served-bundle-commit c21310c82d8b86562a58fc361496e13e01b0fde9 --repo-root . --client-package .claude/skills/harness/bin/dashboard/client --changed .claude/skills/harness/bin/dashboard/client/e2e/geometry.e2e.spec.ts --changed .claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts --changed .claude/skills/harness/bin/dashboard/client/e2e/keyboard.e2e.spec.ts --changed .claude/skills/harness/bin/dashboard/client/e2e/contrast-hatch.e2e.spec.ts --changed .claude/skills/harness/bin/dashboard/client/e2e/tables-a11y.e2e.spec.ts
   ```
   - Combined output: `UI GATE: FAIL`; it contains honest predicate failures and dynamic-title discovery refusals, but does **not** contain `no screenshot evidence`. Full tool output: `artifact://2670`.
5. Infrastructure scan: no collection/import/config/fixture/reference/capture error was emitted by capture; the serialized product errors do contain `Target page, context or browser has been closed` after 30s whole-test timeout while remaining predicate clauses continue. Those are existing timeout fallout, not evidence-capture failures; every affected record has a valid teardown WebP.

## Cleanup
Attempted `rm -rf` only after recording the proof. The domain guard denied `.harness/harness/features/FEAT-53-metrics-dashboard/runs/fix-c6-list` before any deletion because it is outside frontend ownership; remaining cleanup paths are that directory, `.harness/harness/features/FEAT-53-metrics-dashboard/runs/fix-c6-smoke`, and `.claude/skills/harness/bin/dashboard/client/test-results` for Main/lead.
