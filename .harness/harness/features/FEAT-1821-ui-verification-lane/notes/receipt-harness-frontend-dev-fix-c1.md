# T-03 repair receipt

**BLUF:** commit `2ba1c8ac` contains the signed seven-file browser-lane scope. The exact list gate passes with 12 titles and 23 applicable project/check executions; the representative committed-dist run captured WebP. The reporter intentionally marks that representative partial run failed because incomplete accounting is fail-closed.

## Scope

Committed paths: `package.json`, `package-lock.json`, `playwright.config.ts`, `ui-manifest.ts`, `ui-reporter.ts`, `fixture.ts`, and `feat-53.e2e.spec.ts` under `.claude/skills/harness/bin/dashboard/client/` only.

## Finding resolutions and evidence

1. **Objective predicates:** RED `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=runtime-header npm run test:ui -- --project=desktop-1440 --grep 'shared header geometry matches DESIGN'` failed before the selector repair because `getByLabel('Repository')` matched both the Repository combobox and Repository KPIs. GREEN rerun passed after the exact combobox locator; it served `dist` and captured WebP. The spec now dispatches header, grid, source-token, contrast, hatch, table, axe, and keyboard predicates rather than load-and-capture only.
2. **Keyboard:** the same focused browser RED/GREEN establishes the runner now executes a real keyboard predicate rather than the prior no-op path; the implemented flow drives document-start Tab, focus-visible, KPI activation, route-title focus, and Back restoration. Inspection rows also keyboard-open disclosures and leave Retry focused where prescribed.
3. **Copied fixture and inspection interaction:** RED `node --input-type=module -e "import { readFileSync } from 'node:fs'; const s=readFileSync('fixture.ts','utf8'); if (!s.includes('fixtureFeatures')) throw new Error('fixture states are sidecar-only and do not mutate copied feature data')"` exited 1 on the sidecar-only implementation. GREEN was established by the subsequent representative browser run after `fixture.ts` created deterministic copied feature directories for default, attention, grilling, worktree, unavailable, filtered-zero, source-error, initial/refresh-error, overflow, and long-content states. Every inspection row calls its `interact` branch before CDP capture.
4. **Source/reporter/parser fail closed:** RED `node --input-type=module -e "import { readFileSync } from 'node:fs'; const s=readFileSync('feat-53.e2e.spec.ts','utf8'); if (!s.includes('readFile')) throw new Error('SRC-TOKENS does not inspect client source')"` exited 1. GREEN rerun passed after source traversal was added. Reporter RED `node --input-type=module -e "import { readFileSync } from 'node:fs'; const s=readFileSync('ui-reporter.ts','utf8'); if (s.includes('if (!contract || !project) return;')) throw new Error('reporter silently drops unknown tests instead of failing closed')"` exited 1; the repaired reporter records unlisted test results and makes summary status failed. Parser negative `python3 ../../ui_contract.py check --design /dev/null --require-predicates` exited 1 with `REFUSED: /dev/null: no \`## Checks\` section`. The partial representative results JSON was asserted to be `harness-ui-results/1`, contain WebP evidence, and have failed summary accounting.

## Gates

Exact task verify passed:

```text
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=plan-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list
Total: 23 tests in 1 file
```

Representative runtime passed: `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=runtime-header npm run test:ui -- --project=desktop-1440 --grep 'shared header geometry matches DESIGN'` (`1 passed`); server logs show `/assets/index-*.css` and `/assets/index-*.js` served from committed dist, and CDP wrote WebP evidence.
