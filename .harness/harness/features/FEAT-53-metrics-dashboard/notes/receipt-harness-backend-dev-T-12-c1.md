# T-12 receipt — c1

## Verdict

BLOCKED — the native runner amendment resolves test discovery, but T-12's required API cannot serve either fixture or full-repository KPI values because its completed dependency chain currently raises inside `kpi.compute()`.

## Applied amendment

T-12 uses `tests/integration/test-metrics-dashboard.py`, discovered by `run-unit-tests.py`; its amended verify is `python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 tests/integration/test-metrics-dashboard.py`. Native discovery is available: the runner selects `tests/integration/test-*.py`, and `--check-layout` is its registration proof.

## Fail-first and blocking evidence

The first RED run after adding the amended integration test failed before production code because `dashboard/serve.py` did not exist (`FileNotFoundError`, exit 1). After a minimal Flask implementation called the mandated `kpi.compute(root, window)`, the integration run exposed two independent dependency failures:

- Fixture `project-a` returns 500 because `dashboard/grading.py` invokes `code-grade.py --json` with no paths or `--base/--head`; the grader exits 2 with `provide PATH... or both --base REF and --head REF`.
- The feature worktree returns 500 because `dashboard/kpi.py:_change_size` converts git numstat `-` to `int`, raising `ValueError: invalid literal for int() with base 10: '-'`.

Those files are T-08/T-10-owned dependencies and outside amended T-12's two-file grant. Catching either in the server would not serve the required KPI payload, would violate the exact `kpi.compute(root, window)` route contract, and would fail open.

The temporary source and test were removed rather than committing a known-red implementation. No generated client dist was staged and no trend write path was touched. The exact amended scoped verify was not run because it would require committing a test that deterministically fails from the dependency defects; no valid integration case count or elapsed full-repository computation exists.

## Required resolution

Repair the two `kpi.compute()` dependency failures under their owners, then redispatch T-12. Re-run the amended verify block verbatim only after that repair.
