# T-08 receipt — split-spec discovery

PASS — Playwright discovery now includes the root `feat-53.e2e.spec.ts` and `e2e/*.e2e.spec.ts`; the config diff changes only `testMatch`.

## Verification command

```sh
sh -c '
out=$(HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t08-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list feat-53.e2e.spec.ts e2e/geometry.e2e.spec.ts) &&
printf "%s\n" "$out" &&
test "$(printf "%s\n" "$out" | sed -n "s/^Total: \([0-9][0-9]*\) tests.*/\1/p")" = 9 &&
test "$(printf "%s\n" "$out" | grep -F -c "shared header geometry matches DESIGN")" = 2 &&
test "$(printf "%s\n" "$out" | grep -F -c "overview KPI grid is 4 plus 3")" = 2 &&
test "$(printf "%s\n" "$out" | grep -F -c "component source uses only theme tokens")" = 1 &&
test "$(printf "%s\n" "$out" | grep -F -c "dense hierarchy and qualitative states match DESIGN")" = 2 &&
test "$(printf "%s\n" "$out" | grep -F -c "rendered routes and interactions match approved prototype")" = 2
'
```

## Result

```text
> test:ui
> playwright test --config playwright.config.ts --list feat-53.e2e.spec.ts e2e/geometry.e2e.spec.ts

Listing tests:
  [desktop-1440] › e2e/geometry.e2e.spec.ts:106:3 › shared header geometry matches DESIGN
  [desktop-1440] › e2e/geometry.e2e.spec.ts:106:3 › overview KPI grid is 4 plus 3
  [desktop-1440] › feat-53.e2e.spec.ts:129:3 › component source uses only theme tokens
  [desktop-1440] › feat-53.e2e.spec.ts:129:3 › dense hierarchy and qualitative states match DESIGN
  [desktop-1440] › feat-53.e2e.spec.ts:129:3 › rendered routes and interactions match approved prototype
  [desktop-1920] › e2e/geometry.e2e.spec.ts:106:3 › shared header geometry matches DESIGN
  [desktop-1920] › e2e/geometry.e2e.spec.ts:106:3 › overview KPI grid is 4 plus 3
  [desktop-1920] › feat-53.e2e.spec.ts:129:3 › dense hierarchy and qualitative states match DESIGN
  [desktop-1920] › feat-53.e2e.spec.ts:129:3 › rendered routes and interactions match approved prototype
Total: 9 tests in 2 files
```

Title counts: `shared header geometry matches DESIGN` 2; `overview KPI grid is 4 plus 3` 2; `component source uses only theme tokens` 1; `dense hierarchy and qualitative states match DESIGN` 2; `rendered routes and interactions match approved prototype` 2.

The config-only diff is `.claude/skills/harness/bin/dashboard/client/playwright.config.ts:7`, replacing the root-only match with `['feat-53.e2e.spec.ts', 'e2e/*.e2e.spec.ts']`.
