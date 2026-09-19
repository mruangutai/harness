# T-08 receipt

## RED

```text
$ HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t08-red npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- e2e/geometry.e2e.spec.ts

> test:ui
> playwright test --config playwright.config.ts e2e/geometry.e2e.spec.ts

Error: No tests found.
Make sure that arguments are regular expressions matching test files.
You may need to escape symbols like "$" or "*".
```

The unchanged Playwright configuration has `testMatch: 'feat-53.e2e.spec.ts'`, excluding the task-mandated `e2e/geometry.e2e.spec.ts` before its tests can execute.

## Required verify

```text
$ sh -c '<exact T-08 verify command>'

> test:ui
> playwright test --config playwright.config.ts --list feat-53.e2e.spec.ts e2e/geometry.e2e.spec.ts

Listing tests:
  [desktop-1440] › feat-53.e2e.spec.ts:129:3 › component source uses only theme tokens
  [desktop-1440] › feat-53.e2e.spec.ts:129:3 › dense hierarchy and qualitative states match DESIGN
  [desktop-1440] › feat-53.e2e.spec.ts:129:3 › rendered routes and interactions match approved prototype
  [desktop-1920] › feat-53.e2e.spec.ts:129:3 › dense hierarchy and qualitative states match DESIGN
  [desktop-1920] › feat-53.e2e.spec.ts:129:3 › rendered routes and interactions match approved prototype
Total: 5 tests in 1 file
```

The command exits 1 because the two geometry titles are not discoverable, so its `Total: 9` assertion fails. The legacy spec now owns only SRC-TOKENS, VIS-DENSITY, and VIS-PROTOTYPE; `e2e/geometry.e2e.spec.ts` owns the C1 and KPI checks with named steps, soft assertions, and finally-captured WebP evidence. FEAT-53 production remains unchanged.
