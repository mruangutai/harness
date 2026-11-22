# QA review c2 — BUG-2253 T-01 (SC-01, SC-02) — pin 2e96b583

BLUF: **Both c1 must-fixes are closed; SC-01 and SC-02 are proven by exact-base fail-first evidence. Verdict ESCALATE, solely on the settled `unit` floor** (`matrix_ok: false`, advisory per assignment). No task defect found. c0 and c1 are retained unchanged.

## Identity and run
- Audited range `3dd8bb67..2e96b583` in a managed pinned checkout (HEAD `2e96b583dadaff642873566c3234dde6af0eda74`, clean). `git diff --name-only 6cbdc417 2e96b583` outside `.harness/` is empty, so receipts at `6cbdc417` describe the pin's code exactly.
- Verbatim verify, run once by me (HARNESS_* env unset): `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases` → **exit 0, 15 `ok [bug2253]` rows, 0 FAIL, ALL PASSED, stderr empty, 9.43s wall**. Consistent with `green-c2.txt` (9.33s).
- Not re-run by me: the full integration kind. Supplied `green-c2-full.stdout` (exit 0, ALL PASSED, includes the 15 rows plus the sentinel) was read, not executed. The supplied `code-grade.py` PASSING:25 is the main session's claim, not mine.

## Must-fix 1 (SC-01 names with spaces) — CLOSED
Gate (`validate-digest.py` `_run_pool_file_lines`/`_is_run_pool_file_line`) matches run_pool's actual emission (`run_pool.py _emit_result`: `----- <basename> (exit N, Ss) -----`, body, `PASS|FAIL <basename>`; `MUTATED <name>` printed only after all blocks). `FAIL <name>` counts only when it closes the innermost open block of that exact name; `MUTATED` only with no open block. Spaces are kept (`.+` header capture). The case (`test-validate-digest.py` `_bug2253_buried_case`) buries `FAIL my test.py`, `MUTATED notes/my file.md`, stderr `MUTATED test-d.py`/`FAIL test-e.py` above 20+ passing lines, and asserts once, in order, one heading, before the tail, with in-block `FAIL  [x] some case`, `MUTATED inner-echo.txt` and `FAILED-NOT-A-FILE-LINE` excluded, and the 20-line tail boundary exact (`tail 2` in, `tail 1` out). No-match fallback case keeps the tail alone. Residual (non-SC, advisory): a failing file that itself echoes a line byte-equal to `FAIL <its own name>` inside its block would close early; unrealistic.

## Must-fix 2 (SC-02 watchdog) — CLOSED
`_bug2253_watchdog` polls from 2s until `stop()`, killing the child as soon as its pid file is readable (retries on missing/empty). `_bug2253_block_cases` requires `outcome == "timeout"` **and** `ready` (child wrote pid) **and** `spent < 1.5` (1.0s budget, call-only timing). So readiness is now a pass condition and a delayed start cannot evade the watchdog. `_bug2253_containment_case`: child delayed 2.5s under a 60s timeout that ignores the budget is killed (`exit -9`, `killed`, elapsed <10s). That case proves the watchdog primitive, not any site; site discrimination is the block rows. Residual (advisory): a correct site whose child starts later than the 1.0s budget under extreme load fails on `ready=False` — flake exposure, bounded to the loaded-host condition the signed budget docs exclude from any latency claim.

## fail_first (exact base, causality)
Subject: `red-c2.txt` — clean detached base `3dd8bb677bb2936361e3952030fc24f15bf9afc6`, production files byte-identical to base; only the test file is carried in (`6cbdc417` with six sites reverted to `timeout=3`, constant removed; sha256 `0728f033…d22e`). The base predates the cases, so carrying the test file in is the only possible red; it replaces c1's reconstructed-in-memory evidence. Command exit 1, 18.25s, 13 FAIL, streams separate (`red-c2.stdout`, empty `.stderr`).
- SC-01: 1 FAIL on the buried case. The base gate's stderr contains no `Failing or mutated files:` heading and its raw tail (`stderr tail 2..17`) leads, i.e. the defect itself (names buried above the 20-line tail) is what fails, not a setup error. The quiet case stays `ok` on base (fallback preserved).
- SC-02: 6 budget rows `observed=[3, 3, 3]` (literal 3 ignores both rebinds) and 6 block rows with `spent≈2.00s` (the watchdog's 2s mark, not the 1.0s budget, ended the call; `outcome=returned` or a downstream error after the kill). Cause: the literal timeout survives past the budget until the watchdog fires. Weakness noted: `qa-record-read-failure` reports `outcome=timeout, spent=2.0027`; it fails the `spent<1.5` bound for the right reason but the `timeout` outcome at 2.0s with literal 3 is not individually explained by the receipt. The containment row stays `ok` on red, as designed (subject-independent).
- Both SCs have exact-base fail-first. SC-01 additionally agrees with c0's independent exact-base gate reproduction (1 FAIL).

## Matrix
`change_type: bugfix`; `unit when touches_runtime_code` fires (validate-digest.py is runtime code). Required/observed: `integration` satisfied (the BRIEF's declared kind; named tests 15 `[bug2253]` rows; kind suite green in supplied full receipt); `unit` **missing** — no `tests/unit` file exercises the changed branch and T-01's file set excludes `tests/unit/`. Integration does not substitute (P-04). `functional`, `eval` excluded; `locally_run` kinds not on the changed detect surface. `matrix_ok: false` (truthful). Per assignment this is **advisory, non-blocking for T-01**; the validator cannot pair `false` with PASS, so the verdict routes up as ESCALATE for an operator ruling (extend T-01 to a unit file, or rule that the integration kind covers the unit leg), not as dev rework.

## Coverage gaps
- Unit-kind coverage of the gate branch (advisory, outside T-01's files).
- Phase 1 expectations (BRIEF-only): default 30 and two distinct budgets at all six sites — covered; real blocked subprocess bounded — covered; independent watchdog on a missing timeout — covered; all three SC-02 expectations and both SC-01 clauses have tests.

## Pin
Pinned checkout removed on return. No source or test changed by me.

## Principles applied
Build the Lever (read leaf not separately opened; cited by use only via the verbatim verify): none claimed beyond running the shipped lever unchanged. Absence, subject and mutant (harness-code-review): SC-02 reds are bound to the literal-3 mutant at exact-base production files; the missing-timeout-with-late-start mutant is covered by the polling watchdog and containment case (no separate mutation run executed by me).
