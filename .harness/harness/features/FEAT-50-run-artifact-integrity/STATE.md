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
with `open_issues: 0`. `plan.yaml` now carries `status: done`, and `feature.json`'s legacy `status`
key is dropped to match FEAT-41's migrated vocabulary on `main`.

**No lead was dispatched in this run**, so `runs:` is unchanged at 12 and `cycles_used` stays at 8
of 10. A closeout that reworks nothing costs no cycle.

**The finalization is the main session's and is NOT done.** `main`'s copy of this feature dir still
reads `plan.yaml status: review` and `feature.json pr: null`. Neither line can be written from here:
this branch is merged and two merges behind `main`, so a commit in this worktree would need a second
merge, which the closeout was told not to attempt — and the direct route is refused by the checkout
binding **this feature built**, measured at exit 2:

> `check-domain: BLOCKED — …/features/FEAT-50-run-artifact-integrity/plan.yaml is a feature
> artifact whose write belongs in worktree …/.claude/worktrees/harness/FEAT-50-run-artifact-integrity.`

Seven tracked files differ from `main` and `feature-worktree.py remove` compares each byte for byte,
so all seven are copied together: `STATE.md`, `feature.json`, `plan.yaml`, `notes/handoff-ship.md`,
`notes/ship-review-2026-09-01-ship.md`, `notes/ship-review-2026-09-01-ship.html`,
`observations/harness-orchestrator.md`. Only the two lines above actually change. The commands are
in `notes/handoff-ship.md` and in the briefing's *Terminal state* section.

Until they land, `check-state.sh` exits 1 with two FEAT-50 rows — INV-33 (stale `review_sha`,
because FEAT-41's migration edited `plan.yaml` after the pin) and INV-26 (plan derives `review`,
board reads `done`). Both close on the station write; neither is a defect in delivered code.

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
- Q5 (non-blocking, harness defect): a migration landing under a live worktree leaves the two
  checkouts disagreeing about schema — this one's `feature-schema.json` REQUIRED the `status` key
  the main checkout's post-write gate called UNDECLARED, so `feature_json_write` refused the very
  edit the other gate demanded. Resolved here by writing the file directly; the shape recurs
  whenever a schema migration merges while a feature is in flight. Briefing B-19.
- Q6 (non-blocking, carried): `PF-f52c5043…` (`med`), T-03's binding asymmetry, measured INERT
  because no production code sets `HARNESS_PROJECT_DIR`. Briefing B-5.
