# Build segments — BUG-1305 — main-session-direct, every one

## BLUF

**No squad may build any part of this feature.** All eight live tasks carry
`execution_mode: main-session-direct` in the signed plan, and `check-plan-routes.py` at `75cdd200`
confirms it task by task — six `DEVIATION` lines (a granted surface deliberately routed to the main
session, the expected DEC-174 shape) and two `OK` lines (ungranted surfaces that have no other lane).
`0 violation(s)`. The eng segment of the build phase therefore does not exist for this feature, and
dispatching one would make a squad edit the enforcement layer, which DEC-174 forbids.

The orchestrator's build-phase segments that follow the eng segment — qa's `test_matrix` gate,
SIMPLIFY, the `review_sha` pin, the validation panel, pm's goal-check — all grade code. None can run
before these segments land.

## Segments, in dependency order

Each task's `verify:` is reproduced verbatim in `plan.yaml`; run it from the worktree root
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1305-run-state-clobber`.
The `intent:` block in `plan.yaml` is the complete specification for each — files, logic, values,
fail-open rows and red-proof cases. Nothing here restates it.

- **S1 — T-01, T-05, T-11.** No dependencies. T-01 (`run_identity.py` plus its unit test) is the
  riskiest and everything in Mode A waits on it, so the two tasks that do not depend on it sit in
  the same segment: a failure in T-01 wastes neither.
- **S2 — T-02, T-03.** Both depend on T-01. T-02 is the largest surface (four gate scripts, four
  test files) and carries the witness registration; T-03 is the detection invariant.
- **S3 — T-09.** Depends on T-02. The identity refusal itself, plus the `harness-team` seed-field
  documentation.
- **S4 — T-06.** Depends on T-02 and T-09. Same file as both (`check-domain.sh`), so it is serialised
  behind them by construction, not by preference.
- **S5 — T-08.** Depends on every code task. Produces the regression delta SC-07 is graded on and
  re-runs all six suites.

## Test-first is not optional here

Every automated criterion in `BRIEF.md` requires its test demonstrated failing on the pre-change
tree, and `notes/redproof-BUG-1305.md` is where each task records that proof — several `verify:`
blocks grep for its section headings, so a task whose red proof was never written fails its own
verify. `T-09` additionally pins `baseline_sha:` in that file.

## What the orchestrator does when these land

Report back with the tasks' stations recorded and the commits made. The remaining build-phase
segments are then dispatchable in order: qa's `test_matrix` gate (`gates.qa_gate: blocking`, the
project's only blocking gate), SIMPLIFY through eng-lead, then the `review_sha` pin and
`gh-sync.py status <feature-dir> review` together, then the validation panel, then pm's goal-check
against SC-01..SC-13.

## Budget

`cycles_used` is 9 of 9. A first-pass run of any of the segments above costs no cycle. The first
send-back from any reader exhausts the budget, so it stops and escalates to the operator for an
Advisor ruling before the rework, per the resume instruction.
