# FAIL — SC-01 still loses a genuine file verdict after an echoed matching PASS

Reviewed `3dd8bb677bb2936361e3952030fc24f15bf9afc6..645febc89615f9a508a5cc66122a02a80ddabaac`, not HEAD or record-only bef1d148. Full commit list and immutable diff inspected; no human-tagged commits or dirty files observed. Read-only source review; no tests, probes or grader executed by this reader.

## Stage 1 — spec compliance

**High · substance · T-01 / SC-01: captured PASS can consume the genuine enclosing header.** At `validate-digest.py:2521–2525`, either verdict deletes the matching header immediately. Concrete valid producer stream: `----- outer.py (exit 1, 0.30s) -----`, captured child output `PASS outer.py`, actual producer footer `FAIL outer.py`, then over 20 passing lines. `run_pool.py:107–113` prints the captured body verbatim. The echoed PASS removes `outer.py` from the stack; the genuine FAIL finds no header and is discarded. No FAIL heading/file diagnosis survives, and the tail no longer contains the failed file. This is a REASONED counterexample, not an executed probe. The new echoed-header test (`test-validate-digest.py`, `_bug2253_echoed_header_case`) never supplies an echoed closing verdict matching the enclosing file. Preserve genuine verdicts even when captured text resembles a matching close; cover that counterexample. Refusal itself still exits 2: the defect is silent diagnostic loss, not policy fail-open.

### Prior c2 must_fix disposition

- **SC-01: exact unmatched-header counterexample closed; diagnostic-loss obligation retained.** Matching closes now discard unmatched echoed headers (`validate-digest.py:2512–2525`); mutations are recovered immediately above the producer note regardless of stack depth (:2528–2536). The failing/pass-block echoes, later FAIL and spaced MUTATED are covered. The matching-PASS scenario above still violates the same SC.
- **SC-02: closed by inspection and supplied evidence.** Watchdog enumerates direct children and kills them from its 2s deadline without readiness (:6570–6605); actual helpers directly launch the blocker (:1062–1074,3411–3416), and subprocess.run reaps it. Block rows still require readiness (:6640–6649). Delayed and never-ready children under a 60s timeout must return -9 before readiness within 5s (:6653–6675). No remaining readiness-dependent termination authority was found.
- Shared default 30 and all six replacements remain present, with FIFO/symlink/deep-JSON/load-headroom rationale. Plan T-01 verify is exactly `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases`; QA executes it. Neither SC is marked `verify: inspection`.

Supplied immutable `red-c3.*`, `discriminate-c3.*`, `green-c3.*` record exact-base 14 failures, cycle-1 echoed-header discrimination, and fix selected/full-file green. Python diff b228c3a2..pin is empty. These do not exercise the counterexample above. Full-file green is not complete integration-kind coverage. Product docs were recorded absent; no substitute guidance invented. No build amendments were supplied in the intake digest.

## Stage 2

Withheld because Stage 1 fails. Supplied main grading base..b228c3a2: exit 0, PASSING:29, no FAIL; unchanged Python through this pin supports `code_grade: pass`. This is supplied evidence, not reader execution or quality clearance.

## Principles applied

Model the Domain: a matching textual PASS is not proof that the producer closed its block when captured child output is emitted verbatim; the stack still confuses payload with framing.

## Open questions

None. Unit-kind #2281 and pre-existing runner-launch fail-open remain settled out-of-scope operator advisories, not blockers. QA owns any bounded confirmation of the counterexample and final literal verification.
