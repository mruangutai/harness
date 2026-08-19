# STATE

## Current

- feature: FEAT-27-expertise-repository-tier
- run: .harness/harness/features/FEAT-27-expertise-repository-tier/runs/plan-product/state.yaml
- squad: product
- status: in-flight

Unit 6 of effort #336 (ticket #494), mission plan. The product squad drafted BRIEF and plan under
the number FEAT-25, which a peer flow claimed first; the artifacts are being re-homed here under
FEAT-27. Number 26 is held by another live flow.

## Open Questions

- `harness.json`'s `integration.detect` glob does not list `test-check-domain.py` or
  `test-check-expertise.py`, though the runner executes both. `harness.json` belongs to the live
  unit-5 flow this cycle, so the stale glob is raised, not fixed. Non-blocking.
