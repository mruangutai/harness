# T-06 c1 receipt

## Red proof

Against c0, the added `test_change_size_uses_project_default_branch_once` failed because no `git symbolic-ref --short refs/remotes/origin/HEAD` call occurred:

```text
FAIL: test_change_size_uses_project_default_branch_once
AssertionError: ... != []
Ran 6 tests in 0.311s
FAILED (failures=1)
```

The no-fallback branch was also red before its guard:

```text
FAIL: test_missing_project_default_branch_does_not_use_feature_diffs
AssertionError: 1 != 7
Ran 1 test in 0.011s
FAILED (failures=1)
```

## Green proof

The lead-amended T-06 verify ran verbatim and exited 0:

```sh
python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 tests/unit/test-metrics-kpi.py
```

```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.095s

OK
```

## Default-branch and diff evidence

The trunk regression mocks the sole project-root-scoped resolution as:

```text
git symbolic-ref --short refs/remotes/origin/HEAD -> origin/trunk
```

It asserts exactly one resolver call with `cwd=self.project.resolve()`, six `git diff --numstat` calls (one for each feature), and that every diff range starts with `trunk...`. A failed project-root resolution makes all change-size fields unavailable with `project default branch is unavailable` and runs no feature diffs; it cannot fall back to a branch from another repository.

## Targeted code grade

```sh
python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/dashboard/kpi.py tests/unit/test-metrics-kpi.py
```

Exit: 0. `PASSING: 31`; all production functions met bar 4 and all test functions met bar 3.

## Files and commit

Touched: `.claude/skills/harness/bin/dashboard/kpi.py`, `tests/unit/test-metrics-kpi.py`.

Commit: `016e5e3de81a2d2487445856c0ba09a24c663c46` (`[harness:t-06] Resolve project default branch`).
