# QA gate — BUG-2171-task-structured — pin d3792019 (base b7af829c)

BLUF: FAIL. The required unit matrix gate and targeted integration regression passed at the pin, with fresh semantic red-to-green evidence for SC-02 and SC-04. The literal T-01 verify block then failed because its fixed smoke run id already exists; no fresh child/lead yield or automatic append was produced.

## Phase 1 expectations
- SC-02: independent absent, false, non-boolean and true `task.structured` fixtures must execute the port gate and discriminate base from fix.
- SC-04: the real yield handler must validate a JSON-object string exactly as object data, refuse malformed/non-object strings without validation, and retain held-run BLOCKED-only behavior.

## Matrix and runs
- Required: `unit` (`bugfix` + `touches_runtime_code`). `python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit`: PASS, 59 files; `test-omp-hooks.py`: 140 pass, 0 fail, 719 assertions.
- Not required: `integration` (the fix is not confined to tests/contract docs). `python3 tests/integration/test-check-omp-port.py`: PASS, 31/31; it directly exercises SC-02.
- No other matrix predicate applies. `typecheck` remains unresolved with null command and is not a matrix kind.

## Fail-first
- SC-02 — `tests/integration/test-check-omp-port.py:169`: fresh base red named absent, false, string `'true'`, and integer `1`; fixed gate made all five rows green. The base executed the assertion rows, not an invocation failure.
- SC-04 — `tests/unit/omp-hooks.test.ts:1719`: fresh base red was `expect(asString.validations).toHaveLength(1)`, expected 1/received 0; fixed hook passed 1/1 selected test. This is an assertion failure, not a loader failure.

## Gate failure and coverage gap
- The literal OMP smoke refused `feature-record.py run-start`: `runs[]` already contains `2026-11-08-02-smoke-product` as closed PASS. It therefore dispatched no lead or PM, made no yield, appended no fence, and the subsequent canonical-reader assertion failed. Fresh SC-03 runtime evidence is absent; prior receipts are context only and do not make this rerun pass.
- SC-01 and SC-03 are inspection criteria, not automated SCs. Existing source inspection confirms `task.structured: true`, `is not True`, and JSON-object parsing; it does not cure the failed fresh smoke.

## Principles applied
- None: this revalidation ran the signed deterministic verify recipe unchanged.
