# T-03 receipt

The configured FEAT-53 Playwright lane lists its complete applicable contract and successfully serves the committed dashboard bundle for a scoped browser execution.

- Fail-first: `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=plan-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list` exited 1 before edits: `Missing script: "test:ui"`.
- TDD red: `npx playwright test feat-53.e2e.spec.ts` exited 1 before dependencies with `Cannot find package '@playwright/test'`.
- Post-edit signed verify: the same signed command exited 0 and listed 23 executions: all twelve exact titles under `desktop-1440`, the other eleven under `desktop-1920`, with `SRC-TOKENS` only under `desktop-1440`.
- Scoped runtime: `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=t03-runtime npm run test:ui -- --project=desktop-1440 --grep 'shared header geometry matches DESIGN'` exited 0. It started `serve.py` at `127.0.0.1:8972`, served the committed dist assets, captured WebP via CDP, and passed the named desktop-1440 check.
- The generated fixture is prepared before webServer startup and Playwright now writes worker artifacts to `test-results/playwright-artifacts`, leaving the fixture root intact.
- Dependencies are exact-pinned in the lockfile: `@playwright/test@1.63.0`, `@axe-core/playwright@4.13.0`, and the Playwright browser revision; no image dependency was added.

Touched client files: `package.json`, `package-lock.json`, `playwright.config.ts`, `ui-manifest.ts`, `ui-reporter.ts`, `fixture.ts`, and `feat-53.e2e.spec.ts`. No FEAT-53 production source changed.
