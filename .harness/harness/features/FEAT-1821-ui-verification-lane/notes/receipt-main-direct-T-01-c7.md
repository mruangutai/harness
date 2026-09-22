# Receipt — T-01 fix round c7 (main-session-direct) — 2026-09-18

## Findings addressed
- code-reviewer F-01 (high): `gate()` loaded the manifest without `require_predicates` / `require_inspection_evidence`.
- reviewer: inspection records with failed setup (`status: evidence`, non-empty `errors`) were accepted as evidence.
- code grade: `_table_after` 3, `_inspection_evidence` 1, `gate` 1, `_screenshot_reasons` 3 (plus `load_manifest` 2, `main` 2).
- qa: no pinned fail-first receipt for the SC-05/06/10/11 mutants.

## Fail-first (red before fix), verbatim
```
FAIL: test_gate_enforces_predicates_and_inspection_evidence (__main__.GateEvidence.test_gate_enforces_predicates_and_inspection_evidence)
FAIL: test_inspection_record_with_failed_setup_is_not_evidence (__main__.GateEvidence.test_inspection_record_with_failed_setup_is_not_evidence)
Ran 24 tests in 0.151s
FAILED (failures=2)
```
The original T-01 suite was also run red before the module existed (ModuleNotFoundError: ui_contract), at 624eb59a's parent; not pinned then, pinned here.

## Green after fix
```
Ran 24 tests in 0.137s

OK
```
code-grade.py ui_contract.py: 37 records, 0 below bar 4.

## Effect on the committed RED bundle (FEAT-1821-initial-red at 0ef52107)
Gate at its own served_bundle_commit: FAIL with 23 reasons — 18 predicate failures, 4 "inspection setup failed" (VIS-DENSITY / VIS-PROTOTYPE at both projects, newly refused), 1 summary. Structural (non-predicate, non-setup) reasons: 0. The record remains an honest RED; no FEAT-53 production code touched.
