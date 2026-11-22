# QA c7 — BUG-2253 cycle 4 (unit-floor closure) — PASS

**BLUF:** Literal T-01 verify at managed pin `3ba8dd4b` exits 0: 17 integration cases ok + 7 unit tests OK (≈11.1s, unit stderr only the unittest summary). Both SCs have retained fail-first receipts. The unit floor (#2281) is now closed by a named test file that exercises the gate's parsers. matrix_ok true. No blockers.

## Phase 1 (from BRIEF/plan only)
Expected: SC-01 buried FAIL/MUTATED lines before tail (multiple, >20 passing lines), tail-only fallback, refusal status kept; SC-02 six sites observe 30/0.05/0.10, six real-block timeouts, watchdog-independent. Matrix: change_type bugfix → unit `when touches_runtime_code` (validate-digest.py is runtime code, full-feature diff) ; integration is not floor-required (`fix_confined_to_tests...` false) but carries the SCs. Gaps vs Phase 1: none.

## Equivalences (derived by git diff, not assumed)
- `git diff 3c6fb908 3ba8dd4b -- validate-digest.py` empty; `-- tests/integration/` empty; `3c6fb908..pin` outside `.harness` = only the new unit file (+75). `d9026b74..pin` has zero changes under `tests/` or `.claude/`. So c4 integration receipts (green-c4, red-c4, discriminate-c4 on 3c6fb908/b228c3a2) bind the pin's gate and integration file.
- Base→pin gate differs (`_print_independent_run`, `_run_pool_file_lines`, `_run_pool_mutated_indexes` added) — parsers absent at base, as unit-red-3dd8bb67 shows.
- Unit file sha256 `42a2e8dc…212e` equals the receipt's subject hash (`unit-red.txt`); pin sha matches.

## Execution (the one assigned run)
Pin `harness-qa-c7` at `3ba8dd4bf65392a1dd4fe99dddfebb14fe68d01d`, tree clean (0 porcelain lines). Command verbatim: `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases && python3 tests/unit/test-validate-digest-run-pool-lines.py` → EXIT 0; 17 `ok [bug2253]` lines, `ALL PASSED`; `Ran 7 tests … OK`. Pin removed on return.

## Unit boundary / discovery
- Test loads the gate through `harness_boundary.load_repo_module("validate_digest_run_pool_lines", BIN/"validate-digest.py")` (sole path loader, `harness_boundary.py:532`) and calls real `_run_pool_file_lines` / `_print_independent_run` with stderr captured — behavioral, not source-text.
- Runner discovers `tests/unit/test-*.py` (`run-unit-tests.py:_patterns`); new file matches (62 unit scripts at HEAD). I did not run the standing `--kind unit` (not assigned); membership by glob only.
- 7 tests: ordering+duplicates, spaces, echoed case lines, echo-cannot-hide (same-name PASS), MUTATED adjacency to note, buried-before-tail report, tail-only fallback.

## Fail-first (retained receipts, `notes/receipts/`)
- SC-01: `red-c4.txt` — exact base 3dd8bb67 gate, selected group exit 1, 14 failures incl. buried-file case (natural red, semantic). `discriminate-c4.txt` — b228c3a2 gate fails the same-name-PASS echo case only (exit 1). `unit-red-b228c3a2.stderr` — unit `FAILED (failures=1)` on `test_no_echo_hides_a_genuine_failure` (`[] != ['FAIL outer.py','FAIL later.py']`, semantic).
- SC-02: `red-c4.txt` — base subject with timeout=3 sites: observed-3 budget failures and blocked-call failures (reconstructed subject, noted in the receipt).
- `unit-red-3dd8bb67.stderr` 7/7 AttributeError (parsers absent) is signature-absent: proves nothing about behavior, not counted as discrimination. The other 6 unit tests are green on b228c3a2 — their discrimination vs a behavioral defect is unshown (not claimed useless). Green: `green-c5.txt` (d9026b74, group+unit exit 0), `green-c4.txt`.

## Matrix
| kind | state | evidence |
|---|---|---|
| unit | satisfied | 7 named tests green; target is the changed parsers |
| integration | satisfied | 17 named cases green (SC carrier; full-file green at 3c6fb908 in green-c4-full) |

## Advisories (non-blocking, out of scope per operator)
1. Over-listing an echoed FAIL name is accepted cost (no-pairing monotone header membership); unit test pins only the no-hide direction.
2. Runner-launch/timeout fail-open unchanged, out of scope.
3. SC-02 base red uses a reconstructed (reverted-timeout) subject; only the observed old budget is evidence.
4. Standing `run-unit-tests.py --kind unit|integration` not executed this run (assignment limits to literal verify).

## Principles applied
None cited (no craft leaf read).
