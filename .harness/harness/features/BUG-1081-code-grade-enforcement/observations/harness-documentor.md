# Observations - harness-documentor

- 2026-09-01 (BUG-1081 T-04): DEC-208 was already taken on origin/main by FEAT-50 while the branch ceiling read DEC-207; allocated DEC-209. P-02 paid off, and the dispatch expected-number hint was wrong.
- 2026-09-01 (BUG-1081 T-04): first edit landed in the MAIN checkout, not the worktree — relative section path plus a byte-identical file (local main was behind origin/main, so both copies lacked DEC-208 and shared snapshot tag 84D2). Caught only by running git status in BOTH trees; reverted with git checkout on that one path and reapplied via an absolute section path.
- 2026-09-01 (BUG-1081 T-04): bash-write-guard refuses a redirect into mktemp for this persona, so a negative probe of a verify clause must run in-memory in python rather than by writing mutated fixture files.
- 2026-09-01 (BUG-1081 T-04): observations-merge.py crashes with FileNotFoundError on the .lock path when the observations/ directory does not exist yet; mkdir -p first.
