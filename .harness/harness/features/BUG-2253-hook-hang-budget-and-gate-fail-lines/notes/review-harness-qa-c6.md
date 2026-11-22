# QA c6 — regate, pin 3aa17de3 (run 2026-11-22-05-validate-validator)

**BLUF:** The c5 must_fix is closed and both SCs hold, but the matrix `unit` row is honestly `missing` (operator-disposed, #2281). I run the literal T-01 verify once at the managed pin: 17 ok, 0 FAIL, exit 0, 11.42s, empty stderr. The verdict is FAIL only because of the strict QA contract (see Matrix truth).

## Phase 1 (from BRIEF/plan only)
SC-01: a nonzero re-run lists every FAIL/MUTATED file before the tail, including buried ones. It keeps a tail-only fallback and leaves refusal status unchanged. SC-02: six sites at 30 by default, two distinct rebound budgets, a real block times out within budget plus tolerance, and an independent watchdog catches a missing timeout. Fail-first against the exact base. No Phase 1 expectation lacks a test.

## Measured by me
- Pin: managed `pinned-checkout.py` tree, HEAD 3aa17de3, clean. Verify env had HARNESS_AGENT_TYPE and project-root vars unset.
- Code equivalence: `git diff --stat 3c6fb908 3aa17de3 -- .claude tests` is empty. Every receipt on 3c6fb908 therefore binds the pin's code.
- Source read at the pin: `_is_failed_file_line` (validate-digest.py:2513) never un-names a headed file. MUTATED indexes are taken only directly above the run_pool note (2527). `_bug2253_echoed_header_case` (test-validate-digest.py:6435) carries `PASS outer.py` and `PASS later.py` before the genuine FAILs and expects both to be listed.
- Six-site and watchdog coverage retained: 6 budget cases, 6 block cases and 2 watchdog self-proofs, all ok.

## Supplied evidence (not re-executed)
- red-c4: exact base 3dd8bb67 gate, tests from the fix with six sites reverted to timeout=3: 14 FAIL, exit 1. Natural red on a reconstructed subject.
- discriminate-c4: cycle-2 gate b228c3a2 under the final tests, exit 1. Only the echo case fails; this is the natural red for the c5 must_fix.
- green-c4 and green-c4-full: 3c6fb908 group and whole test file, exit 0.
- Main-session `code-grade.py` (29 PASSING, no FAIL rows): supplied, not mine.

## Matrix truth
`integration` is satisfied: `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases`, 17 named cases. `unit` (bugfix floor) is `missing`: no unit test exercises this change, and integration is not counted as unit. The operator ruled this out of scope (#2281). Contract constraint: the validator rejects PASS with `matrix_ok: false`, and `matrix_ok: true` needs every always kind `satisfied`. I report `matrix_ok: false` and VERDICT FAIL rather than fabricate `true`. The orchestrator or operator must apply the scope ruling (waive or override); I do not.

## Scoped-out census (advisory, none must_fix)
- Over-listing an echoed `FAIL <name>` whose name has a header: ACCEPTED Low (operator).
- Unit kind missing: #2281, out of scope.
- Runner-launch fail-open: out of scope, pre-existing.

## Fail-first
SC-01 (buried, echoed, same-name PASS) and SC-02 (six sites): red-c4 and discriminate-c4. Tier: natural red on a reconstructed subject. Only my own evidence examined the c4 fix after c5 raised the finding, so no second-reviewer independence applies to my run.
