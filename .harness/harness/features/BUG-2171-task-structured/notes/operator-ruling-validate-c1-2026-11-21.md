# Operator ruling — BUG-2171 validate c1 must-fix — 2026-11-21

Run `2026-11-21-04-validate-validator` returned FAIL with all four SCs met at review_sha
`d3792019` and one must-fix: T-01's verify recipe hard-codes the smoke run id
`2026-11-08-02-smoke-product`, so a fresh rerun of the live smoke is refused at `run-start`
because that run is closed.

The operator chose **overrule** (reply "1" to the offered options: overrule vs amend-and-revalidate).

- The signed T-01 intent makes the live smoke single-use by design: "The smoke run id must be
  unused … refuse rather than overwrite an existing smoke run." The refusal QA observed is that
  design working, not a product defect.
- SC-03 is met on the saved receipts — actual child and lead `yield` calls, hook-injected strict
  schemas, preserved human-only prefix, hook-owned append — verified by QA, code, goal-check and
  the validator lead at the pin (`notes/receipts/live-smoke*.txt`, `runs/2026-11-08-02-smoke-product/`).
- No production, config or test change follows from this finding; the pin stands.
- Rework: no further round is spent.
