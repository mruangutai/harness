# T-23 receipt — backend-dev — c1

`db7ffbc6` — `[harness:t-23] Fix fallback and errors`

## Red evidence against c0

With the two regression fixtures and c0 collector logic, the amended verify exited `1` and reported both named failures:

```text
FAIL  unreadable worktree falls back to main
FAIL  malformed worktree plan is source-specific
Executed 9 collector assertions; discovered 9 collector assertions.
```

## Green exact verify

Command: `python3 tests/integration/test-work-dashboard.py --case collector`

Exit: `0`

```text
PASS  short id matching
PASS  long id matching
PASS  divergent main and worktree copies
PASS  worktree-only state
PASS  malformed input
PASS  unreadable worktree falls back to main
PASS  malformed worktree plan is source-specific
PASS  multiple segments
PASS  no GitHub dependency
Executed 9 collector assertions; discovered 9 collector assertions.
```

## Targeted code grade

Command: `python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/dashboard/work.py tests/integration/test-work-dashboard.py`

Exit: `0`; all 35 graded functions passed (production bar 4, test bar 3).

```text
PASSING: 35
```

## Files touched

- `.claude/skills/harness/bin/dashboard/work.py`
- `tests/integration/test-work-dashboard.py`
