# Receipt — harness-backend-dev — BUG-2161 altitude pass (read-only)

BLUF: two altitude findings, both fold-in; no plan edits made by this reader. Verdict PASS (advisory).
No checks, tests or verify commands executed; files_touched [].

## Findings

### A-1 fold-in — already-abandoned "no rewrite" has no named home or reader
- File/line: plan.yaml:106 (T-01 intent), D-02 (plan.yaml:79-82).
- Summary: "Re-entry at abandoned must not rewrite that station" is planned as a branch inside cmd_abandon, but the plan names no station reader. Existing readers: `artifact_accessors.load_plan` (already used by `parse_source_issues`, gh-sync.py:469-497) and `check_state/ctx.py:station_of`; `worktree_terminal.py` already carries a regex fallback for the same key. `_record_station` (gh-sync.py:625) and `plan_merge/stations.py:cmd_set_feature_station` have no equal-value short-circuit; [INFERENCE] the splice of an identical value is byte-identical, so "no rewrite" may be unobservable except as a skipped subprocess.
- Cost: a third hand-parse of plan.yaml `status` in a CLI, or a caller-side guard plus a test for a difference nothing can observe; the idempotence rule lives in one caller while `_record_station` is shared with ship/reject/status.
- Alternative: either (a) state in T-01 that the guard reuses `artifact_accessors.load_plan(...)["status"]` (no new parser) and that the assertion is "set-feature-station not invoked", or (b) drop the no-rewrite clause and always call `_record_station` (idempotent by value), keeping only the retained-runs/ prune assertion that INV-51 actually needs. Recommend: fold-in.

### A-2 fold-in — parent-hardwired reporters not in T-01's intent
- File/line: plan.yaml:105-106 (T-01 intent); gh-sync.py:1750-1755 (`_post_abandon_reason`: "reason posted on parent #N"), 1766-1774 (`_report_abandon_gaps`: "no parent recorded — reason not posted").
- Summary: the planned source comment reuses the one comment executor, but its success/failure lines and the gap report assume the comment target is the parent. With sources opted in and no parent (the FEAT-1774 case: unopened mirror), output says "reason not posted" while sources received it.
- Cost: operator's post-run report contradicts what executed, undercutting the "one reported disposal matching what executes" goal (BRIEF maintainer perspective); two message paths to keep in step.
- Alternative: T-01 intent names generalizing those two reporters (target label from plan kind, gap line conditioned on no comment target at all) in the existing functions rather than a source-specific copy. Recommend: fold-in.

## Checked, no finding (leave)
- Source disposal integrated into `_abandon_plan`/`_apply_abandon_plan`/`_close_and_reseat` rather than a second command: right depth (redesign-from-first-principles applied).
- T-02 restating T-01 behavior prose: restatement is the DEC's own content; low drift cost. leave.
- D-01 residual (operator-owned shared-ticket risk): compensating control named (full dry run + both flags). leave.
- `--close-sources` refusal on other subcommands mirrors the existing `--yes` guard (gh-sync.py:2473). leave.
- Unit + integration both covering planner: SC-05 mandates; test-angle, not altitude. leave.
