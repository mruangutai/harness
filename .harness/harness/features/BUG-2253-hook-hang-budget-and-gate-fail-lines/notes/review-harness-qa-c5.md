# QA c5 — scope reassessment, pin 645febc8 (run 2026-11-21-04-validate-validator)

**BLUF:** FAIL, in scope. My own c4 probe (captured `PASS <own name>` in a failing file -> named list `[]`) is a genuine SC-01 diagnostic loss: SC-01 promises every genuine FAIL line is surfaced. c4's "advisory / needs producer format change (out of scope)" is RETRACTED. No evidence shows a producer-format change is the only remedy, and a gate-side fix is not ruled out. This c5 reran nothing and changed nothing.

## Retained vs retracted from c4
- RETRACTED: advisory 1's classification as Low / out of scope and its "a fix needs a producer format change" claim (unsupported). The failing-file half is now an in-scope SC-01 defect, matching code c4 (`review-harness-code-reviewer-c4.md`) and PM c4 (`...goalcheck-validate-c4.md`), reached independently on my own measurement.
- RETAINED unchanged: Both rework-2 closures (echoed unmatched headers; SC-02 pre-readiness watchdog) held. Literal verify `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases` at the pin: 17 ok / 0 FAIL, exit 0, 11.03s, no surviving children (c4 execution; NOT rerun). Code equality b228c3a2..645febc8 EQUAL_CODE (c4 measured).
- RETAINED: the c4 green is honest but silent on this scenario; the 17 cases contain no case with a captured same-name PASS before the genuine FAIL, so green does not bear on it.
- Unit kind (#2281) and runner-launch fail-open: still out of scope per operator. The matrix `missing` unit row remains a contract tension but no longer needs to carry the verdict: a real SC-01 defect permits FAIL on its own, and unit absence is NOT claimed as a blocker.

## Evidence classes
- EXECUTED (c4, not rerun): one bounded non-mutating probe of the pinned gate parser with a failing-file block whose own output echoes `PASS <its own file name>` before its genuine `FAIL <name>`, then more than 20 passing lines. Result: named-file list `[]` (genuine FAIL absent from the diagnosis). Limitation: the exact probe bytes were not retained in the c4 note or receipts; I do not reconstruct them here. Also executed in c4: `FAIL a.py` after echoed headers kept; spaced `MUTATED` kept; `MUTATED` without the producer note not taken (30s bound).
- REASONED (not executed, from code c4 and PM c4): stream `----- outer.py (exit 1, 0.30s) -----`, captured `PASS outer.py`, producer `FAIL outer.py`, over 20 passing lines; `validate-digest.py:2521-2525` pops on either verdict, so the later FAIL finds no header. Producer prints captured body verbatim (`run_pool.py:107-113`). The match with my executed probe is the same mechanism.

## Uncovered expectation (Phase 1 gap)
SC-01 literal: every genuine FAIL file line is named above the tail, in order. Expected test: a failing file whose captured output contains `PASS <same name>` (and symmetric `FAIL`-first variants) must still yield its FAIL. No test covers it: `_bug2253_echoed_header_case` echoes only unmatched header names. Listed as coverage_gap.

## Separate advisory (retained, Low)
The balanced echoed `FAIL fx.py` inside a PASSing file is over-reported (executed in c4). Diagnostic accuracy, distinct from the loss above. No claim that a global framing is impossible; unproven either way.

## Fail-first provenance (preserved from c4)
- red-c3 (exact base 3dd8bb67 gate, six sites reverted): 14 FAIL, exit 1, 17.11s; `notes/receipts/red-c3.stdout`. Natural red for SC-01 buried and echoed; budget rows semantic. Tier: reconstructed-subject red.
- discriminate-c3 (6cbdc417 gate, final tests): exit 1, only echoed-header case fails; `notes/receipts/discriminate-c3.stdout`.
- green-c3 (b228c3a2): group exit 0 10.89s; full file exit 0 22.59s (file, not whole integration kind).
- These cover the prior defects only. For the same-name PASS scenario there is NO red-to-green test: no fail-first exists, and none may be claimed.

## Open
The fix is the dev's (gate-side parse of same-name PASS/FAIL, e.g. consult header exit status); route to the owning dev with a regression test.
