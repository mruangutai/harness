# QA c8 — BUG-2253 reduced scope (cycle 5) — PASS

**BLUF:** The signed T-01 verify exits 0 at managed pin `7e590f73` (3 integration cases ok, 7 unit tests OK, ~1s). SC-01 has retained fail-first receipts. SC-02 is inspection-only and is confirmed by inspection. The deletion left no dead helpers. matrix_ok true.

## Phase 1 (BRIEF/plan only)
SC-01 needs these tests. Several FAIL/MUTATED files sit buried above 20 passing lines and must be listed before the tail, once, in order. Echoed or unclosed run_pool-shaped lines must hide no real failure. A red re-run with no matching lines must keep the tail alone. Refusal status is unchanged. The unit file covers the parsers. SC-02 is inspection, so it has no behavioral test. Matrix: change_type bugfix. The unit kind is `when touches_runtime_code`, and validate-digest.py is runtime code, so it is required. The integration kind is `when fix_confined_to_tests...`, which is false; it still carries the SCs. Gaps against Phase 1: none.

## Execution (the one assigned run)
- Pin: `.claude/worktrees/.pins/BUG-2253-…--2026-11-22-07-validate-validator--harness-qa`. HEAD was `7e590f735af90220baec7013c7ce8eafc2163bce`, with 0 porcelain lines before and after. `worktree-state.py --verify --checkout <pin>` printed "converged" and exited 0.
- Command, verbatim: `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases && python3 tests/unit/test-validate-digest-run-pool-lines.py`. I ran it with HARNESS_AGENT_TYPE unset.
- EXIT 0, elapsed 1s (under the 60s limit). 3 `ok  [bug2253]` lines, `ALL PASSED`, 0 FAIL lines. Unit: `Ran 7 tests … OK`. The stdout and stderr files are `/tmp/c8.out` and `/tmp/c8.err`. They are ephemeral and not copied into the feature, so the quoted lines are the record. stderr held only the unittest dots and summary.
- Pin removed on return. The `remove` call exited 0, and the leftover count is 0.

## Relation to prior pin (derived by diff)
- `git diff 3ba8dd4b 7e590f73 -- .claude tests/unit tests/integration/canonical-reader-classification.json` is empty.
- The only product change since the previous PASS is `tests/integration/test-validate-digest.py` (+3/-224). The gate, unit file and inventory are byte-identical.
- Base→pin: validate-digest.py, the integration file and the unit file changed. The classification JSON is unchanged.

## SC-02 inspection
- `HOOK_HANG_BUDGET_S = 30` is at line 1030, with a rationale comment naming FIFO, dangling symlink and 10,000-deep JSON. It says blocking must fail rather than hang, and that 30s is load headroom, not a performance claim.
- Six sites use `timeout=HOOK_HANG_BUDGET_S`: lines 3033, 3066, 3286, 3288, 3316 and 3318. The last four include the lead-binding calls.
- `grep timeout=3\b` returns nothing.
- Base→pin timeout diff contains only these 6 replacements plus the comment. Other timeouts (30/60/120) are untouched.
- Dead-helper check: the 14 `_bug2253_*` helpers removed in the 232-line deletion have 0 remaining references. All 7 survivors have ≥2 occurrences (a definition plus a use). `run_bug2253_cases` calls the 3 cases. The removed imports (`mock`, `signal`, `threading`) left no unused top-level import. `mock` was imported locally inside deleted functions. This was an AST/regex check, not a linter run.

## Fail-first (retained receipts, `notes/receipts/`)
- SC-01 (natural red, semantic): `red-c4.txt` (+ .stdout/.stderr) runs the exact base 3dd8bb67 gate against the group. Exit 1, including the buried-file case. `discriminate-c4.txt`: the b228c3a2 gate fails the same-name-PASS echo case, exit 1. `unit-red-b228c3a2.stderr`: FAILED (failures=1) on `test_no_echo_hides_a_genuine_failure`.
- `unit-red-3dd8bb67.stderr` (7 AttributeErrors, parsers absent at base) is signature-absent. It proves no behavior and is not counted. Discrimination of the other 6 unit tests against a behavioral defect is unshown, not claimed useless.
- Green: `green-c5.txt`, `green-c4.txt`.
- I did not re-red this cycle. The gate and the 3 retained cases are unchanged from the c4/c7 evidence. Nothing in this pin changes their subject.

## Matrix versus suite breadth
- Matrix floor: unit (satisfied, required). Integration is not floor-required but is the SC carrier (satisfied). Both are satisfied by named tests that exercise the changed gate: 7 unit and 3 integration cases.
- Not run: standing `run-unit-tests.py --kind unit|integration`. The assignment limited me to the literal verify. This is a breadth gap (G-04): the full-bucket green is not shown at this pin. The last full-file integration green is `green-c4-full`, at 3c6fb908. The only product change since then is the test deletion plus the unit file's addition.
- Other kinds: functional is excluded. component and ui are unresolved and do not cover this surface. The `__bug_class__` clause is an unresolvable placeholder.

## Advisories (non-blocking, settled or out of scope)
1. Over-listing an echoed FAIL name (accepted Low).
2. Runner-launch/timeout fail-open is unchanged.
3. #2283 concurrency cause is excluded.
4. The 3-case integration group no longer includes a base-red SC-02 receipt, by operator ruling.

Capabilities used: git diff/show, grep/AST inspection, managed pin, the one signed verify, worktree-state --verify. Not used: full suites, linters/builds/formatters, perturbation, re-red.

## Principles applied
None cited (no craft leaf read).
