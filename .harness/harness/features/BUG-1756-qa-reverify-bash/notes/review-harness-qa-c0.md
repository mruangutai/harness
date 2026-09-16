# QA validation — BUG-1756-qa-reverify-bash c0

## Verdict

**FAIL.** The pinned matrix is not green: the authorized unit run failed in `tests/unit/omp-hooks.test.ts:1261`. The repaired #919 hook independently repeated that unit run and correctly refused an unconditional green QA claim. This failure is outside T-01's declared files and is an explicit scope-change question, not a T-01 remedy.

## Scope and matrix

- Reviewed pin: `01dd2ed8eb6802048cf21ef3508e2e9310096695`; detached validation worktree resolved to that exact SHA.
- Phase 1 expectations (before source): one integration regression must exercise each SC: named-kind Python invocation/acceptance (SC-01), first failure with real tail (SC-02), bare default invocation (SC-03), and Python-stub red-before/operational-failure fail-open behavior (SC-04).
- Required floor: `unit` because T-01 changes runtime Python gate code (`.harness/harness.json:204-219`). `integration` was additionally required by the signed T-01 verification and the changed gate-boundary regression test (`plan.yaml:28-32`).
- Phase 2: `tests/integration/test-validate-digest.py:2282`, `:2291`, `:2309`, and `:2318` cover SC-01 through SC-04 respectively. No Phase-1 coverage gap was found.

## Authorized pinned runs

| Kind | Command | Result | Evidence |
|---|---|---|---|
| unit | `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` | fail | Runner exited 1. `test-omp-hooks.py` failed: `host-stamped tokens > no result carries a figure: nothing is stamped and the run stays unmeasured (DEC-210)`; its assertion at `tests/unit/omp-hooks.test.ts:1261` expected `null` and received `undefined`. |
| integration | `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` | satisfied | Runner completed exit 0; its summary reports `72 files, 96.70s wall`, including `test-validate-digest.py` (27.09s). |

## SC evidence and fail-first

| SC | Covering test | Durable fail-first evidence |
|---|---|---|
| SC-01 | `tests/integration/test-validate-digest.py:2282-2288` | `notes/receipt-main-session-T-01-fail-first.md:3-11`: at parent `1cac517…`, the Python stub was launched by bash, causing the documented exit-2 refusal; the receipt identifies that same broken spawn as the precondition for the added kind-forwarding case. |
| SC-02 | `tests/integration/test-validate-digest.py:2291-2306` | `notes/receipt-main-session-T-01-fail-first.md:3-11`: same measured bash-to-Python-stub failure; it cannot produce the required first-failure tail/stop behavior and is the documented pre-fix state. |
| SC-03 | `tests/integration/test-validate-digest.py:2309-2315` | `notes/receipt-main-session-T-01-fail-first.md:3-11`: same measured broken spawn under the bare-runner precondition; the receipt records that the old launch path refused the green stub. |
| SC-04 | `tests/integration/test-validate-digest.py:2318-2326` | `notes/receipt-main-session-T-01-fail-first.md:5-11`: direct pre-fix run recorded `FAIL [bug919] independent re-run agrees`, exit 2, and explains the bash launch of the Python stub. |

## Repaired digest-gate re-verification

I submitted a syntactically complete unconditional `harness-qa` PASS claim with `suite: pass`, `matrix_ok: true`, and unit/integration kinds to `python3 .claude/skills/harness/bin/validate-digest.py --hook` at the pin. The hook reran the unit kind and refused it (exit 2). Its refusal was:

```text
harness-qa reported VERDICT: PASS with suite: pass and matrix_ok: true, but an independent re-run of run-unit-tests.py at this checkout exited 1 — the gate reported evidence it did not have (issue #919). Re-run the suite yourself, fix what fails, and return again once it is genuinely green. Tail of the independent run:
  ok self-test 0-injection idiom
  ok self-test 1-mutant beside original
  ok self-test 2-pid named mutant
  ok self-test clean controls
  ok self-test live tree, independent root and discovered floor
  ERROR could not resolve scan root above /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp3mnzigth
  ok self-test unresolved root refuses
  root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-bug1756-pin
  discovered 112
  ok no test mutates a path derived from the live checkout
  PASS test-suite-independence.py
  ----- test-feature-record.py (exit 0, 8.45s) -----
  .................................................................
  ----------------------------------------------------------------------
  Ran 65 tests in 8.330s

  OK
  PASS test-feature-record.py
  pool: 8 workers, 40 files, 8.63s wall
  slowest: test-feature-record.py 8.45s, test-code-grade.py 2.40s, test-suite-independence.py 1.77s
```

## Finding / scope-change question

- **substance; unowned (not T-01):** `tests/unit/omp-hooks.test.ts:1261` fails at the reviewed pin because `tokensOf(featureJson)` returns `undefined` where the test requires `null`. This makes both the direct unit run and the repaired hook's independent rerun red. The failing file is outside T-01 (`plan.yaml:28-32`), so expanding this task to change it is a scope change.

## Cleanup

Created `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-bug1756-pin` solely to execute the pin, then removed it with `git worktree remove`. A post-removal `git worktree list` contains no `.claude/worktrees/qa-*-pin` entry.
