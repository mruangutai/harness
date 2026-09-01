# plan.yaml MED fixes — M-1, M-2, M-3 and the T-10 twin

**BLUF.** All four are closed by surgical edits to `plan.yaml` alone. `check-plan-routes.py` exits 0,
the plan still holds 13 tasks / 12 decisions, and both approval blocks still read `pending`. No SC,
no task count, no decision count changed. Nothing was committed.

## M-3 — T-05's verify could not fail on the skipped adapter

Replaced the multi-file `grep -n "set-task-station" <src> <adapter>` with a per-file `for` loop that
`exit 1`s naming the file that failed, and extended the `surgical .Edit` absence check to cover
**both** files. Rationale, recorded in T-05's intent: the adapter is what a Claude-hosted
orchestrator actually reads, so an adapter still carrying the Edit route leaves the old route live
regardless of the canonical source. The loop uses `if ! grep -q …; then … exit 1; fi` rather than
`grep … && { exit 1; }` so a negative check is never mistaken for block failure under `set -e`.
Smoke-tested on three fixtures: source-only match exits 1, both-match exits 0, stale adapter exits 1.
The old form returned 0 on all three.

## M-1 — T-07's verify tested only the deletion side

Chose the **behavioural** option (b), not a residual grep, and said why in the intent: `status`,
`Done` and `Review` all occur legitimately in these five readers as board column names and as the
approval status, so no grep over them is both discriminating and reachable (P-01).

Two changes. The verify now also runs `test-check-plan-routes.py`, `test-board-lifecycle.py` and
`test-gh-sync.py` — without them the verify ran no code from `board_lifecycle.py`,
`check-plan-routes.py` or `gh-sync.py` at all. And the intent now requires each of the five readers
to gain a case in its own test, **demonstrated failing before the repointing**, that builds a feature
dir with no `feature.json` status and a sibling `plan.yaml` station, and asserts the reader returns
it. A half-applied migration reds those cases.

Cost, disclosed in the intent rather than absorbed: `test-gh-sync.py` is the 149 s case T-10 already
discloses, so T-07 now runs long under the same accepted deferral (PB-01 in `BRIEF.md`). It is the
only proof `gh-sync.py` was repointed.

## M-2 — T-09's refusal named a file T-13 may never create

Took neither (a) nor (b) verbatim; a variant of (b) that the plan already uses elsewhere. T-09's
refusal — and the matching assertion in `test-check-domain.py` — now name **`plan-merge.py`
(`plan-write.py` after T-13)**: the basename that exists on disk when T-09 runs, read from the bin
directory rather than retyped from the plan.

Why this over (a): it closes the live window (a) leaves open, and it keeps the strikeability
paragraph at 1179-1180 **true as written** — nothing depends on the rename, so that paragraph needed
no edit and got none. T-13's caller list one paragraph later stays accurate too: its absence-grep for
`plan-merge` across `.claude` will find this refusal text and force the update. This is the exact
convention T-08 already uses for the same tool (`plan.yaml:764-765`).

Why not a runtime-resolved path: T-13's verify asserts the string `plan-merge` is absent from
`.claude`, so any resolver naming both candidates would red it, and a `plan-*.py` glob also matches
`plan-sign-gate.py`.

## The T-10 twin — a refusal that named the path but not the why

`cmd_ship`'s worktree refusal now states the reason first — the feature dir resolves inside a
worktree about to be deleted, so a terminal station written there would not survive — and then names
the equivalent main-checkout path, matching F-1's form. The load-bearing sentence is carried over
from T-09: a refusal that says only what to use instead is indistinguishable from a stuck gate, and
an agent reading it as one retries ship elsewhere instead of moving the write.

## Open questions

None. Nothing here required an SC change, a new task, or a new decision.
