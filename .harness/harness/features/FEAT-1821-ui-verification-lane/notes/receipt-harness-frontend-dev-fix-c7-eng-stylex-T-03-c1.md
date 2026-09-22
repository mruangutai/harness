# T-03 cycle-1 receipt — component-count reconciliation

## Result

**FAIL — the correctly repaired dependency graph makes the configured component suite pass 27/27, not the operator-required 23/23.** The signed browser listing is exactly 23 tests. The two counts exercise different suites; no legitimate correction confined to the StyleX manifest/lock declaration can remove four declared Vitest cases without filtering, deleting, or altering specs/configuration, all prohibited by this assignment.

- Branch: `feat/FEAT-1821-ui-verification-lane`
- Cycle: `fix-c7-eng-stylex`, cycle 1
- Retained pins: `@stylexjs/stylex` exactly `0.19.1` (`client/package.json:14`, lock `node_modules/@stylexjs/stylex:667-670`) and `@testing-library/dom` exactly `10.4.1` (`client/package.json:25`, lock:22).
- The authorized package diff remains only `client/package.json` and `client/package-lock.json` (one manifest insertion; lock 46 insertions and one required metadata removal). No unrelated package/lock churn or transient runner output was introduced.

## Hypothesis and read-only result

Hypothesis: a dependency-resolution defect caused Vitest to collect four extra tests, so correcting only the StyleX dependency declaration would change the configured suite to 23.

Falsifier: after the exact StyleX peer pin loads successfully, the five existing component specs still declare and execute a structural total other than 23.

The hypothesis is falsified. The suite's 27 cases are declared by five pre-existing source specs:

| Spec | Declared/executed cases | Accounting |
| --- | ---: | --- |
| `src/gapstates.test.tsx` | 1 | unavailable versus measured zero |
| `src/kpi-content.test.tsx` | 3 | KPI links/zero, unattributed KPI 6, unavailable throughput |
| `src/panels.test.tsx` | 4 | Shape A, two Shape B charts, unattributed KPI 6 panel |
| `src/work-view.test.tsx` | 6 | statuses/layouts, source errors, filters, inline/detail route, retry, settled paths |
| `src/routes.test.tsx` | 13 | `it.each` 3 product routes; settled paths; `it.each` 5 retired routes; 4 URL/failure/focus behaviors |
| **Total** | **27** | **5 files** |

`src/routes.test.tsx:49-61` has three parameterized route cases and `:67-72` has five retired-route cases; these are independently collected test cases, so its four declarations expand to 13. Package dependency resolution affects whether these declarations load, not their suite cardinality. The repaired graph now loads all five, and the focused runner proves all 27 pass.

## Focused evidence

```text
$ npm --prefix .claude/skills/harness/bin/dashboard/client run test

> test
> vitest run
 RUN  v5.0.1 /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.claude/skills/harness/bin/dashboard/client

 Test Files  5 passed (5)
      Tests  27 passed (27)
   Duration  2.53s
```

The command exited 0. It emitted existing jsdom `scrollTo` notices; no test failed.

```text
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
```

The signed verify command exited 0.

## Scope/acceptance conflict

T-03's desired component count is exactly 23, while its configured component command is `vitest run` and its existing, unfiltered component specs structurally collect 27 cases. The signed browser command is separately correct at exactly 23. Reaching 23 for Vitest would require forbidden source/spec/config or script/filter changes. Keep the exact StyleX repair; resolve the acceptance only by changing the operator requirement or expanding authorized scope.
