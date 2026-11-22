# BUG-2253 final goalcheck — PASS

Both approved perspectives are discharged at review pin `3aa17de30917ca7eee9d5edb6ebc944e6dc45236`, base `3dd8bb677bb2936361e3952030fc24f15bf9afc6`; later record-only `d21cf97f` excluded. T-01 traces to both SCs. No new must-fix or approval request.

- **PASS / met — SC-01 (operator).** Pinned `.claude/skills/harness/bin/validate-digest.py#_is_failed_file_line` only adds header names to `headed`; PASS, later headers and closes never remove them. Thus `PASS outer.py` and `PASS later.py` cannot suppress the genuine FAIL lines. `_run_pool_mutated_indexes` retains note-adjacent MUTATED entries; `_print_independent_run` preserves ordered duplicates, conditional heading and the existing last-20-line tail; refusal remains 2. Pinned `tests/integration/test-validate-digest.py:6435–6461` carries both same-name PASS echoes and tail-only fallback. Supplied `notes/receipts/red-c4.{txt,stdout}` shows buried/echo cases fail on exact-base gate; `discriminate-c4.{txt,stdout}` shows only the echo case fails on cycle-2 gate b228c3a2 (MUTATED survives but both genuine FAILs disappear); `green-c4.{txt,stdout}` shows all three diagnostic rows pass on 3c6fb908.
- **PASS / met — SC-02 (code maintainer).** Pinned test file defines the shared 30-second budget at line 1030 and uses it at all six sites (3033, 3066, 3286, 3288, 3316, 3318). Behavioral assertions at 6542–6678 observe 30/0.05/0.10 per site, exercise real blocked-helper timeout handling at a selected 1-second budget with <1.5-second bound and readiness, and independently kill direct children from 2 seconds without requiring readiness. Delayed/never-ready controls require kill before readiness and <5 seconds. Supplied red-c4 shows all six observed-base rows report [3,3,3] and all six real-block rows fail; green-c4 shows all twelve plus both containment controls pass. discriminate-c4 also retains these passes; it does not prove old-watchdog failure.

## Evidence boundary

Read-only source/evidence inspection only: no suites, builds, lints or probes executed. Direct pinned diff comparison found no differences between executed fix `3c6fb9084534be85542621334f97c7e1a55fbbdd` and review pin for the gate, test file and canonical-reader inventory; this permits evidence transfer, not a claim of execution at the pin. Supplied green-c4 reports literal T-01 command `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases`, exit 0 in 10.82s (17 passing rows), and full test-file exit 0 in 23.17s; full stdout ends ALL PASSED. Red uses final regressions over exact-base production, reconstructing the six original timeout literals and removing the new constant; it records 14 failures, not a claim that base originally contained these tests. Whole integration-kind compatibility is not established by one full file. Main-supplied code-grade exit 0 / PASSING 29 / no FAIL is supplied evidence, not my execution or SC proof.

## Findings and scoped-out census

- **substance / high, resolved:** prior same-name captured PASS diagnosis loss; repaired by the no-pairing invariant and discriminated by the c4 echo row.
- **substance / low, accepted advisory:** echoed FAIL for an already-headed filename may be over-listed. Operator explicitly accepts this cost in round 3; not reopened.
- **substance / med, out-of-scope advisory:** unit-kind coverage remains absent, matrix false, separately tracked as #2281. Integration evidence is not relabeled unit.
- **substance / info, out-of-scope advisory:** existing runner-launch fail-open policy remains unchanged.

PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent as declared; no substitute guidance invented. Open questions: none.
