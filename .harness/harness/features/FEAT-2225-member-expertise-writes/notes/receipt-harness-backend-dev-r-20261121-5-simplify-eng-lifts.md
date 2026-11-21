# Receipt — harness-backend-dev — FEAT-2225 T-01 grade-debt lift (run r-20261121-5-simplify-eng)

**BLUF.** All 24 below-bar functions were refactored in the three owned paths, behavior-preserving, with nothing run (builder phase; no tests, graders or linters executed). Static `check(...)` counts are unchanged (unit 119 → 119, integration 255 → 255, asserts 0 → 0). Grades are PREDICTED from the `code_grade.py` counter rules, not measured. Uncommitted, per dispatch.

## T-01 verify (verbatim from plan.yaml:160; cross-checked, NOT RUN)

```
python3 tests/unit/test-expertise-ops.py && python3 tests/integration/test-expertise-merge.py
```

Output: none — deliberately not executed in this wave.

## Counting expression (same before and after)

`ast.walk` over the file; `check` = nodes `ast.Call` with `func` an `ast.Name` whose `id == 'check'`; `assert` = `ast.Assert` nodes. The suites use `check(name, ok, detail)` appending to `RESULTS`, never `assert`.

|File|check calls before|after|ast.Assert before|after|
|---|---|---|---|---|
|tests/unit/test-expertise-ops.py|119|119|0|0|
|tests/integration/test-expertise-merge.py|255|255|0|0|
|.claude/skills/harness/bin/expertise-merge.py|0|0|0|0|

Predicted before measuring, confirmed by the same script after edits (the parse also proves the files are syntactically valid). Every `check` keeps its original label and detail argument; no check was merged, removed or weakened. Runtime tallies (loops multiply) are unmeasured, but no loop was changed.

## Production — .claude/skills/harness/bin/expertise-merge.py

|Target (grade driver)|Lift|
|---|---|
|destination_rel (cyc 9)|`_is_persona`, `_declared_segment` bool helpers; both reused by `_destination_form_ok` and `_validate_receipt_header`|
|_validate_ops (ABC 20.4)|`_parse_recorded_op`, `_record_describes`, `_validate_op_record`|
|_validate_receipt (ABC 20.3)|`_validate_receipt_header` + `_is_text`; check order preserved (shape, persona, feature, runtime_id, parent_id, then batches)|
|member_ops|`_locate` (real root, rel, dest, receipt; shared with verify_receipt), `_reconstructor`, `_member_report`; `os.makedirs(dirname(dest))` moved to the top of `_land_target` (it only runs before `locked_update`, so order is unchanged)|
|verify_receipt|`_require_files`, `_recorded_batches`, `_read_destination`, `_refuse_mismatches`, `_preserved_adds`; reuses `_locate`|
|main|`_add_apply_parser`, `_add_ops_parser`, `_add_member_parser`, `_add_verify_parser`, `_add_replay_parser`; main loops over them|
|replay_feature (cyc 12, grade 2)|`_plan_refusals`, `_plan_mappings`, `_write_plans`; predicted cyc 6, so NO grade-2 reason needed|

- Anchor: `cmd_ops` and its nested `transform` are untouched, so `expertise-merge.py::cmd_ops.transform` (canonical-reader-classification.json:626-630) still resolves; `_decode_json` and `parse_receipt` (the other two anchors, lines 639-655) are untouched. Classification JSON and guards not modified.
- Interfaces unchanged: all public/CLI names, JSON key order of member-ops and verify-receipt results, exit codes and refusal text. `harness_merge.locked_update` is still looked up as a module attribute, so the unit test monkeypatches (u40, u42) still bind.

## Unit — tests/unit/test-expertise-ops.py

|Old|New (all registered in `GUARDED_CASES`)|Checks|
|---|---|---|
|case_u34_replace_drop_originals (9 check sites)|`case_u34_refusals` (4), `case_u34_applies` (3), `case_u34_refused_batch_report` (1 + 1 loop site); fixtures in `u34_fixtures()`, rebuilt fresh per case|9|
|case_u38_supersession_graph (5)|`case_u38_retirement` (2), `case_u38_refused_graphs` (3); `u38_chain`, `u38_refused_graphs` builders|5|
|case_u40_receipt_failure_fails_call (6)|`case_u40_receipt_failure_fails_call` (4: if/else keeps the two original labels), `case_u40_verify_without_receipt` (2); `failed_receipt_tree` contextmanager owns the patch/restore and rmtree|6|
|main|`LEGACY_CASES` (u1..u23, unguarded, same order), `GUARDED_CASES`, `print_results`|0|

`import contextlib` added beside the existing mid-file imports.

## Integration — tests/integration/test-expertise-merge.py

Registration: `SERIAL_CASES` (the 26 pre-existing cases, original order, unguarded) and `POOLED_CASES` (the 13 FEAT-2225 cases, same 4-worker `ThreadPoolExecutor`, `run_guarded`). `case_cap_drift_detector` and `case_contract_drift` gained an ignored `_root` parameter so one loop drives all of them; no other caller exists (grep). Every split phase is called from its original case function, so the pooled registrations and their sequential per-case state are unchanged; phases are never registered separately because the pool would run them concurrently.

|Case (blocking/grade-2)|Phase functions|Checks (before = after)|
|---|---|---|
|case_member_absent_files|`_check_absent_craft_result`, `_check_absent_receipt_header`, `_check_absent_receipt_content`, `_check_absent_receipt_identity`, `_check_absent_repository`|15|
|case_member_destination_boundaries|`_check_boundary_refusals` (+loop), `_check_boundary_symlinked_segment`, `_check_boundary_symlinked_craft`, `_check_boundary_symlink_onto_control`, `_check_boundary_symlinked_legal_tail`, `_check_boundary_nothing_landed`|9|
|case_member_verify|`_verify_fixture`, `_check_verify_final_effect`, `_verify_refusal_cases`+`_check_verify_refusals`, `_check_verify_tampered_file`, `_check_verify_preserved_add`, `_check_verify_invented_application`|9|
|case_replay_collision_and_repeat|`_collision_fixture`, `_collision_first_replay`, `_check_collision_dry_run`, `_check_collision_write`, `_check_collision_repeat`|10|
|case_replay_changed_main_and_cap|`_changed_main_fixture`, `_check_changed_main`, `_check_changed_replace_refusal`, `_cap_fixture`, `_check_cap_overflow`|7|
|case_supersession_flow|`_supersession_fixture` + 11 `_check_supersession_*`/`_supersession_withdraw` phases|25|
|case_replay_evidence_fails_closed|`_evidence_fixture`, `_check_evidence_identity`, `_check_evidence_undecodable_and_restored`, `_check_evidence_missing_pieces`, `_check_evidence_cycle`|7|
|case_member_strict_ops (g2)|`_check_strict_op_keys`, `_check_strict_payloads`, `_check_plain_paths`|8|
|case_member_batches_append (g2)|`_check_batches_receipt`, `_check_batches_counts`, `_check_batches_identity_refusals`|10|
|case_member_refusal_preserves (g2)|`_check_refusal_ops`, `_check_refusal_untouched`, `_check_refusal_cap`|7|
|case_replay_current_pr_selection (g2)|`_selection_fixture` + case body|4|
|case_replay_independent_callers (g2)|`_independent_fixture`, `_check_independent_replace_pair`, `_check_independent_replace_drop`|4|
|_run_all_cases (g2)|tuple-driven loop + pool|0|

Per-case check counts are the original static sites (derived by reading, not measured per function); the file total 255 is measured. Small shared helpers added: `read_rel_if_exists`, `load_receipt_or_stub`, `read_bytes`, `overwrite`, `overwrite_bytes` (replace repeated open/write idioms; `read_bytes` now closes its handle).

## Grade-2 reasons

None claimed. Every flagged grade-2 function was split below the grade-3 test bar / grade-4 production bar by estimate (ABC counted per `_Counter`: Name-store, every Call, conditions). Residual risk: a few phase functions are estimated at ABC 17-22 against a 26 ceiling (tests) / 20 (production: `member_ops` ~17.7, `verify_receipt` ~14, `_recorded_batches`). If the final `code-grade` run reports any function still under bar, name it there; this receipt claims no measured grade.

## Behavior notes for the final verifier

- u34/u38 phases build fixtures fresh per case; the originals shared one set of dicts across their checks. Only matters if `apply_batch` mutates entries (not observed).
- u40's verify phase now builds its own failed-receipt tree instead of reusing the first phase's tree; the state it verifies against is identical (target written, receipt write failed).
- Intentionally unchanged: changelog/docs/DECISIONS/SPEC. Behavior and interfaces are unchanged, so no semantic doc update exists to make.
- Unrelated dirty paths in `git status` (feature.json, sibling reader receipts) are other agents' work, untouched.

## Principles applied

Delete First (`references/delete-first.md`): not read this run, so not cited. Code-risk grading (`harness-code-risk-grading` skill): helpers are extracted per responsibility, graded independently by estimate, no pass-through wrappers (each new helper owns a decision, a fixture or a refusal).

## Exact next steps (final stage, not mine)

1. `python3 .claude/skills/harness/bin/code-grade.py --base 594af2a8 --head HEAD` — expect no `SEVERITY: high` and no `REASON REQUIRED` in the three paths; report any survivor by function.
2. T-01 verify verbatim: `python3 tests/unit/test-expertise-ops.py && python3 tests/integration/test-expertise-merge.py`; expect 0 FAIL lines. Re-count with the AST expression above (119 / 255); runtime PASS tallies should equal the pre-refactor run (receipt-harness-backend-dev-T-01-c1.md: unit 194, integration 355).
3. Run the canonical-reader classification gate (`cmd_ops.transform` anchor) and `check-plan-routes`/instruction-path guards once.
4. Commit under the T-01 convention after reader findings are applied.
