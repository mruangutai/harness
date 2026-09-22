# Receipt — T-14 (main-session-direct): replayable traces contract + SC-04 rule — 2026-09-19

## Fail-first (red before fix), verbatim — the fail-first run, nonzero exit
Pre-fix tree: 102cd2d7 (ui_contract.py without `### Traces` parsing, trace enforcement, or the pixel-baseline rule); test file extended first.
Command: `python3 tests/unit/test-ui-verification-contract.py` — nonzero exit.
```
ERROR: test_traces_table_normalizes_and_rejects_invalid_rows (__main__.CheckContract.test_traces_table_normalizes_and_rejects_invalid_rows)
FAIL: test_to_have_screenshot_requires_pixel_baseline_opt_in (__main__.GateEvidence.test_to_have_screenshot_requires_pixel_baseline_opt_in)
FAIL: test_traced_results_require_replayable_zip_inside_run_ui (__main__.GateEvidence.test_traced_results_require_replayable_zip_inside_run_ui)
Ran 27 tests in 0.146s
FAILED (failures=2, errors=1)
```

## Post-fix green
```
Ran 27 tests in 0.162s

OK
```
code-grade.py ui_contract.py: 43 records, 0 below bar 4. `.gitignore` probe from T-14's verify: published `runs/<id>/ui/traces/*.zip` tracked; `runs/<id>/ui/test-results/**` and client `test-results/**` ignored.

## SC mapping
- **SC-04** (pixel baselines opt-in) → `test_to_have_screenshot_requires_pixel_baseline_opt_in`: mutant inserts `toHaveScreenshot(` into a package spec with no `pixel-baseline` row → gate FAIL naming the file; positive case adds an opting-in row and its records → PASS. **This is gate enforcement over spec source; it does not change, fix or describe any FEAT-53 production behaviour.** FEAT-53's own predicate RED is untouched.
- SC-05 (Checks contract) → `test_traces_table_normalizes_and_rejects_invalid_rows`: ordered `traced_check_ids`; malformed columns, duplicate id, unlisted id refused.
- SC-02 / SC-06 (evidence and results contract) → `test_traced_results_require_replayable_zip_inside_run_ui`: valid ZIP traces PASS; absent, absolute, escaping, outside ui/, empty, non-ZIP, and trace-on-untraced-check each refused by check@project.
- SC-10 (QA gate blocks on contract failures) → the above reasons surface through `ui_contract.py gate`, which QA runs.
No FEAT-53 check id is hardcoded in ui_contract.py; the Traces table is the only authority.

## V9-01 (validate c9) — `_is_zip` accepted any `PK\x03\x04` prefix
fail-first at c5fab956 with the new mutant (`PK\x03\x04` + 64 bytes of 0xFF): `python3 tests/unit/test-ui-verification-contract.py` → nonzero:
```
FAIL: test_traced_results_require_replayable_zip_inside_run_ui (__main__.GateEvidence.test_traced_results_require_replayable_zip_inside_run_ui)
FAILED (failures=1)
```
Fix: `zipfile.is_zipfile` (central directory must parse). Post-fix: 27/27 OK; grade 0 below bar; the 8 real traces in FEAT-1821-initial-red still produce 0 trace reasons. No FEAT-53 production/dist change.
