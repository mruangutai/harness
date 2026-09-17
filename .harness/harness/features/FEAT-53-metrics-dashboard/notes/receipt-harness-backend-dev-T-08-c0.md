# T-08 receipt

Implemented and committed escaped-defect KPI behavior in `657e0e67` (`[harness:t-08] add escaped defect KPI`).

## Authorized same-task amendment

- Files changed exactly from `[.claude/skills/harness/bin/dashboard/defects.py, .claude/skills/harness/bin/dashboard/kpi.py, .claude/skills/harness/bin/test-metrics-kpi.py]` to `[.claude/skills/harness/bin/dashboard/defects.py, .claude/skills/harness/bin/dashboard/kpi.py, tests/unit/test-metrics-kpi.py]`.
- Verify changed exactly from `python3 .claude/skills/harness/bin/test-metrics-kpi.py` to `python3 tests/unit/test-metrics-kpi.py`.

## TDD evidence

RED, before `defects.py` existed:

```text
Traceback (most recent call last):
  File "tests/unit/test-metrics-kpi.py", line 19, in <module>
    import defects
ModuleNotFoundError: No module named 'defects'
```

A separate unavailable-history RED cycle produced the expected unhandled `RuntimeError: fatal: not a git repository` before the unavailable payload branch was restored.

GREEN scoped verify, run from the worktree root:

```text
$ python3 tests/unit/test-metrics-kpi.py
.............
----------------------------------------------------------------------
Ran 13 tests in 2.318s

OK
```

The behavior test creates two `BUG-NN` feature units, one `Revert ` commit, and two `fix` commits; it asserts the hand-labelled count `3` and excludes both fixes. It also covers unreadable git history as unavailable.

## Code-risk grading

`python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/dashboard/defects.py .claude/skills/harness/bin/dashboard/kpi.py tests/unit/test-metrics-kpi.py` reported `PASSING: 53`; all production functions meet bar 4 or better and test functions meet bar 3 or better.
