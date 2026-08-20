# STATE

## Current

- feature: FEAT-26-pr-linkage-recorded
- run: .harness/harness/features/FEAT-26-pr-linkage-recorded/runs/2026-08-18-1-product/state.yaml
- squad: product
- status: in-flight
- phase: plan — BRIEF and plan.yaml drafted, approval pending. Review segment next
  (simplify + architecture on eng, design contract on validator), then one consolidated
  revision to pm, then the operator's signature.
- source ticket: #492. Plan base pinned at ada8e99.

## Open Questions

- Q1 (BLOCKING, operator): confirm four PR numbers that measurement cannot derive —
  FEAT-01 -> 4, FEAT-02 -> 4, FEAT-03-subissue-mirror -> 15, FEAT-04-decisions-index -> 15.
  Attribution is by PR title, not by branch. T-06 writes exactly these.
- Q2 (non-blocking, operator): should the harness open its own PRs? Contradicts DEC-153,
  so it is not the plan's to choose. The plan is correct under either answer.
- Q3 (non-blocking, operator): should `ship` close the source issues directly instead of
  rendering `Closes` lines? Crosses DEC-196. D-04 takes the render-only branch.
- Q4 (non-blocking, harness defect): feature-id coinage collided twice while this ran and
  nothing detected it. An orphan `FEAT-25-expertise-repository-tier/` sits on disk.
- Q5 (non-blocking, correction): the dispatch premise "check-state.sh carries 19
  invariants, the new one is the twentieth" is FALSE at ada8e99 — they run INV-1..INV-27,
  INV-20 is taken, INV-10 is retired and unreusable. pm used INV-28 correctly. Sibling
  orchestrators may carry the same false premise.
