# T-35 receipt

## Result

Every valid captured manifest trace is now copied before failure accounting is summarized; failing/incomplete results retain their failed status and errors. A11Y-AXE diagnostics now name every violation's id, impact, and first target selector.

## Debug hypothesis

The trace-loss path was caused by `ui-reporter.ts:onEnd` making trace copying conditional on `reporterErrors.length === 0`; a forced reporter error therefore preserved trace metadata in `results.json` but wrote no ZIPs. Falsifier: a forced-error run that still has no trace ZIPs after moving publication outside that condition.

## Evidence

- Pre-fix reproduction (exit 0): `HARNESS_UI_RUN_ID=t35-prefx node --experimental-strip-types t35-trace-smoke.ts` emitted `summary.status: failed`, retained `forced reporter error`, `missing record`, and `incomplete accounting`, listed all eight exact trace destinations, and the `traces/` directory did not exist.
- Post-fix focused smoke plus intentionally incomplete gate (command exit 1 because the gate correctly refused the incomplete bundle): `HARNESS_UI_RUN_ID=t35-postfix node --experimental-strip-types t35-trace-smoke.ts && python3 ../../ui_contract.py gate --design ../../../../../../.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --results ../../../../../../.harness/harness/features/FEAT-53-metrics-dashboard/runs/t35-postfix/ui/results.json --feature FEAT-53-metrics-dashboard --run-id t35-postfix --served-bundle-commit "$(git -C ../../../../../../ rev-parse HEAD)" --repo-root ../../../../../../ --client-package .`
  - Smoke output retained failed summary and all three errors, and published exactly: `C3-KEYBOARD`, `TBL-DESKTOP`, `A11Y-AXE`, and `VIS-PROTOTYPE` ZIPs for both `desktop-1440` and `desktop-1920`.
  - Gate output began `UI GATE: FAIL` and included `missing_check_ids is not empty`, proving independent refusal of the intentionally incomplete bundle.
- Reporter regression probe (exit 0): `node --experimental-strip-types --test ui-reporter.probe.spec.ts` — 15 pass, 0 fail.
- Focused browser accessibility run (exit 1): `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t35-axe npm run test:ui -- e2e/tables-a11y.e2e.spec.ts` — 2 passed and 2 failed on the unrelated existing `every gap treatment` assertion (`Expected: 0; Received: 1`); it produced no axe violation to format. Narrow disposable formatting smoke (exit 0) emitted `loaded overview: button-name (critical): #retry, color-contrast (serious): .status-label`, exercising id, impact, and first selector rendering. Disposable scripts and runs were removed.
- Signed verification, run verbatim from the feature root (exit 0):
  - `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t35-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list | grep -c "›" # still 23 titles at both projects` → `23`
  - `git diff --stat HEAD -- .claude/skills/harness/bin/dashboard/client | grep -c "ui-reporter.ts\|tables-a11y.e2e.spec.ts" # only these two client files changed by this task` → `2`
- Ownership-aware before/after: before, neither signed T-35 path appeared in the dirty client-path list; after, `git diff --name-only HEAD --` limited to the two signed paths listed only `e2e/tables-a11y.e2e.spec.ts` and `ui-reporter.ts`, while both disposable scripts were absent.

## Files touched

- `.claude/skills/harness/bin/dashboard/client/ui-reporter.ts`
- `.claude/skills/harness/bin/dashboard/client/e2e/tables-a11y.e2e.spec.ts`

## Principles applied

- Make Operations Idempotent: trace publication now converges to the required copied trace state regardless of pre-existing reporter errors.
