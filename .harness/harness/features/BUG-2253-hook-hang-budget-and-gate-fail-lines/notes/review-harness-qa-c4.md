# QA c4 — BUG-2253 at pin 645febc8 (run 2026-11-21-04-validate-validator)

**BLUF:** Both rework-2 closures hold. Literal T-01 verify at a managed pin: 17 cases, exit 0, 11.03s, no FAIL rows, no surviving children. Both c3 counterexamples now pass. Only the out-of-scope unit-kind floor (#2281) keeps matrix_ok false, so the contract forbids PASS: ESCALATE, not a masked PASS or a defect FAIL.

## Phase 1 (from BRIEF/plan only)
SC-01: buried FAIL/MUTATED above 20 passing lines, in order, heading once, tail unchanged, tail-only fallback, refusal code unchanged, red at exact base gate. SC-02: six sites observe 30 default and two rebound budgets; six real blocked probes time out within budget+tolerance; missing timeout fails under an independent watchdog; delayed/never-ready child contained. Plus the two c3 counterexamples. Gaps vs Phase 1: none in scope; unit kind (below).

## Code equality
`git diff --quiet b228c3a2 645febc8 -- . ':!.harness'` -> EQUAL_CODE (measured; the diff is notes/receipts only). Pin HEAD verified 645febc8, clean.

## Verify
`python3 tests/integration/test-validate-digest.py --only run_bug2253_cases` in the managed pin (`.claude/worktrees/.pins/...--harness-qa`): 17 ok / 0 FAIL, exit 0, 11.03s (receipt green-c3: 10.89s). pgrep afterwards: no blocker or probe children. Primary checkout untouched.

## Closures
- SC-01 echo: `_bug2253_echoed_header_case` ok. Close pops to the matching header; MUTATED taken above run_pool's note (`validate-digest.py:2499-2535`). Non-mutating probes (30s bound): `FAIL a.py` after echoed headers kept; spaced MUTATED kept; MUTATED without the note not taken.
- SC-02 watchdog: kills all direct children from 2s, no handshake (`test-validate-digest.py:6578`). Late (2.5s) and never-ready (3600s) rows both exit -9 before readiness, under 5s.

## Fail-first provenance
- red-c3 (exact base 3dd8bb67 gate, production byte-identical; test file with six sites reverted to timeout=3 and constant removed): 14 FAIL, exit 1, 17.11s. Natural red for SC-01 buried+echoed; budget rows semantic (observed 3, not an import error). Tier: reconstructed-subject red.
- discriminate-c3 (6cbdc417 gate, final tests): exit 1, only the echoed-header case fails.
- green-c3: b228c3a2 clean; group exit 0 10.89s; full file exit 0 22.59s (the file, NOT the full integration kind). Discovery: file matches `tests/integration/test-*.py`.
- Qualification: containment rows and the quiet case pass at base by design (test infrastructure / retained fallback), not claimed red.

## Advisories (not blockers)
1. Low, residual positional ambiguity: a failing file whose output echoes `PASS <its own name>` loses its FAIL line (probe returned []); a balanced echoed `FAIL fx.py` inside a passing file is over-reported. Tail and refusal unchanged; a fix needs a producer format change (out of scope).
2. Watchdog kills every direct child of the test process; safe while probes run sequentially.
3. Unit-kind coverage (#2281) and runner-launch fail-open: out of scope, unchanged.

## Contract tension (exposed)
Matrix `bugfix` + `touches_runtime_code` requires unit; none covers T-01, so `missing`. The operator ruled it out of this patch (#2281). The qa contract rejects PASS with matrix_ok false, and `missing` implies FAIL. Reported truthfully as ESCALATE; every in-scope result is green. Integration is satisfied for the named 17-case file scope only; the full integration kind was not rerun here.
