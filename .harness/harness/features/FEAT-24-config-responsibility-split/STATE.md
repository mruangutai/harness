# STATE

## Current

- feature: FEAT-24-config-responsibility-split
- run: .harness/harness/features/FEAT-24-config-responsibility-split/runs/2026-08-18-6-eng/
- squad: eng
- status: in-progress

Phase: **ship, building. The cutover is crossed and the write lock is open.** I confirmed it from my
own side with a probe write, and `load_fleet` returns cleanly with kaya's entry at exactly
`name` + `default_branch` — **SC-01 is met.**

Landed and committed: **T-01** `000934b`, **T-08** `22814c7`, **T-09** kaya PR #335 merged `692672d`,
**T-02** `962417a` (verify GREEN, 78/78, re-run by me), **T-07 Part A item 1** `d177bab` (the
operator's eight-line `fleet.yaml` deletion). All three bookkeeping debts the lock made unwritable
are discharged.

**In flight — run 6-eng, four steps:** T-02's mutation proofs (the half the lock prevented: its
assertions are proven able to fail on a missing symbol, never on a wrong implementation), then T-03,
T-06, T-04.

**Two scope corrections found by measuring the red set myself — seven suites, not five.**
1. `test-factory-workspace.py` is a fleet fixture in **no task's `files:` list anywhere in the plan**.
   T-03's title is universal ("every fleet fixture outside `factory_config`"), so I extended T-03's
   dispatch to six files as an execution-time call and said so in the dispatch. Mine, and recorded.
2. `test-no-distribution.py`'s `every_repo_declares_its_own_board` and `kaya_ai_is_paired_with_board_2`
   are assertions this design **deliberately falsifies**, in a file T-07 owns and never mentions
   them. That is the operator's, not the squad's. Q1 below.

**Next after run 6:** T-05 to the operator (DEC-174 carve-out, lands in the SAME commit as T-04),
then T-07's remainder, then T-10, then the qa `test_matrix` segment, simplify, pin `review_sha`, the
review panel, pm's goal-check.

Cycles: 1 of 10. Runs: 8 recorded of 20, plus this one.

## Open Questions

- Q1 (operator, BLOCKING before T-07 completes): `test-no-distribution.py`'s
  `every_repo_declares_its_own_board` and `kaya_ai_is_paired_with_board_2` assert a board in the
  fleet entry, which SC-01 now forbids. T-07's Part B adds one case and names two others as
  untouchable; these two are neither. Delete, invert, or repoint at kaya's remote config?
- Q2 (settled, recorded): the orphaned `ready:`/`Done:` rationale comments left in `fleet.yaml` are
  **already in T-07 Part A item 5's scope** — it requires one line pointing a reader at kaya's own
  config, where those rationales now live as `_board_*_note` keys. Not a residual, not SC-11.
- Q3 (harness defect, backlog B-12): `factory_land.py` does not commit — T-09 failed with
  `No commits between master and factory/issue-334` until the operator committed by hand.
- Q4 (harness defect, filed as #461, backlog row only): a lead returned a verdict while its member
  was in flight — eighth recorded instance. Do not re-file.
- Q5 (harness defect, backlog B-4): `feature.json`'s schema declares no `phase` property under
  `additionalProperties: false`, so the playbook's "record your phase there" is unsatisfiable.
- Q6 (harness defect, backlog B-11): `gh-sync.py` has no un-start subcommand.
- Q7 (main session): four paused feature dirs carry six of `check-state.sh`'s seven violations.

Briefing: `notes/ship-review-2026-08-18-ship-01.md` (rendered `.html` beside it).
