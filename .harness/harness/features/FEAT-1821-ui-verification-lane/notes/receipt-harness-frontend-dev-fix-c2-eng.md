# T-03 repair receipt

The runner now prepares a run-scoped, clean fixture tree and captures each inspection label despite unchanged FEAT-53 product failures; the signed product contract remains RED.

## Fail-first evidence

`npx playwright test --config playwright.config.ts --grep 'fixture preparation is clean'` initially exited 1: `prepareFixtureSync('red-fixture-proof')` returned the shared `fixture-project-a` path rather than a run-scoped root. The pre-repair focused header runtime also remains product RED: `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=header-red npm run test:ui -- --grep 'shared header geometry matches DESIGN'` exited 1 in both projects because `header` was absent.

## Scoped verification

- `npx playwright test --config playwright.config.ts --grep 'fixture preparation is clean'` passed after the fixture change (one desktop-1440 pass; desktop-1920 skip).
- Concurrent focused preparation: `HARNESS_UI_RUN_ID=fixture-race-a npm run test:ui -- --list >/tmp/fixture-race-a.log 2>&1 & HARNESS_UI_RUN_ID=fixture-race-b npm run test:ui -- --list >/tmp/fixture-race-b.log 2>&1 & wait ...` exited 0 and confirmed both distinct roots with no `fixture-states.json` sidecar.
- `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=inspection-red-complete npm run test:ui -- --grep 'dense hierarchy|rendered routes'` exited 1 only on unchanged product body/header failures, while emitting every named VIS-DENSITY and VIS-PROTOTYPE WebP attachment for both projects; capture continues after every setup failure.
- Signed command: `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=plan-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list` exited 0 with 12 titles and 23 executions; SRC-TOKENS appeared only for desktop-1440.

## Remaining failure

T03-F1 and T03-F2 are not complete: objective assertions remain partial and C3 coverage is not a fully clause-by-clause implementation. T03-F4 has stronger exact attachment validation but no retained behavioral negative-probe matrix for every requested class. The expected FEAT-53 product failures are separately RED and were not weakened.
