# T-26 receipt — registered worktree rows

## Result

Committed T-26 as `3c8453c8` (`[harness:t-26] emit registered worktree rows`).

## Authorized DEC-229 amendment

- files was: `.claude/skills/harness/bin/dashboard/work.py`, `.claude/skills/harness/bin/test-work-dashboard.py`
- files now: `.claude/skills/harness/bin/dashboard/work.py`, `tests/integration/test-work-dashboard.py`
- verify was: `python3 .claude/skills/harness/bin/test-work-dashboard.py --case worktrees`
- verify now: `python3 tests/integration/test-work-dashboard.py --case worktrees`
- reason: the integration-test migration moved the work-dashboard harness into `tests/integration`; the amended case preserves the signed scoped behavior without reviving the retired bin path.
- authorization: `Feat53Resume.DesirableSilkworm`, 2026-09-16.

## RED

Before collector changes, the new worktrees case executed four assertions and exited 1:

```text
FAIL  worktrees include every canonical path exactly once
FAIL  worktrees retain primary linked detached orphan terminal and error rows
FAIL  only linked worktrees override feature copies
FAIL  worktrees use terminal classification and repository identity
Executed 4 worktrees assertions; discovered 4 worktrees assertions.
```

## GREEN

Command:

```text
python3 tests/integration/test-work-dashboard.py --case worktrees
```

Output:

```text
PASS  worktrees include every canonical path exactly once
PASS  worktrees retain primary linked detached orphan terminal and error rows
PASS  only linked worktrees override feature copies
PASS  worktrees use terminal classification and repository identity
Executed 4 worktrees assertions; discovered 4 worktrees assertions.
```
