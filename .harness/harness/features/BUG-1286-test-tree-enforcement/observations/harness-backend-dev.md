# Observations - harness-backend-dev

- 2026-09-05: T-03 (suite-census.py tree-audit): a bare relative path in `edit` (`tests/manual/suite-census.py`, copied from a `read` header) silently landed against the MAIN checkout instead of the worktree — the edit tool reported success with a fresh tag. Caught only by an immediate `git status --porcelain` check in the main checkout right after. Confirms G-18: always prefix the absolute worktree path, and verify with `git status --porcelain` in the worktree (not just "it returned success") after the FIRST write of a session.
