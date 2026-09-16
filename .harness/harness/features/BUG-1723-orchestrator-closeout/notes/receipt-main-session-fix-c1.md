# Fix c1 — BUG-1723 (validate c0 FAIL: V-01/V-02/V-03) — by Main, main-session-direct

- V-01 (T-02, high): the terminal-station downgrade in INV-43 is removed; a retrospective succession is a VIOLATION at `done` as at `review` (SC-03/D-02). `case_inv43_scope` (43.j) now expects the violation at both stations. Live consequence: the two BUG-285-canonical-reader retrospective successions AND BUG-1723's own plan→build succession (appended by the validate orchestrator at 05:39Z, after validate-validator started) now report as violations — honest census, not noise.
- V-02 (T-01, med): `CloseRunTest` gains the judgement-stage refusal (241-char reason → schema code, run-end retained, no judgement, no spend line) and the spend-stage seam (`_stage("spend", …)` over an authority exiting 3 names the stage and exits 3). A data-driven spend refusal is unreachable after the earlier stages' validated writes; the test says so.
- V-03 (T-03): SKILL.md step 6 names `code_grade: n_a` as the recorded field; `test-check-state-plans.py`'s INV-6 producer binding matches the step by its lead words rather than the whole heading.

Verify: `python3 tests/unit/test-feature-record.py` OK (48); `python3 tests/integration/test-check-state-feat59.py` exit 0; `run-unit-tests.py --kind integration` PASS (72 files).
