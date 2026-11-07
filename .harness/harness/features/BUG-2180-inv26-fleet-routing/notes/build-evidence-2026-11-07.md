# BUG-2180 T-01 build evidence — 2026-11-07 (main-session-direct, DEC-174)

## Fail-first baseline

- Production code at baseline: `4a05030d401593003209f525fd06e00802eccd36` (origin/main). `check_state/board.py` was unchanged at that point. The worktree HEAD was `4f65a990`, the planning commit.
- Tests added first: commit `f1032619` ("INV-26 fleet-routing regression cases (x.1-x.6), red at base").
- Command: `python3 tests/integration/test-check-state-inv26.py`. **Exit 1.** The 31 existing assertions passed, so the owner/unbound controls stayed green. These 6 failed:
  - `FAIL - (x.1)`: traceback. The owner `org/repo` was asked for `[14, 16, 17]` and then raised `factory_gh.GhError: … Could not resolve to an Issue with the number of 14.` This is the live Kaya crash.
  - `FAIL - (x.2)`: traceback, the same GhError, and no finding.
  - `FAIL - (x.3)`: no calls and no finding. With owner sync off, the bound feature was never checked.
  - `FAIL - (x.4)`: traceback. `by_repo={'org/repo': {16, 17, 40, 41}}`, so the bound numbers were unioned into the owner read.
  - `FAIL - (x.5)`: exit 1 with a traceback (`GhError … number of 16`), and no CANNOT VERIFY finding.
  - `FAIL - (x.6)`: traceback. `owner_asked={16, 17, 40, 41}`, meaning the owner fell back to the unresolvable feature's numbers.
- Every failure is a routing or error-handling assertion. None is a setup or import failure.

## After the fix

- `check_state/board.py`:
  - `inv_26`, `_inv26_check`, `_inv26_groups`, `_inv26_binding` and `_inv26_group` replace the owner-wide `_inv26_numbers`, `_inv26_stations` and `_inv26_compare`.
  - `_inv26_import` also loads `feature_schema`.
- Command: `python3 tests/integration/test-check-state-inv26.py`. **Exit 0, 37 `ok`, 0 `FAIL`.** Wall time ≈ 6.6 s.
- Neighbouring suites, each exit 0:
  - `tests/integration/test-check-state-table.py`
  - `test-checker-structure-locks.py`
  - `test-check-state-entry.py`
  - `test-gh-sync-ship.py`
  - `tests/unit/test-broad-catch-census.py`
  - `test-config-shape-matrix.py`
  - `test-gh-board.py`
- `check-plan-routes.py --canonical-reader-audit`: 0 unresolved reader sites. `check-plan-routes.py`: 0 violations across 6 plans.
- `uvx pyflakes check_state/board.py tests/integration/test-check-state-inv26.py` reported 5 unused-local warnings in other invariants (INV-37 L335, INV-30, INV-13). The same warnings exist at baseline, and none is in INV-26.

## Live smoke (real GitHub, read-only)

- Command: `HARNESS_PROJECT_DIR=<FEAT-01-kaya-platform worktree> python3 <this worktree>/.claude/skills/harness/bin/check-state.py --feature FEAT-01-kaya-platform`, with `FACTORY_GH` set to a logging wrapper around `gh`.
- Before the fix, the same command aborted with `factory_gh.GhError: … Could not resolve to an Issue with the number of 17` (2026-11-07, recorded in #2180).
- After: **exit 0, no INV-26 finding, no traceback.** The wrapper logged three calls:
  1. `api repos/mruangutai/kaya/contents/.harness/harness.json?ref=main` (binding resolution)
  2. `auth status`
  3. a single `api graphql -F owner=mruangutai -F name=kaya` covering issues 14, 16–26.
- mruangutai/harness was never asked about the Kaya numbers.
