# QA validation — BUG-1756 c1

**PASS.** The pinned matrix and repaired #919 re-verification are green at `c1f9601fe87660b732aac0bf5e5f72dd17fac0d7`; all four automated SCs have an exact covering case and fail-first/discrimination evidence.

## Phase 1 — expected coverage before source

T-01 must prove: (1) named `unit` and `integration` Python invocations accept a green claim; (2) first non-zero stops later kinds, retains its output tail, and refuses with exit 2; (3) no named kinds invokes the default runner bare; and (4) the Python-stub/bash defect reddens pre-fix while missing runner, real spawn error, and timeout fail open. The bugfix runtime predicate requires `unit`; the signed integration regression/verify requires `integration`.

## Pinned matrix

| Kind | Authorized command | Result and non-vacuity evidence |
|---|---|---|
| unit | `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0; runner discovered and executed 40 files. `tests/unit/omp-hooks.test.ts` ran under bun: 74 pass, 0 fail, 155 expectations. |
| integration | `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` | exit 0; runner discovered and executed 72 files, including `tests/integration/test-validate-digest.py` and its 10/10 bug919 cases. |

`matrix_ok: true`. No collection, import, or assertion failures occurred.

## SC and fail-first evidence

| SC | Pinned covering test | Exact pre-fix / mutant evidence |
|---|---|---|
| SC-01 | `tests/integration/test-validate-digest.py:2282-2288` asserts exit 0 and exact `--kind unit`, `--kind integration` argv. | Receipt arm 2, `notes/receipt-main-session-T-01-fail-first.md:19-20`: this exact case failed at pre-fix `24e766bb` with exit 2 and `argv=[]`. |
| SC-02 | `tests/integration/test-validate-digest.py:2291-2306` asserts first-kind-only argv, real `UNIT_TAIL_LINE`, no second-kind execution, exit 2. | Receipt arm 2, `:21-22`: this exact case failed at pre-fix `24e766bb` with exit 2 and `argv=[]`. |
| SC-03 | `tests/integration/test-validate-digest.py:2309-2315` asserts one bare runner invocation and acceptance. | Receipt arm 2, `:17-18`: this exact case failed at pre-fix `24e766bb` with exit 2 and `argv=[]`. |
| SC-04 | `tests/integration/test-validate-digest.py:2347-2369` reaches the real `subprocess.run` seam and asserts exit 0 plus `could not independently re-run` for `OSError` and `TimeoutExpired`; completed-nonzero remains covered at `:2291-2306`. | Receipt arm 1, `:3-5`, records the Python-stub/bash red at pre-fix. Arm 3, `:31-33`, mutates `except Exception: return None` to `raise`: both exact spawn-error and timeout cases fail with `RAISED OSError` / `RAISED TimeoutExpired`, so neither is vacuous. |

## c0 closure and #919 exercise

- **Q1 closed:** c1’s in-process OSError and timeout arms target `subprocess.run`, not the earlier directory precondition; both discriminatory mutants redden.
- **Q2 closed:** receipt arm 2 runs each exact SC-01/02/03 case against pre-fix `24e766bb` and records its red result.
- **Q3 closed:** the direct pinned unit run includes `tests/unit/omp-hooks.test.ts` and is green (74 pass, 0 fail), replacing c0’s unrelated line-1261 red.
- At immutable `c1f9601`, a syntactically complete unconditional `harness-qa` PASS naming both active kinds was accepted by `python3 .claude/skills/harness/bin/validate-digest.py --hook` (exit 0, no output). **Non-gating, out-of-scope observation:** a later feature-checkout `f29a34d3` hook refused the terminal return because it still launched the runner through bash; that checkout is outside this immutable review object and does not alter this c1 grade.
- Temporary detached worktree `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-c1-pin` was removed. Post-removal `git worktree list --porcelain` contains no `.claude/worktrees/qa-*-pin` entry.

## Findings

- `findings: []`
- `must_fix: []`

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pinned unit and integration matrix are green; c0 Q1/Q2/Q3 and #919 re-verification are closed."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 40 }
    - { kind: integration, state: satisfied, cmd: "python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 72 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-validate-digest.py:2282-2288" }
    - { id: SC-02, test: "tests/integration/test-validate-digest.py:2291-2306" }
    - { id: SC-03, test: "tests/integration/test-validate-digest.py:2309-2315" }
    - { id: SC-04, test: "tests/integration/test-validate-digest.py:2347-2369" }
  fail_first:
    - { sc: SC-01, evidence: "notes/receipt-main-session-T-01-fail-first.md:19-20 (exact pre-fix red)" }
    - { sc: SC-02, evidence: "notes/receipt-main-session-T-01-fail-first.md:21-22 (exact pre-fix red)" }
    - { sc: SC-03, evidence: "notes/receipt-main-session-T-01-fail-first.md:17-18 (exact pre-fix red)" }
    - { sc: SC-04, evidence: "notes/receipt-main-session-T-01-fail-first.md:3-5,31-33 (pre-fix bash red; OSError/timeout mutants redden)" }
  open_questions: []
  files_touched: [".harness/harness/features/BUG-1756-qa-reverify-bash/notes/review-harness-qa-c1.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1756-qa-reverify-bash/.harness/harness/features/BUG-1756-qa-reverify-bash/notes/review-harness-qa-c1.md
```
