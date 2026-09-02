# Observations - harness-ui-reviewer

- 2026-09-01: FEAT-51 panel-c1: a repo-relative `read` call (no absolute path, cwd not pinned to worktree) silently resolved plan-sign-gate.py against the MAIN checkout (307 lines) instead of the pinned worktree copy (416 lines) — the byte-identical-copies cross-tree hazard flagged for writes also bites plain reads. Always pass the absolute worktree path to `read`/`git show <sha>:` when auditing a pinned diff.
