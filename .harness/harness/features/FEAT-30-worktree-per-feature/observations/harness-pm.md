# Observations — harness-pm — FEAT-30-worktree-per-feature

- 2026-08-20: writing plan.yaml through a QUOTED bash heredoc was DENIED by
  branch-create-gate.sh. The intent text of T-05 enumerated forbidden git shapes, one of which read
  as a branch-creating checkout with a placeholder name; the gate's regex matched the command STRING
  even though the heredoc creates no branch and runs no git. Fix was to write the file with the Write
  tool instead. Two lessons: (1) any plan whose subject is git itself cannot be authored through Bash
  in this repo, and (2) the gate has no notion of quoting — it scans the whole command text. Raised as
  a non-blocking open_question in the handoff.
- 2026-08-20: the dispatch named two consumers of the fixed segment count; there are four. The two it
  did not name are inside check-domain.sh's shape phase (_norm at :644, SWEEP_GLOBS at :602), spelled
  locally on purpose because that phase's import of harness_boundary is absorbing rather than
  fail-closed. Pattern worth keeping: when a lead cites "line X and line Y", grep the constant's own
  module comment for a list of deliberate non-consumers before believing the count.
- 2026-08-20: run-unit-tests.sh runs a drift detector over the UNION of its two script arrays, so
  merely CREATING a new bin/test-*.py file reddens the runner until it is registered. That makes
  "register in a later task with a depends_on edge" a decision about every intermediate verify, not
  just about CI visibility. Recorded as D-06 in the plan.
- 2026-08-20: a criterion about a CLI's refusal is only met when every ROUTE to the underlying
  operation is covered. SC-07 held inside feature-worktree.py (T-02) and was open on the Bash route:
  bash-write-guard.sh:424 tests `_ops[1] not in ("add", "move")`, so `git worktree remove --force`
  passed at exit 0 while the unforced form was refused by git itself at 128. Lesson for planning: when
  a plan puts a guard in a new tool, grep the EXISTING guard's parser for the same verb set before
  calling the criterion covered.

- 2026-08-20 (simplify apply, L-1): a fixture that satisfies the OLD mechanism by accident is
  invisible to every review angle. `test-check-domain.py` built `.claude/worktrees/wt1/` with
  `os.makedirs` alone; `WORKTREE_REL_RE` (`harness_boundary.py:36`) is worktree-agnostic, so 5
  pre-existing assertions plus all 16 of T-03's new in-worktree cases were green against a directory
  that is not a worktree. Replacing the regex with a pointer-reading mechanism reds all 21 at once.
  Lesson for planning: when a task swaps a mechanism, list the FIXTURES the old one accepted and ask
  which of them the new one rejects — the digest reported 2 of 21, and both the eng lead and my
  dispatcher narrowed it further, because `_show` looked like the only consumer at risk.
- 2026-08-20: also, `checkout_relative` and `linked_worktrees` read DIFFERENT sides of the git
  pointer pair (worktree-side `.git` file vs owner-side `.git/worktrees/<id>/gitdir`). A plan that
  says "a real linked worktree so a `.git` pointer exists" specifies only half of it.
