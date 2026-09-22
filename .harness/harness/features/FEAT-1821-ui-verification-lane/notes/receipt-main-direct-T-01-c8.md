# Receipt — T-01 round c8 (main-session-direct; operator ruling notes/answers-validate-c7.md) — 2026-09-19

## V7-01 — gate false-positive on manifest-driven specs
Cause: `spec_titles()` greps `test('<literal>')`; the lane's specs register `test(check.spec_title, …)` from the manifest, so a client-package change reported eleven titles absent.
Fix: a title is present when a spec names it literally OR the bundle carries an executed record under that exact title with screenshot evidence (`_executed_titles`). Literal grep retained for the no-bundle case.
Proof: `ui_contract.py gate … --changed client/src/tiles.tsx` against the committed FEAT-1821-initial-red bundle at 153909c7 → titles reported absent: **0**; non-RED reasons: **0** (was 11 absent).
Test: `test_client_package_change_requires_every_spec_title` rewritten — manifest-driven spec + executed records PASS; a title missing from BOTH source and bundle is refused by name; a literal-only title satisfies the rule; a change outside the package does not invoke it.

## V7-02 — fail-first per SC, reconstructed against the real pre-fix trees
Today's `tests/unit/test-ui-verification-contract.py` run unchanged against each tree:

| Tree | Result |
|---|---|
| pre-T-01 (`624eb59a^`, module absent) | `ModuleNotFoundError: No module named 'ui_contract'` — every case red |
| pre-c7 (`9adb6c58`) | FAIL: test_gate_enforces_predicates_and_inspection_evidence; test_inspection_record_with_failed_setup_is_not_evidence; test_client_package_change_requires_every_spec_title |
| pre-c8 (`0af450c5`) | FAIL: test_client_package_change_requires_every_spec_title |
| c8 (this commit) | 24/24 OK |

SC → discharging test (all red in the pre-T-01 tree; c7/c8 rows above show the later mutants red at their own pre-fix commits):
- SC-05 contract shape/duplicates/expect → CheckContract.* (10 cases), GateEvidence.test_gate_enforces_predicates_and_inspection_evidence
- SC-06 results schema/identity/WebP/accounting → test_identity_and_pin, test_results_cannot_bring_their_own_check_list, test_screenshot_evidence_must_be_real_webp, test_accounting_and_status_consistency, test_inspection_manifest_entries_need_their_screenshot, test_inspection_record_with_failed_setup_is_not_evidence
- SC-10 runner/contract blocking → test_missing_runner_or_contract_blocks, test_missing_results_file, test-suite-layout.py case 12 (ui kind active, cmd, detect)
- SC-11 client change requires whole table → test_client_package_change_requires_every_spec_title
- SC-02 / SC-03 / SC-04 are the runner's (T-03/T-06/T-13): their red-before is the lane's own T-06 record (22 red at 153909c7) and T-13's seven two-stage probes; not T-01's to pin.

code-grade.py ui_contract.py: 0 records below bar 4.
