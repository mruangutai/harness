# Build-side four-angle simplify pass — FEAT-2397 — 2026-11-22

This ran as the last build step before `review_sha` pins (harness-simplify skill). It used four separate
read-only `scout` dispatches, one per angle file. Scope was `origin/main...HEAD` over the 55 paths
in `notes/simplify-scope.txt`, with feature records excluded. The tree was the merge
of origin/main at `3912d98a` plus the T-06 station (`9dffccd7`).

The settled surface, which was not flaggable: plan decisions D-01..D-04, every `decisions_affected`
row, the `answers-2026-11-22-*.md` rulings and the grilling note.

| Angle | Reader | Findings |
|---|---|---|
| Reuse | SimpC_Reuse | 1 (low) |
| Simplification | SimpC_Simplification | 1 (low) |
| Efficiency | SimpC_Efficiency | none. Gate-runtime's added parity case shares the existing fixture and driver batch, and the hot path loses a checker subprocess, a second stdout decode and the transcript-tail I/O. |
| Altitude | SimpC_Altitude | none. Decoding, drift checks, model policy and probe identity sit at their authority boundaries. |

## Applied by Main (build side, main-session-direct under DEC-174)

The one-fix ceiling was not needed: both passed on the first run. No assertion was deleted or
weakened.

1. **Reuse.** `tests/integration/test-dispatch-guard.py` `_declared_worktree_checkout` now composes
   `git_support.init_repo` / `commit_files` / `add_worktree`. Before, it re-implemented the
   git-init, identity, commit and worktree recipe. The seeded commit, the branch `wt-<flow>`, the
   station path `.claude/worktrees/harness/<flow>` and the marker write are unchanged. The suite
   passes 178/178, exit 0.
2. **Simplification.** In `tests/integration/test-check-domain-grant.py`, the one-entry wrapper
   `_session(name)` is deleted and its six call sites pass `{"session_id": ...}` inline. The suite
   passes 21/21, exit 0.

`python3 tests/unit/test-code-grade.py` passes after both applies.

## Skipped

None.
