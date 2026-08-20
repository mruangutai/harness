# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: re-grade of SC-08 and SC-09 dispatched against the current pin
- squad: product
- status: Review — budget raised to 11 by operator ruling (DEC-157), spent on this re-grade

**The stale-pin history is a matter of record and I am not letting a correction overwrite it.**
`review_sha` read `4f2e5d0` at the moment pm graded — confirmed by
`git show 4881173:.../feature.json` and `git show 075fda0~1:.../feature.json`, both of which record
`4f2e5d0`. At that sha `git show 4f2e5d0:CLAUDE.md | grep -c "wait loop"` returns **0** and
`git merge-base --is-ancestor 9c9785f 4f2e5d0` reports NOT an ancestor. **pm's SC-09 verdict was
correct on the tree it was given.** The pin is current now only because re-pinning was the remedy;
reading the present pin backwards would invert cause and effect. DEC-89 being skipped on both halves
is precisely what made it stale, so the skip and the staleness are the same fact, not competing ones.

**SC-08 is a genuine failure and both prior verifications missed it, twice.** The previous `STATE.md`
carried a 506 figure with zero condition tokens while FEAT-29 reads `status: Building` and is still in
force. Remedied: every cost figure below carries board, item count and commit.

**Operator ruling, recorded so the next grader need not guess:** SC-08's *no such document* binds to
documents making a claim about the READ'S COST. A status file naming the figure must carry its
condition; the clause does not reach every live file in the tree. Its durable home is a plan
amendment, which is the operator's signature to write.

The result, every figure with conditions: `check-state.sh` costs **5 GraphQL points** (board 3, 473
items, `8c2c24d`, `notes/measurement-after.md`) against **506** before (board 3, 486 items,
`e1bcdc1`, `notes/measurement-before.md`). Board 6, four items, both shapes back to back at
`8c2c24d`: **old 102, new 1**, `board_items: 4` on both sides (`notes/measurement-board6.md`).
Orchestrator spend across the feature: **46 GraphQL points**, this repository, 2026-08-19 to 08-20.

Nine of nine tasks done. `--kind unit` exit 0 / 18 of 18 scripts / 0 FAIL; `--kind integration` exit 0
/ 12 of 12 / 0 FAIL. `matrix_ok: true`, panel PASS, SIMPLIFY four angles zero applies. Close-out
complete: 34 Expertise entries across 14 files, gate exit 0; ship-refresh skipped and disclosed.

## Open Questions

- Q1 (blocking, operator): the re-grade's verdict on both criteria, against a pin that is current for
  the first time. If it still returns UNMET that is the answer, unreconciled.
- Q2 (record, operator): my correction to the correction — the pin WAS stale at grading time, and the
  evidence is two `git show` reads of committed `feature.json`. Ruling 3's worked example survives.
- Q3 (non-blocking): 17 backlog rows are command-ready for the operator to run; `cmd_backlog` is the
  main session's subcommand and I have not executed it.
- Q4 (non-blocking, harness defect): `check-state.sh:221-228` checks `review_sha` is present, never
  that it is current, and the hand-edit convention that would catch a stale pin is enforced on
  neither half. This is ruling 3's row.
