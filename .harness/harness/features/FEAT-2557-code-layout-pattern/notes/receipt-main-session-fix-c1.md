# Receipt — fix c1, main session (DEC-174 direct) — 2026-11-27

Must-fix from r-20261127-1-validate-validator (code-reviewer, substance/high, T-01): DEC-259 Because now names the plan-merge.py `signed_task_hash` re-export that FEAT-70 kept for INV-40 path loading. The low DEC-149 form finding is folded into the same paragraph, citing the agents' autoloadSkills frontmatter for current delivery and DEC-149 for origin. The change is prose only; plan-merge.py and check_state/ctx.py are untouched (SC-06). The index was regenerated because the DEC-259 row's derived tags changed.

T-01 verify (verbatim in notes/receipt-main-session-T-01.md) re-run after the edit: exit 0.

```text
examined 25 anchor(s), 0 failed
ok - test_row_per_distinct_dec_matches_authority
ok - test_argv_is_validated_and_only_the_write_path_writes
ok - test_malformed_row_is_reported_not_silently_dropped
ok - test_refs_graph_omits_ids_with_no_live_heading
ok - test_preserves_hand_written_rulings_by_dec_number
ok - test_strips_inline_ok_stale_marker_on_a_row
ok - test_committed_index_matches_a_fresh_regeneration
ok - test_committed_index_is_complete_and_within_budget
ok - test_orphaned_ruling_is_reported_not_silently_dropped
ok - test_root_resolves_through_harness_boundary_not_the_retired_variable
ok - test_no_amendment_construct_survives_in_the_authority
ok - test_dec_233_entry_names_every_removed_enforcement_point
LAYOUT-SKILL-AGENTS-DEC-OK
```
