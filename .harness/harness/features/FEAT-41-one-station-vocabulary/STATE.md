# STATE

## Current

- feature: FEAT-41-one-station-vocabulary
- run: .harness/harness/features/FEAT-41-one-station-vocabulary/runs/2026-08-25-03-product/state.yaml
- squad: none
- status: blocked

## Open Questions

- Q1 BLOCKING: every harness-pm dispatch is refused on a live single-flight claim held by the decisions-triage pm (03:49:40Z). Operator must release it or tell me to wait. I will not clear it.
- Q2 BLOCKING: plan.yaml does not parse (line 83, D-09 because, colon-space in a plain scalar). Unsignable until pm can run.
- Q3: ruling 2 is on HOLD; T-12's recording form becomes a named open dependency. Not yet applied.
- Q4: F-1 (high) and F-2 (med) from the code-review pass are not yet applied.
- Q5: both-ends deadlock — dispatch-guard refuses the dispatch and validate-digest refuses the return, reading the same claim. Lead recommends a discriminator on claim age.
- Q6: T-04 vs T-06 disagree on the terminal-feature count; D-11's arithmetic rests on it.
