# T-07 receipt — grading CLI repair

## BLUF

The current `grading.distribution()` implementation already passes every tracked Python path to the requested project's real `code-grade.py` invocation; commit `e07481af` adds the missing real-CLI regression so omission cannot recur.

## Fail-first evidence

A temporary git fixture containing `probe.py` ran the current CLI with `--json` and no PATH inputs before source editing. It exited 2 with exactly:

```
usage: code-grade.py [-h] [--base BASE] [--head HEAD] [--json] [paths ...]
code-grade.py: error: provide PATH... or both --base REF and --head REF
```

The inspected production source already had the required `git -C project_root ls-files` and tracked `.py` path invocation, so no source amendment was necessary.

## Post-fix proof

`test_grading_distribution_runs_real_cli_with_tracked_python_paths` creates the temporary fixture project and executes `grading.distribution()` without mocking its subprocess. It passes only when the real CLI receives tracked Python paths for that fixture project.

Exact T-07 verify after commit:

```
..................
----------------------------------------------------------------------
Ran 18 tests in 3.024s

OK
```

- Commit: `e07481af` (`[harness:t-07] verify grading CLI inputs`)
- Changed file: `tests/unit/test-metrics-kpi.py`
- Amendments: `[]`
