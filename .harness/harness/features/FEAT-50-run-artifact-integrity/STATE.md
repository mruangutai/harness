# STATE

## Current

- feature: FEAT-50-run-artifact-integrity
- station: done
- pr: 1105, merged at `75bf0901`; branch tip `9f50ee66` is an ancestor of `origin/main`
- briefing: `notes/ship-review-2026-09-01-ship.md`
- handoff: `notes/handoff-ship.md`

**Shipped.** The ship transition ran on 2026-09-01 as a late closeout, after the pull request had
already merged. `gh-sync.py ship` posted the ship review on parent #1082, wrote the `Done` station
on all sixteen recorded cards (#1082, #1083–#1094, #1056, #1057, #1058), closed milestone 35, and
recorded `pr: 1105`. Every one of those was read back and verified, not assumed: all sixteen issues
read `CLOSED`/`COMPLETED`, all sixteen cards read `done`, and the milestone reads `state: closed`
with `open_issues: 0`. `plan.yaml` now carries `status: done`.

**No lead was dispatched in this run**, so `runs:` is unchanged at 12 and `cycles_used` stays at 8
of 10. A closeout that reworks nothing costs no cycle.

**The finalization is the main session's and is NOT done.** Two record lines must land on `main`,
and no agent in this checkout can put them there:

1. `main`'s `plan.yaml` still reads `status: review` — FEAT-41's migration (`559354bc`) moved the
   station key there after FEAT-50 merged and deliberately did not re-adjudicate the value.
2. `main`'s `feature.json` still reads `pr: null`.

Neither can be committed here: this branch is merged and two merges behind `main`, so a commit in
this worktree would need a second merge, which the closeout was told not to attempt. The direct
route is refused by the checkout binding **this feature built** — measured, exit 2:

> `check-domain: BLOCKED — …/.harness/harness/features/FEAT-50-run-artifact-integrity/plan.yaml is
> a feature artifact whose write belongs in worktree
> …/.claude/worktrees/harness/FEAT-50-run-artifact-integrity.`

The exact commands are in the briefing's **Terminal state** section. Until they land,
`check-state.sh` exits 1 with two FEAT-50 rows — INV-33 (stale `review_sha`, because FEAT-41 edited
`plan.yaml` after the pin) and INV-26 (plan derives `review`, board reads `done`). Both close on the
station write; neither is a defect in delivered code.

**Removing this worktree is the main session's or the `post-merge` hook's act, from outside the
tree.** `git worktree remove` exits 0 when run from inside the tree it deletes. Expect INV-29 to
start refusing on it once the station lands on the default branch, since that classifier reads the
landed station from `main`.

## Open Questions

- Q1 (non-blocking, for the operator): no post-build `harness-pm` goal-check was ever run against
  the delivered code — the two goal-checks on disk graded the PLAN. SC-01…SC-21 are graded instead
  by the validation panel (`notes/qa-feat50-pinned-review.md`,
  `notes/review-harness-code-reviewer-feat50-pinned.md`). Reconstructing it is one read-only run;
  briefing Q-A.
- Q2 (non-blocking, record gap): **SC-10** — "neither suite regresses" — has no first-hand
  measurement anywhere in the record. Both the qa and code personas recorded it as reported ground
  truth under their task constraints, and this closeout was instructed not to run project-wide
  suites.
- Q3 (non-blocking, harness defect): the two write routes disagree on the identical target. The
  Write route refuses a governed write to the main checkout's FEAT-50 record at exit 2; the Bash
  route returns exit 0 for `python3 gh-sync.py ship <that same dir>`, because
  `bash-write-guard.sh` cannot see through an interpreter. Briefing B-13. The refusal was honoured
  here rather than routed around.
- Q4 (non-blocking, harness defect): a merged feature's honest `review_sha` goes stale when a LATER
  feature's migration rewrites its `plan.yaml`. INV-33's terminal-station silence catches it only
  for features shipped in time; one sitting in `review` under a landing migration goes red for a
  reason nobody on it caused. Briefing Q-B.
- Q5 (non-blocking, harness defect): this checkout and `main` now disagree about `feature.json`'s
  schema — the worktree's copy REQUIRES `status`, the main checkout's post-write gate calls it
  UNDECLARED. The same bytes are valid and invalid depending on which checkout reads them. Resolves
  when the worktree goes; the shape does not. Briefing B-19.
- Q6 (non-blocking, carried): `PF-f52c5043…` (`med`), T-03's binding asymmetry, measured INERT
  because no production code sets `HARNESS_PROJECT_DIR`. Briefing B-5.
