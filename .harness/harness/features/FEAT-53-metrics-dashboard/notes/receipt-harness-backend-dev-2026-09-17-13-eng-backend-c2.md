# Backend repair receipt — FEAT-53 cycle 2

All-window KPI enrichment now resolves refs once with `git for-each-ref`, skips unavailable feature refs without calling `git diff --numstat`, and calculates a shared available branch once. Commit: `b2f41726` (`fix: reuse all-window KPI branch diffs`).

## Focused regression proof

`tests/unit/test-metrics-kpi.py` adds an interface-level case that makes one ref unavailable and assigns the same available ref to two features. It asserts the unchanged unavailable reason, the successful diff values, one ref sweep, and exactly one diff subprocess.

## Verification

```text
$ python3 tests/unit/test-metrics-kpi.py
.....................
----------------------------------------------------------------------
Ran 21 tests in 3.107s

OK

$ python3 tests/integration/test-metrics-dashboard.py
....full repository /api/kpis elapsed: 3.721s
..
----------------------------------------------------------------------
Ran 6 tests in 5.283s

OK

$ python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/code-grade.py --base 7ddf6d67e31cee63ac8fbd4f8fd9f49d2e98a594 --head HEAD
PASSING: 5
```

No full native kind, formatter, linter, project-wide suite, or client Vitest was run.

## Scope

Committed files:

- `.claude/skills/harness/bin/dashboard/kpi.py`
- `tests/unit/test-metrics-kpi.py`

A guard refused removal of generated `dashboard/__pycache__`, incorrectly resolving the FEAT-53 worktree location as the main checkout. Reported to the engineering lead for cleanup; no workaround was used.
