# Measurement — before, POSITIVE CONTROL (T-06 addendum)

## Why this exists

SC-04 grades that `check-state.sh` emits the identical violation set before and after the
cutover. The plain baseline in `measurement-before.md` contains **zero INV-26 lines**, because
the board agreed. Issue #588 records that INV-26 also prints nothing when the board read
FAILS. So after the change a silent break and a working cheap read produce identical output,
and SC-04 would pass either way — a comparison that cannot fail for the one invariant this
feature touches.

This run makes INV-26 SPEAK, so the after-measurement has something that can go missing.

## Method

Perturb, measure, restore, verify — the mutation-proof discipline, not an assumption.

1. `plan.yaml` copied aside.
2. All 7 `status: pending` tasks flipped to `done`. Per `gh_board.py:88` `derive_station`,
   every task done derives `review`, while the board reads `Building` from T-06s `start-task`.
3. Gate run, cost differenced across `gh api rate_limit`.
4. `plan.yaml` restored and proven **byte-identical** with `cmp -s`.

before: 524
after: 1030
delta: 506
inv26_violations: 8
plan_restored: byte-identical (cmp -s, exit 0)

## What the after-measurement must reproduce

These 8 lines, verbatim, at a cost of 1-2 points instead of 506. If the cheap read silently
skips, they vanish and the diff is loud instead of silent.

INV26-BEGIN
  VIOLATION  INV-26 FEAT-29-graphql-budget T-01 (issue #579): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-02 (issue #580): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-03 (issue #581): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-04 (issue #582): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-07 (issue #585): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-08 (issue #586): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget T-09 (issue #587): plan says done, so the card should read Done — the board reads Backlog.
  VIOLATION  INV-26 FEAT-29-graphql-budget parent (issue #571): the plan derives Review — the board reads Building.
INV26-END

## Side finding, answering the orchestrators open Q2

`gh-sync.py open` printed no board-station line, so whether sub-issues #579-#587 reached
board 3 was unverified. They did: every card above reads `Backlog`, which is a real station
on board 3 and not an absence. No repair needed, and none was made during a measurement.
