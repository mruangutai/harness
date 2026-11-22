# QA review c0 — BUG-2253 T-01 (SC-01, SC-02)

BLUF: **ESCALATE.** Both automated SCs are proven (fail-first reproduced by me, fix green, integration kind green). One matrix question needs the operator: DEC-217's `unit when touches_runtime_code` leg fires (gate `validate-digest.py` changed) and no unit test exercises the change. I will not grade `unit` satisfied from integration evidence (P-04). If the operator rules the integration kind covers it (BRIEF "Verification gaps: None"), the verdict is PASS.

Identities: pin `21e064c9475e35a4abfdd71b5b5cdd23517c0659` (verified `git rev-parse` in managed pin); base `3dd8bb677bb2936361e3952030fc24f15bf9afc6` (merge-base of pin and base = base). Diff 3dd8bb67..21e064c9 touches 3 product files only: `validate-digest.py` (+26/-9 ish, only the failed re-run branch), `tests/integration/test-validate-digest.py` (+268), plus feature records. `canonical-reader-classification.json` unchanged (green.txt: 0 unresolved reader sites). Current HEAD baef2852 is a record-only commit; not used.

## Phase 1 (from BRIEF/plan, before source)
Expected: SC-01 buried multi FAIL + MUTATED on stdout and stderr above >20 passing lines → all listed before tail, heading once, tail unchanged, status 2; no-match fallback tail-only; base-red on buried case. SC-02 six sites observe 30 default and two rebound budgets; real blocked subprocess times out within budget+tolerance; missing timeout fails an independent watchdog; base-red. All have tests; no Phase 1 gap.

## Verification (mine, at the pin, `HARNESS_AGENT_TYPE` unset; no HARNESS_* env inherited)
- Literal T-01 verify `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases` → exit 0, 14 `ok  [bug2253]` rows, 0 FAIL, `ALL PASSED`, 6.7s wall (<60s).
- Standing integration kind `run-unit-tests.py --kind integration` → exit 0, `ALL PASSED`, 88 files, 122.5s; `test-validate-digest.py exit 0, 30.43s` (glob `tests/integration/test-*.py` binds the file, P-14).
- main(): `run_bug2253_cases` registered last in the checks tuple (test file ~6650) and selectable via `--only`; verify discovered 14 rows from this group.

## Fail-first, reproduced by me (natural-subject perturbation in the pin, restored; pin removed)
- SC-01: pin test file + base gate (`git checkout 3dd8bb67 -- validate-digest.py`): exit 1, exactly 1 FAIL — the buried-file case; the no-match fallback case stays `ok` (retained-safety, not red evidence, as the plan states). Output `/tmp/qa-c0-red-gate.out` (volatile).
- SC-02: pin test file with all six `timeout=HOOK_HANG_BUDGET_S` rewritten in memory to `timeout=3` (6 replaced, no source write): exit 1, 12 FAIL: six `observed=[3, 3, 3]` rows plus six block rows (`outcome=returned|timeout|FileNotFoundError spent≈2.0`), i.e. the 2s watchdog killed the blocked child rather than the call hanging or passing. Whole run 15.7s, no leaked process observed. Output `/tmp/qa-c0-red-budget.out` (volatile).
- Supplied receipts (observed, not rerun): `notes/receipts/red.txt` (subject base 3769919f155aee2013b6539ec3cf3d6ed4f9f49b, 13 FAILING, gate diff vs base empty) and `green.txt` (14 ok, ALL PASSED; subject "working tree at the pin" with no SHA stated). 3769919f vs 3dd8bb67 differ only under `.harness/` (checked `git diff --name-only | grep -v ^.harness` empty), so the red subject is code-identical to the immutable base. The receipt's SC-02 red subject is the final test file with six sites reverted, not the literal base test file (base has no new cases); my reproduction used the same construction.

## Simplify deviations assessed
1. One-token `(?:FAIL|MUTATED) \S+` fullmatch instead of bare prefix: narrower than BRIEF/plan ("every line beginning FAIL␠/MUTATED␠"). Matches run_pool's only emitted forms (`run_pool.py:113,134`: `FAIL <name>`, `MUTATED <name>`). Case echoed `FAIL  [x] some case` stays out and is asserted. Consequence: a file name containing a space, or other-format FAIL lines, would not be listed (still in tail when within 20). Intent-satisfied, literal-wording narrower (O-04) — advisory, below blocker.
2. Readiness as pid channel only: `ready` is never asserted. Sound: only `subprocess.run` raises `TimeoutExpired` for a still-running child; a startup failure exits → `outcome=returned`/other → red. No vacuous pass found. Intent text "readiness handshake" and "process-group" watchdog are weaker in implementation (pid kill of direct child; child IS the direct subprocess, `_t09_fire:1067`, `_lead_binding_result:3414`) — adequate, advisory.
3. Timing only the real call: sound; real `_t09_fire`/`_lead_binding_result` retained, only `VALIDATE` replaced (sibling digest_destination.py covered through dirname). Bound is `spent < 1.5` (budget 1.0 + 0.5).
Watchdog genuinely bound: in the SC-02 perturbation every block row failed at ≈2.0s.

## Matrix
`change_type: bugfix`. harness.json: always `[]`; `unit` when `touches_runtime_code` (DEC-217: any changed file outside `tests/**`, `*.md`, `.harness/` → TRUE, `validate-digest.py`); `integration` when `fix_confined_to_tests_and_contract_docs` (FALSE); `__bug_class__` unresolvable placeholder (never fires). Integration is nonetheless the SC evidence kind and was run (satisfied). Unit: no `tests/unit` file references `_t09_fire`, `RUN_UNIT_TESTS_BIN` or `check_qa_matrix_claim` → `missing`. Other kinds: functional/eval `excluded`, component/ui/typecheck unresolved (BRIEF: not this surface), three `locally_run` probes not on the changed detect surface.

## Advisory (out of scope, no blocker)
- Gate refusal text changed shape: "Tail of the independent run:" is now its own line instead of ending the first sentence; content/exit code (2) unchanged.
- `qa-record-read-failure` red row is `outcome=timeout spent≈2.01` at literal 3: discriminates only through the `spent<1.5` clause — still genuinely red.
- green.txt names no commit SHA for the fixed subject; this note supplies pin identity.

## Principles applied
Absence/subject/mutant (harness-code-review): the base-red rows are bound to the exact mutant (gate at base; literal 3), not to absence assertions.
