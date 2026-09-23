# QA gate — FEAT-64 c0

## BLUF

**PASS** — pinned review `dc71e09e0647882c63f66ab0b6d6048bc6dd2688` against baseline `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983` satisfies the cross-module unit/integration matrix. Required commands and the signed T-03 chain passed in a detached checkout at the review SHA; pinned code grade passed 48 changed functions.

## Phase 1 matrix

From the signed BRIEF and T-01/T-02/T-03 (`change_type: cross_module`), the matrix requires **unit** and **integration**. Expected coverage: preserved established suite bytes/exit status (SC-01); AST ceilings and increase/reduction mutants (SC-02); typed expected boundaries while unrelated exceptions escape, including `hook_guard` process-control behavior (SC-03); and one-load-per-execution for route and handoff authorities (SC-06).

| Kind | Command | Result |
|---|---|---|
| unit | `python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` | pass |
| integration | `python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration` | pass |
| signed T-03 | `python3 tests/unit/test-broad-catch-census.py && python3 tests/integration/test-check-plan-routes.py && python3 .claude/skills/harness/bin/check-plan-routes.py --consolidation-audit` | pass: both test scripts `ALL PASS`; audit reports `0 consolidation finding(s) under bin/` |
| grade | `python3 .claude/skills/harness/bin/code-grade.py --base a4a3d7f8 --head dc71e09e0647882c63f66ab0b6d6048bc6dd2688` | pass: 48 passing functions, 0 failures |

## SC evidence and fail-first

| SC | Coverage | Executed evidence | Fail-first evidence |
|---|---|---|---|
| SC-01 | named T-01/T-02 receipt suites | matrix unit/integration runners passed; final byte/exit comparison is receipt-only | `notes/red-first-receipts.md:43-112` (pre-change boundary cases red); final baseline/head byte comparison at `:7-41`, divergences ruled at `notes/build-divergences.md:7-31` |
| SC-02 | `tests/unit/test-broad-catch-census.py`, `tests/integration/test-check-plan-routes.py` | signed chain passed; census test asserts 16 zero ceilings and `harness_boundary.py == 2`; integration test exercises 4 independent zero-ceiling increase mutants, third-boundary mutant, and clean reduction | `notes/red-first-receipts.md:114-132` |
| SC-03 | T-01/T-02 typed-boundary tests, notably `tests/unit/test-harness-boundary.py`, plus integration boundary suites | required unit/integration runners passed; signed route test independently proves its unrelated `RuntimeError` escapes | `notes/red-first-receipts.md:45-112` (pre-change RuntimeError escape and hook-guard cases) |
| SC-06 | `tests/unit/test-handoff-done-when.py`; `tests/integration/test-check-plan-routes.py` | required unit/integration runners passed; route test asserts one `load_plan` call for both live and shipped plan fixture executions | `notes/red-first-receipts.md:71-73,117-120,134-135` |

## Non-vacuity

The executed T-03 integration suite names each mutation outcome: lib `except Exception`, lib bare `except`, tool `except Exception`, tool bare `except`, a third `harness_boundary` broad catch, and a clean reduction. Its real-tree audit found zero consolidation findings. The executed unit census independently asserts all 16 zero-ceiling entries plus the exact two-catch boundary ceiling. These are behaviorally discriminating fixture mutations, not a source-text absence check.

SC-01's baseline/head stream comparison and all pre-fix executions are retained receipt evidence, not re-executed historical evidence; this distinction is intentional and does not hide the source of proof.

## Findings

[]

## Coverage gaps

[]

## Principles applied

None; this was a read-only gate.
