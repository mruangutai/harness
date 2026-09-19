# Observations — harness-frontend-dev — FEAT-1821-ui-verification-lane

- 2026-09-17: Playwright list invokes config fixture preparation, so local test-results can exist even for --list and require a cleanup owner when domain guards deny removal.
- 2026-09-18: T-10 listing command discovered keyboard.e2e.spec.ts once per desktop project, with the exact C3-KEYBOARD title twice.
- 2026-09-18: A test-level finally cannot capture WebP after Playwright exhausts the whole-test timeout because the page has already closed; 10 of 23 smoke records remained without evidence.
- 2026-09-18: Playwright test.afterEach can capture a valid WebP for timeout-failed tests before page fixture disposal; in-test finally executes after the page closes.
- 2026-09-18: The dashboard Vitest suite structurally collects 27 cases from five source specs (including 3+5 parameterized route cases), independent of the 23-test Playwright listing; a peer dependency repair can restore loading but cannot legitimately reconcile those counts.
