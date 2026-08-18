# STATE

## Current

- feature: FEAT-24-config-responsibility-split
- run: .harness/harness/features/FEAT-24-config-responsibility-split/runs/2026-08-18-5-eng/
- squad: eng
- status: in-progress

Phase: **ship, building, executing ROUTE A of the cutover.** THIS FILE WAS WRITTEN BEFORE THE T-02
DISPATCH, DELIBERATELY. Once T-02's `factory_config.py` edit is on disk, no governed agent — me
included — can `Write` anything until the operator deletes the board block from
`.harness/factory/fleet.yaml`. Commits still work; `Write` does not (`bash-write-guard.sh:375`,
`:475`, `:551`). So this is my last writable moment for the window.

Done, verified and committed: **T-01** (`000934b`), **T-08** (`22814c7`), **T-09** (kaya PR #335,
merged `692672d` — I re-ran its verify against kaya's `master` myself: GREEN). D-10's outage window
is now **zero**: kaya declares its own board before anything removes the fleet copy.

**In flight: T-02**, dispatched to `harness-eng-lead` with the write-ordering constraint — tests and
receipt written first, `factory_config.py` as the member's FINAL write, then run the verify
read-only and return.

**What happens on its return, in this exact order.** I commit (allowed) and return immediately,
naming the SHA and the exact `fleet.yaml` lines to delete. I do NOT attempt to record the run, mark
T-02 `done`, or run `close-task` — every one of those is a `Write` and would fail. **Those three are
owed to my successor** once the operator has made the deletion:
`feature.json` gains the `2026-08-18-5-eng` run entry, `plan.yaml` T-02 goes to `done`, and
`gh-sync.py close-task T-02` runs after it. Then the continuation run for T-02's post-migration
mutation proofs, then T-03, T-06, T-04.

**If the member returned WITHOUT landing `factory_config.py`** there is no lockout and none of the
above applies — writes work normally and the run is recorded the ordinary way.

Cycles: 1 of 10. Runs: 7 recorded of 20, plus this one in flight.

## Open Questions

- Q1 (operator, on T-02's return): delete the `board:` block from `.harness/factory/fleet.yaml`'s
  `mruangutai/kaya-ai` entry — T-07 Part A item 1 only. The entry keeps `name` and `default_branch`.
  Nothing else in the file changes; Part A items 4 and 5 stay with T-07 proper.
- Q2 (carried into the T-04 dispatch): the plan-phase architecture review asked that T-04's
  rewritten `load_board` docstring state it raises `FleetError`. Nobody dispositioned it.
- Q3 (carried into the T-02 dispatch as a flag): `validate_board`'s `what` slot reads "fleet key
  invalid" at five raise sites; after T-02 neither surviving caller reads `fleet.yaml`.
- Q4 (harness defect, backlog B-4): `feature.json`'s schema declares no `phase` property under
  `additionalProperties: false`, so the playbook's "record your phase there" is unsatisfiable.
- Q5 (harness defect, backlog B-12): `factory_land.py` does not commit — T-09 failed with
  `No commits between master and factory/issue-334` until the operator committed by hand.
- Q6 (harness defect, backlog B-11): `gh-sync.py` has no un-start subcommand, so an abandoned
  dispatch leaves cards on `Building` and INV-26 reports it as drift.
- Q7 (main session): four paused feature dirs carry six of `check-state.sh`'s seven violations, and
  two of them both claim FEAT-25. Not FEAT-24's, and I have stayed off them.

Briefing for the operator: `notes/ship-review-2026-08-18-ship-01.md` (rendered `.html` beside it),
now carrying B-12.
