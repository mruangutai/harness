# Observations - harness-qa

- 2026-08-31: the read tool returned stale/mismatched content for two separate line-range reads on large files in this session (test-check-domain.py:2530-2625, worktree_terminal.py:178-256) — showed a different function's body than sed/grep confirmed at those exact lines. Cross-verify large-file line-range reads with bash sed/grep before trusting them for this repo.
