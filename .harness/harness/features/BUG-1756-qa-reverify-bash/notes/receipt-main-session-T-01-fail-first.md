# Fail-first receipt — T-01 (BUG-1756) — main-session-direct

## Arm 1 — the stub as a Python file (SC-04 red on the defect)

Parent 24e766bb (validate-digest.py unchanged; the test stub switched from a bash `.sh` to a Python `.py` file, as run-unit-tests.py has been since #1674): `independent re-run agrees` FAILs with exit 2 — the green Python runner is refused because `_reverify_suite` spawns `["bash", run_bin]`.

## Arm 2 — every SC case against the PRE-FIX validator (validate c0 Q2)

Throwaway `git worktree` at 24e766bb with the final `tests/integration/test-validate-digest.py` copied in; `python3 tests/integration/test-validate-digest.py`:

    FAIL  [bug919] independent re-run agrees (exit 0) — accepted
          | exit=2 stderr="harness-qa reported VERDICT: PASS with suite: pass and matrix_ok: true, but an independent re-run of run-unit-tests.py at this checkout exited 2 — the gate reported evidence i
    ok    [bug919] independent re-run disagrees (exit 1) — the false-PASS is refused
    ok    [bug919] a non-PASS verdict is never re-run — the stub was never asked to run
    ok    [bug919] a missing suite script fails OPEN, loudly — never blocks on our own gap
    ok    [bug919] RED proof: with the qa wiring removed, the same false PASS is accepted
    FAIL  [bug919] BUG-1756 SC-03: a claim naming no kinds runs the Python runner once with no --kind
          | exit=2 argv=[] stderr="harness-qa reported VERDICT: PASS with suite: pass and matrix_ok: true, but an independent re-run of run-unit-tests.py at this checkout exited 2 — the gate reported ev
    FAIL  [bug919] BUG-1756 SC-01: a claim naming unit+integration runs the Python runner once per kind
          | exit=2 argv=[] stderr="harness-qa reported VERDICT: PASS with suite: pass and matrix_ok: true, but an independent re-run of run-unit-tests.py at this checkout exited 2 — the gate reported ev
    FAIL  [bug919] BUG-1756 SC-02: the first failing kind stops the rerun and its real tail is reported
          | exit=2 argv=[] stderr="harness-qa reported VERDICT: PASS with suite: pass and matrix_ok: true, but an independent re-run of run-unit-tests.py at this checkout exited 2 — the gate reported ev
    ok    [bug919] BUG-1756 SC-04: a spawn OSError fails OPEN, loudly
    ok    [bug919] BUG-1756 SC-04: a re-run timeout fails OPEN, loudly
    6/10 bug919 qa-matrix-reverify cases passed.
    ok    [bug919] a feature_root lookup failure resolves to None, never a silent owner_root substitution
    1/1 bug919 fallback-resolution cases passed.

SC-01 (kinds forwarded), SC-02 (first failure stops), SC-03 (bare default) each FAIL with exit 2 and `argv=[]` — the Python stub was never executed, so no `--kind` argv was recorded; SC-04's two arms are fail-open behaviour the old code already had and pass on both sides.

## Arm 3 — SC-04 discriminates (validate c0 Q1)

Mutant: `_reverify_suite`'s `except Exception: return None` → `raise`. Both SC-04 arms go `FAIL … RAISED OSError` / `RAISED TimeoutExpired`; with the real code both are `ok`. The arms monkeypatch `subprocess.run` at the exact seam inside the loaded validator (the c0 directory fixture never reached it).
