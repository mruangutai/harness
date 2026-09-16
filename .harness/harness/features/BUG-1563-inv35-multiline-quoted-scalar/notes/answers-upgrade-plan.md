# Operator answers — BUG-1563 plan upgrade

- recorded_at: 2026-09-15
- recorded_by: main session
- question: Authorize upgrading BUG-1563 from the signed two-file patch to a plan that adds the minimum matrix-required unit coverage, while preserving DEC-174 main-session-direct routing for enforcement-layer files?
- answer: Yes — upgrade to plan.
- scope: Add only the minimum unit-kind coverage required by the configured hard test matrix.
- constraints:
  - Preserve DEC-174 main-session-direct routing for enforcement-layer files and their own tests.
  - Do not waive or weaken the hard test matrix.
  - Resume the Harness ship flow after the amended scope is approved and executed.
