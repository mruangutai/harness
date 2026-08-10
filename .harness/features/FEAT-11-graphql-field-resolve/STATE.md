# STATE

## Current

- feature: FEAT-11-graphql-field-resolve
- run: none yet this mission
- squad: none
- status: in-progress

Mission SHIP, phase BUILD (transitioned from phase plan at 8dedeae, on the operator's signature).
Both approvals read `approved` / `operator` / 2026-08-10, so the step-0 gate passes and the
plan-phase handoff's `## Next` is validated: mirror, then T-01 to eng-lead, then the qa segment.
Two inherited claims were re-measured before any dispatch rather than trusted: the three sha256
sentinels recompute byte-identical (Q4 is moot, no amendment owed), and the working tree is clean
over `run-unit-tests.sh` and all four DEC-174 carve-out files (Q3's FEAT-12 hazard has not arrived
here). Baseline suites are green and the verify's discriminating clauses are red, as designed.
8 of 12 cycles spent, all of them in the plan phase.

## Open Questions

- Q1 (SC-01): ANSWERED by the operator's signature ruling — board 6 is a retained fixture, its item
  station values are recorded before the proof and restored after. Carried into the UAT script.
- Q2 (the falsified grilling rationale): CLOSED — ruling stands in `feature.yaml` `e1_ruling`.
- Q3 (FEAT-12 / `run-unit-tests.sh`): measured clean at 8dedeae. Re-check before the final commit.
- Q4 (sha256 sentinels): CLOSED — recomputed byte-identical at 8dedeae.
- Q5 (`DESIGN.md:59`, `:119` inert `<!-- ok-stale -->` markers): the orchestrator may resolve this
  without asking, per the ship dispatch. Swept as a product-squad segment in this phase.
- Q6 (harness defect: `harness-pm` has no `notes/receipt-*.md` grant in team-config.yaml): still
  open, not this feature's to fix. Rides the briefing's backlog.
- Q7 (validator residuals): the bugfix matrix binds only `unit`, so the qa segment is told
  explicitly that `integration` is the required bug-class kind, citing SC-09. The two unmeasured
  envelope shapes are named in T-01's fixture list.
