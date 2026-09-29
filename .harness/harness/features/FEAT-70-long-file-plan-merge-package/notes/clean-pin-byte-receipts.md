# FEAT-70 — clean-checkout implementation-pin receipts (reviewed record)

The generated receipt `clean-pin-byte-receipts.generated.md` is the evidence and is committed exactly
as `receipt-scripts/feat70-cleanpin.py` wrote it. This file is the human record beside it.

## Identity and chronology
- implementation pin: `73ba9dceee11253bbf57b7ca1b36323c81d83891` — the last production/test commit.
  Production: carve b900d207, twelve grade fixes dbba18f7, simplify pass 35b42d2a (the FIRST pin,
  superseded). Validate c0 found the sweep/hooks fixtures copy bin's files without its packages
  (VAL-02); that test-only fix, 73ba9dce, selected this pin and every measurement was re-run for
  it. Because the fix landed after the first pin's receipts were committed, the pin TREE contains
  the first pin's receipt files; nothing in them is claimed for this pin — the receipts for
  73ba9dce are the commit after it, derived from executions over 73ba9dce.
- baseline: `9e531b34fc04f752cedf51586dc13c460580901a`, the worktree's base (origin/main when cut).
- checkouts: `.claude/worktrees/harness/feat70-cleanpin-73ba9dce` and `feat70-base-9e531b34`, both
  detached, `git status --porcelain` empty, asserted by the script before any measurement.
- executions: `feat70-baseline.py` once per checkout (stamps printed in the generated receipt): the
  baseline's from the 13:50Z run (its tree did not change), the pin's fresh over 73ba9dce; the
  SC-03 cross-run and the two grade assertions once each at receipt time.

## Reproduction, exactly as run
From the FEAT-70 worktree root:
```
python3 .harness/harness/features/FEAT-70-long-file-plan-merge-package/notes/receipt-scripts/feat70-cleanpin.py 73ba9dceee11253bbf57b7ca1b36323c81d83891 9e531b34fc04f752cedf51586dc13c460580901a
```
(~65 min: two plain suite runs, two recorded suite runs of 293/295 CLI invocations, two scratch
corpora of 6,518 commands over 100 plans, grades.) Add `--reuse` to regenerate from the JSONs.

## What was measured (SC-02), and the result
1. The checkout's own `test-plan-merge.py`, plainly: exit 0 both sides; 107 pre-existing case
   identities identical; the pin adds `case_feat70_record_amendments_after_a_block_scalar_splice`.
2. Behavioural ledger: every CLI subprocess the 107 cases fork, through a recording shim (argv,
   exit, stdout, stderr, plan bytes before/after). 293 aligned invocations; 2 differing records,
   both ruled (below). Determinism applied identically on both sides by the driver, never to the
   tool: fixed fixture paths, frozen clock inside the shim, serialised `Popen` in the concurrency
   case. `behavioral_identity: PASS`.
3. Scratch corpus: 100 tracked `plan.yaml` (own record excluded), `check` + idempotent
   `set-feature-station` + per-task `set-task-station` + per-field `amend --show`, 6,518 commands per
   side, zero plan changes either side; 5 differing records in 4 plans, all ruled (below).
   `scratch_identity: PASS`.
4. Grades: 12 below bar 4 at baseline, 0 at pin; 198 moved functions with unchanged bodies keep
   their exact grade; 16 changed bodies and 23 new helpers all ≥4.

## Rulings (fable-advisor, blocking rulings delegated by the operator on 2026-09-28)
Recorded in `notes/divergence-rulings.json` and printed beside each record in the generated
receipt. Full text in `build-divergences.md`.
- Two stderr records in `case_feat61_approval_reset_refuses_an_unknown_task_station` (`delete-items`,
  an intended raise): traceback FRAME file/line coordinates changed because the code moved;
  function-name chain, final exception line, exit, stdout, plan bytes identical. Accepted; no
  traceback normalisation added.
- Five scratch records (`check` over the shipped plans BUG-1699, FEAT-1714, FEAT-61, FEAT-66): each
  carries a `plan-merge.py#<symbol>` anchor to a function now in the package, so the pin's `check`
  prints one more `FAIL … no definition or token` line (FEAT-66's exit 0→1). Identical tool logic
  on changed input; DEC-232 re-resolves at build entry and these shipped plans have none; re-pointing
  would reset four approvals. Accepted (option A); no anchor edited.

## SC-01
`feat70-grade-assert.py <pin> <baseline>` green at the pin (237 functions: 106 at 5, 131 at 4);
`--tree <baseline>` red (12 below 4; no package; the twelve not at their owners). Both outputs are
in the generated receipt.

## SC-03
`red-first-receipts.md`.

## T-01 `verify:`, verbatim as plan.yaml spells it, and its output (exit 0)

```
python3 -c 'import importlib.util,pathlib,sys; r=pathlib.Path("."); p=r/".claude/skills/harness/bin/plan_merge"; want={"__init__.py","text.py","guards.py","union.py","approval.py","stations.py","panel.py","amend.py","amendments.py","delete.py","check.py"}; assert {x.name for x in p.glob("*.py")}==want; g=r/".claude/skills/harness/bin/code_grade.py"; s=importlib.util.spec_from_file_location("feat70_grade",g); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); paths=[r/".claude/skills/harness/bin/plan-merge.py",*sorted(p.glob("*.py"))]; bad=[(q.path,q.qualname,q.grade) for x in paths for q in m.grade_source(x.read_text(),str(x)) if q.grade<4]; assert not bad,bad; sys.path.insert(0,str(r/".claude/skills/harness/bin")); e=importlib.util.spec_from_file_location("feat70_entry",paths[0]); n=importlib.util.module_from_spec(e); e.loader.exec_module(n); assert callable(n.signed_task_hash)' &&
python3 tests/integration/test-plan-merge.py && python3 tests/integration/test-check-state-worktrees.py && python3 tests/integration/test-check-plan-routes.py
```

Output (tail):

```
over_budget_task_sets_the_EXIT_CODE_not_just_stdout
PASS case_23i_the_budget_boundary_is_exact
PASS case_23j_every_budgeted_field_counts_exactly_once
PASS case_23j2_BUDGETED_FIELDS_is_still_the_eleven_this_case_pins
PASS case_23g_both_plan_yaml_and_PLAN_md_is_refused
PASS case_24_backlog_is_checked
PASS case_24_plan_is_checked
PASS case_24_ready_is_checked
PASS case_24_building_is_checked
PASS case_24_review_is_checked
PASS case_24_done_is_skipped
PASS case_24_abandoned_is_skipped
PASS case_24_Done_is_checked
PASS case_24_finished_stations_is_a_subset_of_the_station_vocabulary
PASS case_24_no_feature_yaml_is_checked_not_skipped
PASS case_24_feature_yaml_a_sequence_is_checked_not_crashed
PASS case_24_feature_yaml_a_bare_scalar_is_checked_not_crashed
PASS case_24_feature_yaml_status_is_a_list_is_checked_not_crashed
PASS case_24_feature_yaml_a_mapping_with_no_status_is_checked_not_crashed
PASS case_24_ten_key_feature_json_with_a_done_plan_station_is_skipped_end_to_end
PASS case_27a_owner_manifest_controls_routes
PASS case_27b_prior_revision_false_ok
PASS case_27c_unreadable_owner_manifest_refuses
PASS case_41a_legal_task_statuses_is_the_mandate_plus_the_terminal_stations
PASS case_41b_every_legal_task_status_and_an_absent_one_are_accepted
PASS case_41c_task_status_pending_is_a_VIOLATION_naming_the_value
PASS case_41c_task_status_Building_is_a_VIOLATION_naming_the_value
PASS case_41c_task_status_Done_is_a_VIOLATION_naming_the_value
PASS case_41c_task_status_shipped_is_a_VIOLATION_naming_the_value
PASS case_41c_task_status_in-progress_is_a_VIOLATION_naming_the_value
PASS case_41c_task_status_exits_1_with_one_violation_per_value
PASS case_41c_the_violation_names_every_legal_value
PASS case_41d_an_absent_or_legal_top_level_status_is_accepted
PASS case_41f_top_level_status_pending_is_a_VIOLATION_naming_the_value
PASS case_41f_top_level_status_Done_is_a_VIOLATION_naming_the_value
PASS case_41f_top_level_status_nonsense_is_a_VIOLATION_naming_the_value
PASS case_41f_top_level_status_exits_1_with_one_violation_per_value
PASS case_41_t07_is_shipped_FEAT-A-shipped_is_shipped
PASS case_41_t07_is_shipped_FEAT-B-building_is_checked
PASS case_41_t07_is_shipped_FEAT-C-no-plan_is_checked
PASS case_41_t07_is_shipped_FEAT-D-plan-md-era_is_shipped
PASS case_41_t07_is_shipped_FEAT-E-both_is_checked
PASS feat64_manifest_deviation_unrelated_RuntimeError_escapes
PASS feat64_live_plan_loaded_exactly_once_per_execution
PASS feat64_shipped_plan_loaded_exactly_once_and_skipped

ALL PASS
```

## T-02 `verify:`, verbatim as plan.yaml spells it, and its output (exit 0)

```
python3 -c 'import re,subprocess; rel=".harness/harness/features/FEAT-70-long-file-plan-merge-package/notes/clean-pin-byte-receipts.generated.md"; c=subprocess.check_output(["git","log","-1","--format=%H","HEAD","--",rel],text=True).strip(); assert c,"receipt commit not found"; t=subprocess.check_output(["git","show",f"{c}:{rel}"],text=True); p=re.findall(r"(?m)^implementation_pin: ([0-9a-f]{40})$",t); assert len(p)==1,p; pin=p[0]; assert pin!=c; assert "baseline: 9e531b34fc04f752cedf51586dc13c460580901a" in t; assert re.search(r"(?m)^baseline_existing_cases: 107/107 PASS$",t); assert re.search(r"(?m)^pin_existing_cases: 107/107 PASS$",t); assert re.search(r"(?m)^behavioral_identity: PASS$",t); assert re.search(r"(?m)^scratch_identity: PASS$",t); assert re.search(r"(?m)^overall: PASS$",t); subprocess.run(["git","merge-base","--is-ancestor",pin,c],check=True); subprocess.run(["python3",".harness/harness/features/FEAT-70-long-file-plan-merge-package/notes/receipt-scripts/feat70-grade-assert.py",pin,"9e531b34fc04f752cedf51586dc13c460580901a"],check=True)'
```

Output (tail):

```
graded tree 73ba9dceee11253bbf57b7ca1b36323c81d83891: 237 function(s) over 12 file(s): 5 -> 106, 4 -> 131, 3 -> 0, 2 -> 0, 1 -> 0
pre-image 9e531b34fc04f752cedf51586dc13c460580901a: 214 function(s) in the monolith
moved, body unchanged (grade identity required): 198
moved, body changed (>= 4 required): 16 -> [('_amended_plan_bytes', 4, 4), ('_amendment_against_plan', 4, 4), ('_find_field_line', 3, 4), ('_index_list_items', 3, 5), ('_index_top_keys', 3, 4), ('_item_range', 3, 5), ('_panel_own_end', 3, 4), ('_parsed_value', 3, 4), ('_print_apply_receipt', 3, 4), ('_proposal_field_lines', 4, 4), ('_render_field', 4, 4), ('_replace_fields', 3, 4), ('_task_status_line', 2, 4), ('_verify_spliced', 2, 5), ('cmd_amend', 2, 4), ('cmd_amend.transform', 2, 4)]
new (>= 4 required): 23 -> [('_amend_preflight', 4), ('_amend_rendered', 5), ('_amend_request', 5), ('_closes_item', 5), ('_dash_lines_at_first_indent', 4), ('_differing_fields', 4), ('_expected_union_ids', 4), ('_half_open_ranges', 5), ('_is_document_tail', 5), ('_is_own_field', 5), ('_item_by_id', 4), ('_item_closed_by_range', 5), ('_item_range_within', 4), ('_locate_under_lock', 5), ('_opens_nested_block', 5), ('_print_field_rows', 4), ('_refuse_illegal_amendment', 5), ('_reload_spliced', 5), ('_status_in_task', 4), ('_task_search', 4), ('_top_key_positions', 4), ('_verify_schema_preserved', 5), ('_verify_union_ids', 4)]
twelve named: _task_status_line 2->4, _verify_spliced 2->5, cmd_amend 2->4, cmd_amend.transform 2->4, _item_range 3->5, _index_list_items 3->5, _find_field_line 3->4, _parsed_value 3->4, _index_top_keys 3->4, _print_apply_receipt 3->4, _panel_own_end 3->4, _replace_fields 3->4
GREEN: every function on plan-merge.py + plan_merge/** at grade >= 4; owners, identity, import all hold
```
