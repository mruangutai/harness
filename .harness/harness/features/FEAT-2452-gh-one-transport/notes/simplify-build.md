# Build-side four-angle simplify pass — FEAT-2452 — 2026-11-23

Four separate read-only `scout` readers ran, one per angle file, over the merge-base..HEAD diff
of the 30 paths in `notes/simplify-scope.txt`. The settled surface was not flaggable: the
signed plan, the sign-off conditions, and the grilling's transport-only scope with caller policy
kept. Also settled: the pinned label matcher repeated verbatim, the (e) cut, deadlines as a
non-goal, and the legacy grade-1 mains.

| Angle | Reader | Findings |
|---|---|---|
| Reuse | SimpD_Reuse | 2 (low, test support) |
| Simplification | SimpD_Simplification | none. Each transport layer earns its place, and the caller adapters hold distinct policies. |
| Efficiency | SimpD_Efficiency | none. Measurement happens once, the counter is unmeasured, and nothing is dispatched twice. |
| Altitude | SimpD_Altitude | none. Mechanics sit in factory_gh, meaning stays at the callers, and confinement has one home. |

## Applied by Main (main-session-direct), no assertion changed
1. `tests/offline_gh_support.py`: the hand-rolled `_shell_quote` is replaced by `shlex.quote`.
2. `tests/unit/test-gh-cost-log.py`: the custom `_patched`/`_MISSING` context manager is replaced
   by `unittest.mock.patch.multiple`/`patch.object`, and its `contextlib` import is gone.

Re-run: test-gh-cost-log 59/59. A pool of test-gh-board, test-wayfind, test-gh-sync-open and
test-board-lifecycle shows no failures.

## Skipped
None.
