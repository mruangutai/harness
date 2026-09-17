# T-31 receipt

T-31 extends the existing work collector with phase elapsed time and null-aware token aggregates while retaining T-26 worktree behavior.

## Fail-first

Before production edits:

```text
$ python3 tests/integration/test-work-dashboard.py --case metrics
Traceback (most recent call last):
  File "tests/integration/test-work-dashboard.py", line 171, in metrics_case
    original_now = work._now
AttributeError: module 'dashboard.work' has no attribute '_now'
```

The failing deterministic metrics fixture required the missing clock seam and metric fields.

## Amended scoped verification

```text
$ python3 tests/integration/test-work-dashboard.py --case metrics && python3 tests/integration/test-work-dashboard.py --case worktrees
PASS shipped elapsed phases
PASS in-progress elapsed phases
PASS missing boundaries stay null
PASS all measured tokens
PASS none measured tokens
PASS mixed token coverage presentation
PASS no dollar cost
Executed 7 metrics assertions; discovered 7 metrics assertions.
PASS worktrees include every canonical path exactly once
PASS worktrees retain primary linked detached orphan terminal and error rows
PASS only linked worktrees override feature copies
PASS worktrees use terminal classification and repository identity
Executed 4 worktrees assertions; discovered 4 worktrees assertions.
```

No formatter, linter, project-wide build, or project-wide test suite was run.

## Files

- `.claude/skills/harness/bin/dashboard/work.py`
- `tests/integration/test-work-dashboard.py`
