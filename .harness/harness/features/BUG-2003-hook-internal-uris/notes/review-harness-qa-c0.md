# QA review c0 — BUG-2003 T-01 @ 85038f8c (harness-qa)

**BLUF: PASS.** Literal verify `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-omp-hooks.py` exits 0: 106 pass / 0 fail, 405 expects. Unit kind exits 0. matrix_ok true.

## Equivalence
Execution used the assigned worktree (HEAD = pin). `git diff f9e23bcb 85038f8c -- .omp tests` is empty and `git diff 85038f8c -- .omp tests` is empty, so the working tree equals committed source for both T-01 files. f9e23bcb^ = 7fba7e1d, the base named in the fail-first receipt. Pin diff vs base, scoped to the two files: harness-hooks.ts +94/-37 churn, omp-hooks.test.ts +131.

## Matrix (bugfix)
- unit `when touches_runtime_code`: TRUE (harness-hooks.ts changed) → REQUIRED. State: satisfied.
- integration `when fix_confined_to_tests_and_contract_docs`: FALSE (runtime changed) → not required.
- `__bug_class__`/match_bug_class: unresolvable placeholder (repo G-08); floor is unit alone.
- Unit cmd `run-unit-tests.py --kind unit`: exit 0, 44 files, discovered 118 (self-test line), `test-omp-hooks.py` listed and PASS (5.32s). The binding script is in the runner's set (P-14).
- Nonzero discovery: 106 named bun tests in 1 file; the 6 named cases below sit at tests/unit/omp-hooks.test.ts:1054-1125.
- Unit-kind output holds `FAIL BUG-1290` lines; these are the deliberate mutation-proof prints (repo G-09). Exit 0 governs.

## fail_first (receipt notes/receipt-t01-fail-first.txt: base 7fba7e1d, 102 pass / 4 fail; notes/receipt-t01-pass.txt: 106 pass / 0 fail)
- SC-01: `agent:// and xd://report_issue skip the domain gate on both routes and stages` (test:1054) red → green.
- SC-02: `every other scheme is refused by name and never reaches check-domain.py` (:1066) and `an edit MV destination is judged by the same scheme rule` (:1083) red → green.
- SC-03: `an allowed URI never exempts a sibling file or a refused URI in the same edit` (:1093) red → green. Controls `an ordinary file keeps its exact domain-gate payloads` (:1112) and `the main session's writes are untouched, URIs included` (:1125) passed before and after; they are NOT fail-first (the receipt labels them so).
- SC-05: the four red cases above, covering write/edit, both stages, MV, mixed edits, allowed/refused URIs and real files.

Assurance tier: the red run is the developer's retained natural RED (command + 4 named `(fail)` lines + counts). I did not reproduce it; my pinned-checkout perturbation (base adapter under pin tests) was refused by bash-write-guard, and the receipt was consistent with the base SHA and the new test names. The green run is my own.

## SC-04
Inspection SC, not mine to grade (code/security readers). Not assessed here.

## Findings
None.
