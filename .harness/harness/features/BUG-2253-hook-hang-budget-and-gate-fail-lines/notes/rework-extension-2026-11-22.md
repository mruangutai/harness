# Scope reduction — 2026-11-22 (operator)

Validate cycle 4 passed. The operator then asked what drove host load ~125, the cause behind #2253's 3s timeouts.

**Finding (filed as #2283).** On a 12-core host, these full pooled suites (8 workers each) ran at once:
- BUG-2187's validate c2 QA, full integration;
- FEAT-2225's concurrent validate c5 QA, full unit then full integration;
- FEAT-2225's #919 gate re-running the whole suite on QA's PASS.

**Ruling.** Keep the gate change and the `HOOK_HANG_BUDGET_S = 30` constant. Remove every SC-02 behavioral regression: the site observations, blocked-process probes, watchdog and containment cases. SC-02 is now verified by inspection.

Amendments:
- T-01 `intent` (amendment judgement ledgered);
- BRIEF SC-02, the maintainer perspective line, and SC-01's evidence (now `integration, unit`).
