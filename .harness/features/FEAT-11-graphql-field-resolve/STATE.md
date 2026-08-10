# STATE

## Current

- feature: FEAT-11-graphql-field-resolve
- run: .harness/features/FEAT-11-graphql-field-resolve/runs/plan-fix-product/state.yaml
- squad: none
- status: awaiting-user

Mission plan is COMPLETE and the phase ends here. BRIEF.md, plan.yaml and DESIGN.md are written,
reviewed by five personas across four runs, and both approval fields are `pending` — the signature
is the operator's alone. One task, 12 SCs, 5 REQs, 4 decisions, zero main-session-direct steps.
8 of 10 cycles spent. Handoff at `notes/handoff-plan.md`. Nothing is committed: the artifacts are
unsigned and approval-gated. Next action is the operator's signature, then the build phase.

## Open Questions

- Q1 (for the signer): SC-01 is the live cost proof and it writes to board 6, so it is operator-run
  by construction and reads `not_met` at end of build. The cleanup half of this is now ANSWERED by
  the operator's own ruling at 687fd3e — board 6 is a retained FIXTURE, not cleanup debt. That
  creates a new tension nobody in this flow could have seen: SC-01 runs a real `factory_decompose`,
  which MOVES items between stations, mutating the "four items in known states" the ruling preserves.
  Scheduling SC-01 means deciding whether those states are restored after, or are expendable.
- Q2 (for the signer): the grilling artifact's premise that `_validate_stations` and the `Redy` case
  depend on `factory_gh.py:251-262` is FALSE — I verified it at 835b297. The constraint stands; only
  the reason was wrong, and the plan text is corrected. Ruling in `feature.yaml` `e1_ruling`.
- Q3 (for the signer): FEAT-12 edits `run-unit-tests.sh`, the command T-01's verify invokes. No file
  collides, but landing order changes what T-01's verify means.
- Q4 (for the signer): T-01's verify pins three sha256 content hashes. Any unrelated edit to
  `test-factory-{decompose,claim,land}.py` between signature and build reddens it with correct
  delivery behind it. Verified still valid at 687fd3e. Remedy: refresh the hashes at build start,
  or have the build orchestrator recompute and route an amendment to pm.
- Q5 (my error, cheap to strike): `DESIGN.md:59` and `:119` carry `<!-- ok-stale -->` markers. My
  dispatch instructions cited that mechanism; the operator STRUCK it at 835b297, removing 66 such
  markers. Both are inert — no checker reads them — but they re-introduce what was just removed.
- Q6 (harness defect, not this feature): `harness-pm` has no `notes/receipt-*.md` grant in
  team-config.yaml while `harness-handoff` instructs every agent to file a receipt. check-domain.sh
  blocked the write; pm used `notes/research-*.md` instead of working around the hook.
- Q7 (residuals the validator recorded, not acted on): the bugfix test-matrix binds only `unit` so
  SC-09's integration evidence rests on T-01's task-local verify; and two envelope shapes
  (`{"data": null}`, a field dict missing `options`/`id`) are unmeasured and unfixtured.
