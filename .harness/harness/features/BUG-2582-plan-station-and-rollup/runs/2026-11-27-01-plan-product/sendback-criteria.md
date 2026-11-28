# Send-back criteria — written before the draft returns (P-05)

A draft is sent back (or the team digest FAILs) if any holds:

1. An operator constraint is dropped or softened: loader `_validate_station_only` pair unchanged in both directions; INV-34 remedy text gains the "a later plan apply converts" line; BUG-2565 repro (one-task apply onto station-only record) becomes an exit-0 test.
2. Defect 2's relief is not scoped to plan-mission teams, or rests on the lead's word instead of validate-digest reading plan.yaml `panel.findings` on disk; or an open finding of that reader can still drop its FAIL.
3. Any task lacks `execution_mode: main-session-direct`.
4. Out-of-scope work appears (reader contract, INV-34 firing time, other roll-up ranks, #2622, #2627).
5. No answer on DEC-123 amend vs new decision, or `decisions_affected` empty without justification.
6. The reachability question is unanswered: record-panel appends findings as `disposition: open` (plan_merge/panel.py ~:458-474); the draft must say what flips a finding to `resolved` within the plan run before the lead's yield, or the defect-2 fix can never fire.
7. `plan-merge.py check` not run to exit 0.
