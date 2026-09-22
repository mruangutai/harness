# T-03 receipt — Astryx StyleX peer repair

## Result

Pinned `@stylexjs/stylex` to exact `0.19.1` in the client manifest and lock. npm metadata reported the compatible `0.19.x` releases as `0.19.0` and `0.19.1`; `0.19.1` satisfies `@astryxdesign/core@0.6.2`'s `^0.19.0` peer. `@testing-library/dom` remains exact `10.4.1`.

The signed UI listing passes with exactly 23 tests. The focused component suite now loads StyleX and passes, but its runner reports **27**, not the required 23, tests; consequently T-03 acceptance is not met.

## Fail-first evidence

The prior T-03 receipt, `notes/receipt-harness-frontend-dev-fix-c7-eng-T-03.md:29-37`, records the already-observed component-suite failure after the DOM repair:

```text
Test Files  5 failed (5)
Error: Cannot find package '@stylexjs/stylex' imported from .../node_modules/@astryxdesign/core/dist/AppShell/AppShell.js
```

That known failing state was not rerun.

## Dependency and diff scope

- Manifest pin: `@stylexjs/stylex: "0.19.1"` under `dependencies`.
- Lock entry: `node_modules/@stylexjs/stylex` at `0.19.1`, plus its required `css-mediaquery`, `invariant`, `loose-envify`, `styleq`, and shared `js-tokens` production-marking metadata.
- `npm install --package-lock-only --ignore-scripts --save-exact --legacy-peer-deps @stylexjs/stylex@0.19.1` exited `0`.
- Scoped diff contains only `client/package.json` (one insertion) and `client/package-lock.json` (46 insertions, one required `dev` metadata removal); no unrelated versions changed.
- Branch: `feat/FEAT-1821-ui-verification-lane`.
- No `test-results`, `playwright-report`, `blob-report`, or `.ui-*` transient output exists.

## Verification

```text
$ npm view @stylexjs/stylex@0.19 version --json
[
  "0.19.0",
  "0.19.1"
]
exit status: 0

$ npm --prefix .claude/skills/harness/bin/dashboard/client run test

> test
> vitest run


 RUN  v5.0.1 /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.claude/skills/harness/bin/dashboard/client

Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method
Not implemented: Window's scrollTo() method

 Test Files  5 passed (5)
      Tests  27 passed (27)
   Start at  08:38:42
   Duration  2.53s (import 39%, environment 36%, tests 19%, transform 5%, setup 1%, worker 1%)

exit status: 0
counts: 5 files passed; 27 passed; 0 failed

$ HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=plan-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list

> test:ui
> playwright test --config playwright.config.ts --list

Listing tests:
  [desktop-1440] › e2e/colour-placement.e2e.spec.ts:107:3 › KPI identity hues stay on identity marks
  [desktop-1440] › e2e/colour-placement.e2e.spec.ts:107:3 › status hue stays on attention labels
  [desktop-1440] › e2e/contrast-hatch.e2e.spec.ts:66:1 › dark tokens meet DESIGN contrast floors
  [desktop-1440] › e2e/contrast-hatch.e2e.spec.ts:107:1 › unavailable hatch uses 45 degree 1 pixel 6 pixel stops
  [desktop-1440] › e2e/geometry.e2e.spec.ts:91:3 › shared header geometry matches DESIGN
  [desktop-1440] › e2e/geometry.e2e.spec.ts:91:3 › overview KPI grid is 4 plus 3
  [desktop-1440] › e2e/keyboard.e2e.spec.ts:80:1 › keyboard focus transitions and restoration match DESIGN
  [desktop-1440] › e2e/tables-a11y.e2e.spec.ts:41:3 › desktop tables contain overflow and keep ID sticky
  [desktop-1440] › e2e/tables-a11y.e2e.spec.ts:41:3 › routes pass axe and expose non-colour equivalents
  [desktop-1440] › feat-53.e2e.spec.ts:108:3 › component source uses only theme tokens
  [desktop-1440] › feat-53.e2e.spec.ts:108:3 › dense hierarchy and qualitative states match DESIGN
  [desktop-1440] › feat-53.e2e.spec.ts:108:3 › rendered routes and interactions match approved prototype
  [desktop-1920] › e2e/colour-placement.e2e.spec.ts:107:3 › KPI identity hues stay on identity marks
  [desktop-1920] › e2e/colour-placement.e2e.spec.ts:107:3 › status hue stays on attention labels
  [desktop-1920] › e2e/contrast-hatch.e2e.spec.ts:66:1 › dark tokens meet DESIGN contrast floors
  [desktop-1920] › e2e/contrast-hatch.e2e.spec.ts:107:1 › unavailable hatch uses 45 degree 1 pixel 6 pixel stops
  [desktop-1920] › e2e/geometry.e2e.spec.ts:91:3 › shared header geometry matches DESIGN
  [desktop-1920] › e2e/geometry.e2e.spec.ts:91:3 › overview KPI grid is 4 plus 3
  [desktop-1920] › e2e/keyboard.e2e.spec.ts:80:1 › keyboard focus transitions and restoration match DESIGN
  [desktop-1920] › e2e/tables-a11y.e2e.spec.ts:41:3 › desktop tables contain overflow and keep ID sticky
  [desktop-1920] › e2e/tables-a11y.e2e.spec.ts:41:3 › routes pass axe and expose non-colour equivalents
  [desktop-1920] › feat-53.e2e.spec.ts:108:3 › component source uses only theme tokens
  [desktop-1920] › feat-53.e2e.spec.ts:108:3 › dense hierarchy and qualitative states match DESIGN
  [desktop-1920] › feat-53.e2e.spec.ts:108:3 › rendered routes and interactions match approved prototype
Total: 23 tests in 6 files

exit status: 0
counts: exactly 23 browser tests listed in 6 files
```
