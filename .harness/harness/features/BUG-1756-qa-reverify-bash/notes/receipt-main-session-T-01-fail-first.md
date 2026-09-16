# Fail-first receipt — T-01 (BUG-1756) — main-session-direct

Parent commit: 1cac517817c1a14b88effe8987d4b76bd58455ec (validate-digest.py unchanged; only the test stub switched from a bash `.sh` to a Python `.py` file, as run-unit-tests.py has been since #1674).

`python3 tests/integration/test-validate-digest.py` at that state:

    FAIL  [bug919] independent re-run agrees (exit 0) — accepted
          | exit=2 stderr="harness-qa reported VERDICT: PASS with suite: pass and matrix_ok: true, but an independent re-run of run-unit-tests.py at this checkout exited 2 — the gate reported evidence it did not have (issue #919) ...
    4/5 bug919 qa-matrix-reverify cases passed.

The green stub is refused because `_reverify_suite` spawns `["bash", run_bin]`. This is SC-04's red arm; SC-01..SC-03's cases (kind forwarding, first-failure stop, default set) are added with the fix and would not have compiled against the old spawn.
