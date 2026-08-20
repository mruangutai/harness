# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: none in flight
- squad: none
- status: Building — goal-check FAIL, **8 of 10 SC met**; two unmet, both operator-owned

**The feature works and is proven.** `check-state.sh` costs **5 GraphQL points against a 506
baseline** at 473 items. Board 6 rules out the competing explanation: **102 vs 1 with `board_items: 4`
on both sides**. Discovery is intact — the control's seven lines reappeared verbatim, and the live run
returns two different station values across nine cards, which no truncating or failing read can do.

Both suites green at the tip: unit exit 0 / 179 `^PASS ` / 0 FAIL; integration exit 0 / 0 FAIL.
`matrix_ok: true`, panel PASS, SIMPLIFY zero applies.

**SC-09 is unmet and ship-blocking: T-08's deliverable is NOT in the committed tree.** I re-ran the
check the product lead could not (leads hold no Bash) — `git show 4f2e5d0:CLAUDE.md` lacks the
wait-loop rule entirely; it exists only in the operator's uncommitted working-tree edit, which is also
**20 lines shorter** than the committed file (9 insertions, 29 deletions). T-08's `verify:` passed by
reading the working tree rather than the tree under review. Remedy is the operator's: one commit.
SC-09's cost-citation clause is separately absent from both versions — and budget is **not** the
obstacle, `CLAUDE.md` being 55 lines against DEC-181's 80.

**SC-08 is unmet: the absence clause is false, and the live set is one shipped feature.** My corpus
sweep: the grilling note is struck by T-05 ✓; `FEAT-13/BRIEF.md` and
`.harness/notes/grilling-board-read-lookups-2026-08-10.md` already call the figure stale, so they do
not refute; the refuting set is **`FEAT-11`'s five artifacts**, and `FEAT-11` reads `status: Done`.
Root cause is planning, not execution: a criterion quantifying over "every surviving document" cannot
be discharged by a task whose `files:` names one.

Briefing: `notes/ship-review-2026-08-19-03.md`, rendered.

Budget: **46 GraphQL points** across the whole feature. **8 cycles of 10; 14 runs of 20.** Five lead
runs closed with a member still in flight — three bought no artifact, one built a digest from a
mid-write read, one became a false premise in a brief.

## Open Questions

- Q1 (blocking, operator): commit `CLAUDE.md` so T-08's deliverable is in the shipped tree, and rule
  on SC-09's cost-citation clause — amend it, or add the figure.
- Q2 (blocking, operator): SC-08's absence clause versus `FEAT-11`'s shipped artifacts. Striking a
  dated ship-review and UAT falsifies a record; T-05's own precedent is strike-in-place with the
  correction beside it. Or amend SC-08 to scope to live documents.
- Q3 (non-blocking): close-out — ship-refresh and distillation — has not run and is mine, dispatched
  as two dispatches in one message once Q1 and Q2 clear.
