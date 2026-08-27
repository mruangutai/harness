# Observations - harness-backend-dev

- 2026-08-26 (T-05 cycle 1): "confirmed present in the pre-fix run too" is not evidence unless the
  pre-fix run predates ALL of this task's edits -- cycle 0 compared against its own mid-task state
  (already containing its first fix) and mis-filed two new fail-opens as pre-existing. Compare
  against the actual last-known-good baseline, not against "before my SECOND edit".
- 2026-08-26 (T-05 cycle 1): a lazy import moved inside one gate function does not cover every
  caller of that function -- require_or_die() has multiple callers (check-state.sh at minimum) and
  the fix that satisfied bash-write-guard.sh/check-domain.sh (neither of which calls
  require_or_die()) left check-state.sh broken. When a shared function's caller list is not
  enumerated, assume it is longer than the two you tested against.
- 2026-08-26 (T-05 cycle 1): git stash push -- <specific paths> (not a bare git stash) isolates
  "is this failure caused by MY edit" from "is this failure caused by the tree's other in-flight
  uncommitted work" in a multi-task worktree -- a bare stash reverts everyone's uncommitted state at
  once and produces a misleading comparison.
