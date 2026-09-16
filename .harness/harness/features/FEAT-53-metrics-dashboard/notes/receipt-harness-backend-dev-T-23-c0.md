# T-23 receipt — backend-dev — c0

Collector implemented and verified in commit `2c54210b` (`[harness:t-23] Collect fleet work`).

## Red assertions before implementation

`python3 tests/integration/test-work-dashboard.py --case collector` exited `1` before `dashboard.work` existed. The named red assertions were: short id matching; long id matching; divergent main and worktree copies; worktree-only state; malformed input; multiple segments; no GitHub dependency. Each reported `collector import failed: No module named 'dashboard.work'`.

## Amended task verify

Command: `python3 tests/integration/test-work-dashboard.py --case collector`

Exit: `0`

```text
PASS  short id matching
PASS  long id matching
PASS  divergent main and worktree copies
PASS  worktree-only state
PASS  malformed input
PASS  multiple segments
PASS  no GitHub dependency
Executed 7 collector assertions; discovered 7 collector assertions.
```

## Targeted code grade

Command: `python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/dashboard/work.py tests/integration/test-work-dashboard.py`

Exit: `0`; `PASSING: 29`. All production functions met bar 4 or better; all test functions met bar 3 or better.

## Files touched

- `.claude/skills/harness/bin/dashboard/work.py`
- `tests/integration/test-work-dashboard.py`
