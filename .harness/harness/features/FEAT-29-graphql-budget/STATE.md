# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: none in flight
- squad: none
- status: Review — SC-08 and SC-09 re-graded UNMET; both remedies are operator rulings, not a fix cycle

**The independent re-grade contradicted both the operator's verification and mine, which is why it
earned its cycle.** `runs/2026-08-20-15-product/digest.md` grades SC-08 and SC-09 unmet, and the two
failures are different kinds — one genuinely wrong, one merely unproven.

**SC-08 was failed by THIS FILE.** Its previous revision stated a 506 figure with no condition, while
FEAT-29 reads `status: Building` and is therefore still in force. The recording rule this feature
exists to establish was violated by the orchestrator's own status file. Every cost figure below now
carries its board, that board's item count, and its commit.

**SC-09 failed on a stale pin, not on the tree.** `review_sha` was `4f2e5d0`, and
`git merge-base --is-ancestor 9c9785f 4f2e5d0` reports the rule's commit is NOT an ancestor of it. The
deliverable is correct and committed; the pin predated it. DEC-89 prescribes that a hand edit commits
with a `[harness:human]` prefix and the state check re-pins `review_sha` — `9c9785f` carries no such
prefix and no re-pin followed, so both halves of that doctrine were skipped, and DEC-89 is cited
nowhere in this feature outside the re-grade digest. Re-pinned to the tip.

The result, every figure with its conditions: `check-state.sh` costs **5 GraphQL points** (board 3,
473 items, `8c2c24d`, `notes/measurement-after.md`) against **506** before (board 3, 486 items,
`e1bcdc1`, `notes/measurement-before.md`). Board 6, the four-item fixture, both shapes back to back at
`8c2c24d`: **old 102, new 1**, `board_items: 4` on both sides (`notes/measurement-board6.md`).
Orchestrator spend across the feature: **46 GraphQL points**, this repository, 2026-08-19 to 08-20.

Nine of nine tasks done. `--kind unit` exit 0 / 18 of 18 scripts / 0 FAIL; `--kind integration` exit 0
/ 12 of 12 / 0 FAIL. `matrix_ok: true`, panel PASS, SIMPLIFY four angles zero applies. Close-out
complete: 34 Expertise entries across 14 files, gate exit 0; ship-refresh skipped and disclosed, no
map exists here. **Cycle budget EXHAUSTED at 10 of 10** — no squad fix cycle remains, and both
outstanding remedies are record-keeping or operator rulings, neither of which spends one.

## Open Questions

- Q1 (blocking, operator): SC-08 limb 3 — does *no such document* quantify over every in-force
  document, or only over documents asserting `item-list` is cheap? The lead reads *such* as binding to
  *still in force*. The instance is remedied; the reading is the operator's.
- Q2 (blocking, operator): SC-09 names no sha, and at HEAD the rule IS committed — so the criterion as
  literally written is satisfied, and it failed only under the convention of grading at `review_sha`.
  The lead recorded this disagreement with pm rather than reconciling it.
- Q3 (blocking, operator): both criteria stand UNMET on the record until re-graded, and no budget
  remains to re-grade them.
- Q4 (non-blocking, harness defect): `check-state.sh:221-228` implements INV-6 as a presence check
  only — nothing compares `review_sha` to the tip, and DEC-188 deleted the propagation checker. A
  stale pin passes the state gate silently, which is how SC-09's failure survived ten cycles.
- Q5 (non-blocking): SC-09's 10-second-polling limb is not assessable from any artifact — it was live
  main-session conduct, never a recorded rule.
