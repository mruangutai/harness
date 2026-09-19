# fix-c5 receipt

The split lane no longer performs fixture preparation during Playwright config evaluation: `fixturePath()` is pure, `fixture.ts` is `globalSetup`, and its default setup calls `prepareFixtureSync()` once before workers. The web-server prerequisite sentinel is created only when the configured server command starts; global setup replaces it with the shared run fixture before browser work.

## Hypothesis and fix

Hypothesis: config-module evaluation in the main process and each worker calls `prepareFixtureSync()`, racing recursive deletion/copy for the same run fixture; `feat-53.e2e.spec.ts` also references an undeclared `overview`. Falsifier: a four-worker lane still reports `ENOTEMPTY`, `ENOENT`, or `ReferenceError` after configuration is made pure and global setup owns preparation. The smoke result contains none of those terms.

Changed files:

- `.claude/skills/harness/bin/dashboard/client/fixture.ts`
- `.claude/skills/harness/bin/dashboard/client/playwright.config.ts`
- `.claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts`

## Verification

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=fix-c5-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list
```

Exit `0`; output: `Total: 23 tests in 6 files`.

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=fix-c5-smoke npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --workers=4
```

Exit `1` only because current UI predicates remain false. `results.json` reported `check_count=23`, `records=23`, `missing_check_ids=[]`, and status counts `{'evidence': 4, 'failed': 18, 'passed': 1}`. A serialized-results scan reported `forbidden_matches=0` for `ENOTEMPTY`, `ENOENT`, and `ReferenceError`.

Remaining honest predicate failures are the pre-existing UI contract failures (including contrast token ratios, missing KPI identity marks, geometry/keyboard/table/a11y predicates, and inspection evidence-accounting mismatches); they were not suppressed or edited. `SRC-TOKENS` passed.

## Cleanup

Cleanup complete: `.harness/harness/features/FEAT-53-metrics-dashboard/runs/fix-c5-list` and `.harness/harness/features/FEAT-53-metrics-dashboard/runs/fix-c5-smoke` are absent; the generated client `test-results/` tree, including `fixtures/fix-c5-smoke`, was removed after evidence extraction.
