# FEAT-1821 integrated list receipt

Configured UI discovery passed: exit 0, 23 tests, and zero reporter-probe executions.

## Command

```sh
HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=split-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list
```

## Output

```text
> test:ui
> playwright test --config playwright.config.ts --list

Listing tests:
  [desktop-1440] › e2e/colour-placement.e2e.spec.ts:122:3 › KPI identity hues stay on identity marks
  [desktop-1440] › e2e/colour-placement.e2e.spec.ts:122:3 › status hue stays on attention labels
  [desktop-1440] › e2e/contrast-hatch.e2e.spec.ts:81:1 › dark tokens meet DESIGN contrast floors
  [desktop-1440] › e2e/contrast-hatch.e2e.spec.ts:123:1 › unavailable hatch uses 45 degree 1 pixel 6 pixel stops
  [desktop-1440] › e2e/geometry.e2e.spec.ts:106:3 › shared header geometry matches DESIGN
  [desktop-1440] › e2e/geometry.e2e.spec.ts:106:3 › overview KPI grid is 4 plus 3
  [desktop-1440] › e2e/keyboard.e2e.spec.ts:74:1 › keyboard focus transitions and restoration match DESIGN
  [desktop-1440] › e2e/tables-a11y.e2e.spec.ts:51:3 › desktop tables contain overflow and keep ID sticky
  [desktop-1440] › e2e/tables-a11y.e2e.spec.ts:51:3 › routes pass axe and expose non-colour equivalents
  [desktop-1440] › feat-53.e2e.spec.ts:129:3 › component source uses only theme tokens
  [desktop-1440] › feat-53.e2e.spec.ts:129:3 › dense hierarchy and qualitative states match DESIGN
  [desktop-1440] › feat-53.e2e.spec.ts:129:3 › rendered routes and interactions match approved prototype
  [desktop-1920] › e2e/colour-placement.e2e.spec.ts:122:3 › KPI identity hues stay on identity marks
  [desktop-1920] › e2e/colour-placement.e2e.spec.ts:122:3 › status hue stays on attention labels
  [desktop-1920] › e2e/contrast-hatch.e2e.spec.ts:81:1 › dark tokens meet DESIGN contrast floors
  [desktop-1920] › e2e/contrast-hatch.e2e.spec.ts:123:1 › unavailable hatch uses 45 degree 1 pixel 6 pixel stops
  [desktop-1920] › e2e/geometry.e2e.spec.ts:106:3 › shared header geometry matches DESIGN
  [desktop-1920] › e2e/geometry.e2e.spec.ts:106:3 › overview KPI grid is 4 plus 3
  [desktop-1920] › e2e/keyboard.e2e.spec.ts:74:1 › keyboard focus transitions and restoration match DESIGN
  [desktop-1920] › e2e/tables-a11y.e2e.spec.ts:51:3 › desktop tables contain overflow and keep ID sticky
  [desktop-1920] › e2e/tables-a11y.e2e.spec.ts:51:3 › routes pass axe and expose non-colour equivalents
  [desktop-1920] › feat-53.e2e.spec.ts:129:3 › dense hierarchy and qualitative states match DESIGN
  [desktop-1920] › feat-53.e2e.spec.ts:129:3 › rendered routes and interactions match approved prototype
Total: 23 tests in 6 files
```

## Execution counts

| Listed spec(s) | Executions |
| --- | ---: |
| `feat-53.e2e.spec.ts` + `e2e/geometry.e2e.spec.ts` | 9 |
| `e2e/colour-placement.e2e.spec.ts` | 4 |
| `e2e/keyboard.e2e.spec.ts` | 2 |
| `e2e/contrast-hatch.e2e.spec.ts` | 4 |
| `e2e/tables-a11y.e2e.spec.ts` | 4 |
| Reporter probes (`ui-reporter.probe.spec.ts` or any reporter probe) | 0 |
