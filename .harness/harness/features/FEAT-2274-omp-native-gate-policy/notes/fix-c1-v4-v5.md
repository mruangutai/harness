# Fix round 1 — V4 and V5

## V4: `[control] BUG-2141/lead-eng` (tests/unit/test-lead-start-preflight.py)

This is a migration to the new contract. FEAT-2274 deleted dispatch-guard's `spawns:` allowlist on purpose, and omp's native spawn policy is now the only authority. The old assertion, `refused_before_claim(...) and "spawns: list" in stderr`, encoded the contract the panel named as wrong.

The new assertion: product-lead -> harness-eng-lead on an all-direct plan passes dispatch-guard. The start exits 0, exactly one claim is held, `spawns: list` does not appear on stderr, and DEC-174 does not appear on stderr. It is still a control. If someone re-adds the allowlist, the dispatch is refused before the claim and the case fails.

RED (the HEAD 99d30cda copy of the file, run from tests/unit/ and then removed):
```
$ python3 tests/unit/_red_v4.py
FAIL [control] BUG-2141/lead-eng: lead -> harness-eng-lead keeps its existing spawns allowlist refusal
      | exit=0 claim=yes receipt=yes stderr=''
60 of 61 cases passed
```
GREEN: `python3 tests/unit/test-lead-start-preflight.py` -> `PASS [control] BUG-2141/lead-eng ...`, 61 of 61 cases passed.

## V5: code-grade bars (refactor only; no change in behaviour)

The three functions are now table-driven, with small module-level fire helpers and predicate helpers. code-grade.py only compares commits. To grade the working tree, I ran `code_grade._records` on the edited files directly. Every function named f2274/feat65/f65 grades ≥ 4. The grade-1/2 functions before the change were: run_feat2274_unavailable_cases at grade 1 (abc 45.3), case_feat2274_unavailable_outcome at grade 1 (abc 85.4, cc 17), and run_feat65_guard_cases at grade 2 (abc 26.6).

| Function | Checks before | Checks after | Shape after |
|---|---|---|---|
| run_feat65_guard_cases | 6 named cases (13 conjuncts) | 6, same names, inputs and conjuncts | `_FEAT65_CASES` table + `_feat65_fire_guarded/_escapes` + `_f65_*_ok` predicates |
| run_feat2274_unavailable_cases | 9 named cases (21 conjuncts) | 9, same names, inputs and conjuncts | `_F2274_CASES` table + `_f2274_fire_unavailable/_passes/_refusals` + `_f2274_unavailable_with/_quiet_pass/_refused/_object_refusals` |
| case_feat2274_unavailable_outcome | 8 `check()` calls | 8, same names and conditions | 6 probe helpers (`_f2274_emitter_checks`, `_open_guard`, `_closed_guard`, `_quiet_guard`, `_system_exit`, `_run_hook_body`) sharing `_f2274_guarded` |

Two notes:
- `feat2274_hook_guard_without_script_emits_no_unavailable` now also goes through the TypeError-catching helper. A signature regression there now shows up as a FAIL instead of a crash.
- The failure-detail strings changed slightly. For example, the normal-return detail is now `rc=… err=…`. None of the case names or conditions changed.

GREEN:
- `python3 tests/integration/test-validate-digest.py`: ALL PASSED. 15 f2274 and feat65 lines are `ok`.
- `python3 tests/unit/test-harness-boundary.py`: ALL PASS.
- `python3 tests/unit/test-code-grade.py`: PASS. Before the change it reported 2 failures, for run_feat65_guard_cases and run_feat2274_unavailable_cases.
