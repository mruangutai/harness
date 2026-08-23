# STATE

## Current

- feature: FEAT-35-orchestrator-stop-and-wake
- run: none — revision closed PASS, digest at runs/2026-08-23-02-product/digest.md
- squad: none
- status: awaiting-user

<!-- phase: plan, at its exit gate. The operator's one consolidated revision (DEC-176) is applied
     and verified at source. BRIEF.md and plan.yaml both status: pending, unsigned. cycles_used 1
     (the revision was rework on already-produced artifacts). Next act is the operator's
     signature, then the orchestrator commits once. -->

## Open Questions

- SIGNATURE. Both artifacts read pending. All five revision items verified at source by the
  orchestrator, and check-plan-routes.py re-run independently: 5 OK rows, no DEVIATION,
  0 violations across 1 plan.
- Q1, non-blocking, for a ticket AFTER signing. D-08 rules run-unit-tests.sh is not enforcement
  layer on am.4's CATEGORY while conceding it IS a step of the required integration CI job. If
  "reached by a required check" were sufficient, that script has been an unlisted gate since before
  FEAT-35 — a pre-existing DEC-174 enumeration gap this feature neither created nor can legally
  close. Raised by the product lead; the orchestrator confirmed the CI wiring at
  .github/workflows/tests.yml:81 and :87.
- The fabricated-completion incident and the leads' identical wait pattern remain OUT by operator
  ruling. The main session owns filing the first; #610 and #552 track the second, recorded in the
  plan as D-09, a known cost of the boundary.
