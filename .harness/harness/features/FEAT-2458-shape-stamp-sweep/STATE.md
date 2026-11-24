# STATE

## Current

- feature: FEAT-2458-shape-stamp-sweep
- run: .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-24-01-validate-validator/state.yaml
- squad: none
- status: awaiting-user

## Open Questions

- Main session (DEC-174 lane) owes the round-1 fix for MF-2 then MF-1 from runs/2026-11-24-01-validate-validator/digest.md; validate re-runs over the new tip after it lands.
- OQ-1: re-point SC-07's evidence at `--canonical-reader-audit`, or move the T-07 case into CASES? Non-blocking; operator.
- OQ-2: tighten SC-01's `absent` substring marker to a phrase? Rewords signed SC-01/D-01. Non-blocking; operator.
- OQ-3: amend T-01 intent (d) so an unreadable fleet tree is told apart from a missing one? Non-blocking; operator.
- OQ-4: harness defect — `test-check-plan-routes.py --canonical-reader-self-test` carries 2 FAILs at 322b12b0 and at the pin, and no runner invokes it.
