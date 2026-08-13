# Handoff — validate seam — FEAT-18-board-truth

## Working set

- `.claude/skills/harness/bin/check-state.sh` — INV-26, and the E-01 fix at `_derived is None`.
- `.claude/skills/harness/bin/test-check-state.py` — `_inv26_fixture`, cases v.1–v.10.
- `.claude/skills/harness/bin/gh_board.py` — `derive_station`, `read_station`, `set_station`.
- `.harness/features/FEAT-18-board-truth/BRIEF.md` — SC-01 amended, SC-08 struck.
- `.harness/features/FEAT-18-board-truth/notes/mutation-record-T-02-T-04.md`.

## Next

Nothing here. Shipped: PR #334, squashed as `3e23907`, `review_sha` `af204ed`, eight live criteria
all met, 2 cycles of 10, 8 runs of 20. Leaving this feature:

1. Issue #250 — integration `detect` names 4 of the runner's 12 scripts and the unit glob matches
   all 12. This feature's qa gate read that layer.
2. Issue #247 — INV-27, the citation invariant. Grilling at
   `.harness/notes/grilling-prose-truth-2026-08-13.md`.

## Trust

- The suite for all six tasks: unit 0, integration 0, `check-state.sh` 0, `check-plan-routes.py` 0
  violations, re-run at `af204ed`.
- **Case v.8 only, for the E-01 fix.** Proven able to redden — against the reverted file it FAILS,
  old code printed to show the revert applied. v.9 and v.10 guard over-reporting and pass either
  way, so they are not evidence for this defect.
- **Not "6 of 6" or "5 of 5" for T-02/T-04** — no artifact substantiates them, both ran
  main-session-direct which writes no receipt. See `notes/mutation-record-T-02-T-04.md`.
- **Not any claim this feature observed GitHub.** Every automated criterion asserts against a fake
  `gh` (`functional` has `cmd: null`, DEC-187). The live board closed zero criteria.
- **SC-08 is struck: EIGHT live criteria, never nine.** The main session briefed "nine"; pm
  confirmed eight at source.
- **SC-01 was amended at re-signature, not weakened.** Its "closing the task lands its card in
  `Done`" half was unprovable by its own signature — D-03/T-03 forbid the harness writing a `Done`
  station, so no field-set call exists to capture. GitHub's `Item closed` moves it. Behavior
  unchanged.

## Dead ends

- **A green INV-26 suite did not mean INV-26 worked.** Every fixture was single-task; the defect
  needs two. `derive_station({done, pending})` is `None`, and the old code skipped the whole feature
  on `None` — including the per-task comparison, which never needed the derivation.
- **Concurrent panel and goal-check.** The operator overruled it so panel findings reach the
  goal-check.
- **Re-running qa at an unchanged pin.** Skipped, not deleted, reason on disk.
- **`/clear` kills an orchestrator and it is not resumable.** Respawn from disk state and run
  `check-state.sh` first — the killed agent left a digest missing its `artifact:` key.
- **INV-26's first live finding was not a defect.** A minute after the squash it reported
  `parent #326: plan derives Review — the board reads Done`, because the merge closed the issue and
  GitHub moved the card while `feature.json` still read `Review`. That is the feature working.
