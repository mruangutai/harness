# Code review — BUG-1898 c3

PASS. The canonical two-stage review of `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..6bfc21e3ccdf78eb86cdd0eb250067348d887096`, with focused comparison `4942950a83c1895d85922f7cd9e9cfd41e28daf8..6bfc21e3ccdf78eb86cdd0eb250067348d887096`, finds no spec violation or code-quality defect.

## Stage 1 — spec compliance

The focused executable delta is confined to `tests/integration/test-suite-claim-preservation.py:34-40,113-120` and serves SC-01/T-03/T-04 by closing F-QA-01. The oracle extracts the complete set of lines beginning with the exact `FAIL  [bug1898] ` prefix and requires set equality with exactly `after the child settles the identical yield passes` and `and releases only the parent`. The retained test passed against the real validator suite and persona-release mutant. Independent negative controls showed rejection for (1) only the first required label and (2) the first required label plus a different replacement label. The four relocated-copy schema failures (`drifted key spelling is caught`, `enum near-miss is caught, not normalized`, `code reviewer omission of code_grade is rejected`, and `code_grade's missing-field hint names the four legal values, not the list wording`) are emitted by the ordinary case runner, not `_b1898_check` (`tests/integration/test-validate-digest.py:765,778,2934,2951,5674-5675,5880-5897`), so they lack the `[bug1898]` prefix and neither satisfy nor spoil the exact-set comparison.

No production path changed after the c2 pin. F-01 remains closed: the focused delta does not alter strict registry reads, held-child refusal, or exact release. F-02 remains closed: canonical grading reports `_registry_errand` 4, `_settle_in` 5, and `_release_own` 5. The remaining SC-02 through SC-06 and SC-08 obligations have no executable regression in the focused delta; SC-01's permanent mutation proof is now exact. SC-07 remains `pending_operator_gate`; it was not run and is not a panel failure.

## Stage 2 — code quality

The exact-set implementation is fail-closed: any missing required label, any additional prefixed label, or any substituted prefixed label rejects. Unprefixed unrelated failures cannot create acceptance and cannot contaminate the target set. The changed test functions grade 4 or 5 against the test-code bar of 3; the full canonical Python grade reports 127 passing records and no severity or grade-2 record. No stale-path, silent-acceptance, tautological-control, or fail-open finding remains.

## Evidence

- `python3 tests/integration/test-suite-claim-preservation.py` — PASS: seeded-persona preservation, pinned suite, byte-identical strangers, and exact parent-settlement mutant oracle; `0 failure(s)`.
- Two injected-output negative controls — singleton: REJECTED; different replacement label: REJECTED.
- `code-grade.py --base a4d72e7f... --head 6bfc21e3...` — `PASSING: 127`, no failures.
- No live OMP, formatter, linter, or unrelated suite ran. No scratch checkout was created. The focused test and negative-control invocations created only their own temporary copied-bin directories and removed them in `finally`; no scratch material remains.

## Principles applied

None.
