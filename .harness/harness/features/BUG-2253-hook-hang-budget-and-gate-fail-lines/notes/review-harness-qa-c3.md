# QA review c3 — BUG-2253 T-01 (SC-01, SC-02) — pin 2e96b583

BLUF: **FAIL. My c2 closure assurance ("both SCs proven, no task defect") is WITHDRAWN.** Both code-reviewer c2 counterexamples are CONFIRMED against the pin; neither has a test, so each is a Phase-1 coverage gap and a real acceptance hole. c2 is left unchanged; this note supersedes its verdict. The c2 ESCALATE rested on the advisory `unit` floor, which is not a gate; the verdict is now driven by in-scope findings only.

## Evidence basis
- Pin `2e96b583`; production files and test file identical to the reviewed fix `6cbdc417` (c2: no non-`.harness/` diff). I did NOT rerun the verify or the broad suite; the measured c2 result stands: `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases` exit 0, 15 `ok [bug2253]` rows, 0 FAIL, 9.43s.
- Two bounded, non-mutating probes run once from /tmp importing the pin's modules (no repo file written; probe 2 ended in 5.2s).

## Finding 1 (SC-01, substance/high) — CONFIRMED, executed probe
`_run_pool_file_lines` (`validate-digest.py` ~2494-2518) pushes every header-shaped line; `run_pool._emit_result` prints captured child output unescaped, so a child echoing `----- fixture.py (exit 1, 0.10s) -----` leaves an unmatched entry on the stack top. Probe stream: outer header `test-a.py`, echoed header `fixture.py`, genuine `FAIL test-a.py`, three PASS blocks, final `MUTATED notes/my file.md`. Result: `named == []` — the genuine FAIL is not reported (footer compared only to stack top `fixture.py`) and the later MUTATED is treated as in-block. With >20 later lines the operator loses both diagnoses, contradicting SC-01 "every FAIL/MUTATED ... before the tail". No test in the 15 rows feeds an unmatched header-shaped payload line (the buried case only injects non-header `FAIL`/`MUTATED`/`FAILED-NOT-A-FILE-LINE` echoes). Realism is modest (child must print run_pool's header shape) but the SC and run_pool's unescaped producer admit it.

## Finding 2 (SC-02, substance/high) — CONFIRMED as a bound on the watchdog; scope qualified
`_bug2253_watchdog` (test ~6551-6576) can only kill after its pid file exists. Probe 2: blocker with `BUG2253_DELAY=5` under `subprocess.run(timeout=30)` and the real watchdog (2s start): child killed at 5.2s, exit -9, i.e. the 2s deadline did not fire — nothing bounds a pre-readiness stall; with `BUG2253_DELAY=60` and a helper whose timeout is removed, the probe blocks ~60s (permanently if readiness never occurs). The containment row (2.5s delay) only proves eventual post-readiness kill.
Qualification (refutes any broader claim): with the fixture as shipped (`BUG2253_DELAY` unset → child writes its pid in milliseconds), a site with a missing/ignored timeout IS caught: watchdog kills at ~2s → `outcome=returned` → row fails; c2's red run shows exactly this (`spent≈2.00s`). So the hang requires delayed/absent readiness (extreme load, or inherited `BUG2253_DELAY`). SC-02 text "must fail under an independent watchdog, not pass or hang the regression" is unconditional, hence a gap against its letter; practical exposure is the loaded-host case the feature targets.

## fail_first
- Existing (retained, c2): SC-01 buried case 1 FAIL and SC-02 six budget rows `[3,3,3]` + six block rows `spent≈2.00s` at exact base `3dd8bb67` — `notes/receipts/red-c2.txt`. Unexplained: `qa-record-read-failure` row `outcome=timeout, spent=2.0027` on red. Assurance note only; it fails for the right bound and does not alter failure causality.
- New counterexamples: no regression test exists, so no test-bound fail-first. Evidence is the executed probes above (present-state, tier: reasoning+probe, not a natural RED).

## Matrix
`unit when touches_runtime_code` remains missing (T-01 files exclude `tests/unit/`); integration does not substitute (P-04); `matrix_ok: false` truthful. Per dispatch this is advisory/nonblocking and is retained only as a nonblocking question; it is NOT a reason for this FAIL. Contract tension reported, not normalized: the validator forbids `matrix_ok:false` + PASS, so a PASS would have been impossible even with no in-scope finding; here FAIL stands on findings 1-2 independently of that.

## Coverage gaps
- SC-01: header-shaped unmatched payload line inside a block before a genuine FAIL/MUTATED.
- SC-02: missing-timeout site with delayed/never-ready child; no readiness-independent deadline in the watchdog.
- Unit kind (advisory).

## Pin
No pinned checkout created (read-only against the worktree). No source/test changes by me.
