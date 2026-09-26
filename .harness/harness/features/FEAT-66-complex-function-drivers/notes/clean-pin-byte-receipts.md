# FEAT-66 — clean-checkout implementation-pin receipts

Written 2026-09-26T15:08:51+00:00, AFTER the pin it names; this file is not inside `e2b580a6`.

- implementation pin: `e2b580a68cbc5116839c80e30c220f5b67cf6e65`
- baseline: `35c39f02bb383bba167e27d9a9b97c97798ef076` (the signed plan; production bytes identical to origin/main cb6f8050)
- pin checkout: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat66-cleanpin-e2b580a6` (detached, `git status --porcelain` empty)
- baseline checkout: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat66-base-35c39f02` (detached)
- baseline receipts: captured at the baseline in the feature worktree before any production edit (`/tmp/feat66-baseline.py` → `/tmp/feat66-baseline.json`); exit status and sha1 of stdout/stderr per suite.

## Owning suites at the pin vs baseline (SC-02)

Compared after replacing each checkout's own absolute root with `<checkout>` on both sides: three `ok` lines in
`test-validate-digest.py` print the agent file's absolute path, which names the checkout that ran the suite and nothing else.
The sha1 columns are of the raw bytes and so differ for that one suite; the `identical` column is the normalised comparison.

| suite | exit base→pin | stdout sha base / pin | stderr sha base / pin | identical |
|---|---|---|---|---|
| `tests/integration/test-check-domain.py` | 0→0 | 9f3a2d504473 / 9f3a2d504473 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-artifact.py` | 0→0 | 192c92446a82 / 192c92446a82 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-claims.py` | 0→0 | 1810b823ba32 / 1810b823ba32 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-grant.py` | 0→0 | 1e6c60523185 / 1e6c60523185 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-post.py` | 0→0 | 8b05b2b516ca / 8b05b2b516ca | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-worktree-parity.py` | 0→0 | 7d5700af43df / 7d5700af43df | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-worktree.py` | 0→0 | 5eb8753b929f / 5eb8753b929f | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-check-domain-approval.py` | 0→0 | 058ca85441ab / 058ca85441ab | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-plan-merge.py` | 0→0 | 331296f544b1 / 331296f544b1 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/integration/test-validate-digest.py` | 0→0 | 05d44942d82f / d9b52125dd3b | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/unit/test-config-shape-matrix.py` | 0→0 | 849446963b7b / 849446963b7b | da39a3ee5e6b / da39a3ee5e6b | yes |

All identical: **yes** (11/11).

## Grade lock at the pin (SC-01)

`python3 tests/unit/test-driver-grades.py` in the pin checkout → exit 0
```
PASS check-domain.py: shape_problems exists under its name
PASS check-domain.py: shape_problems grades >= 4 or exactly 2
PASS validate-digest.py: validate exists under its name
PASS validate-digest.py: validate grades >= 4 or exactly 2
PASS plan-merge.py: apply_merge exists under its name
PASS plan-merge.py: apply_merge grades >= 4 or exactly 2
ALL PASS
```

## Red-first: the pin's lock against the baseline tree (SC-01, SC-04)

`FEAT66_BIN=<baseline>/.claude/skills/harness/bin python3 <pin>/tests/unit/test-driver-grades.py` run in the baseline checkout → exit 1
```
PASS check-domain.py: shape_problems exists under its name
FAIL check-domain.py: shape_problems grades >= 4 or exactly 2 grade 1 (cyclomatic+cognitive+abc cyc=135 cog=356 abc=320.6)
PASS validate-digest.py: validate exists under its name
FAIL validate-digest.py: validate grades >= 4 or exactly 2 grade 1 (cyclomatic+cognitive+abc cyc=124 cog=244 abc=251.0)
PASS plan-merge.py: apply_merge exists under its name
FAIL plan-merge.py: apply_merge grades >= 4 or exactly 2 grade 1 (cyclomatic+cognitive+abc cyc=59 cog=136 abc=162.9)
3 failure(s)
```

## Extracted functions at bar 4 (plan.yaml verify's grade assertion, run at the pin)

exit 0
```
FEAT-66 grades [('.claude/skills/harness/bin/check-domain.py', '_head', 5), ('.claude/skills/harness/bin/check-domain.py', 'deny', 5), ('.claude/skills/harness/bin/check-domain.py', '_rule_run_digest', 4), ('.claude/skills/harness/bin/check-domain.py', '_rule_run_identity', 5), ('.claude/skills/harness/bin/check-domain.py', '_rule_plan_yaml', 4), ('.claude/skills/harness/bin/check-domain.py', '_plan_yaml_doc', 5), ('.claude/skills/harness/bin/check-domain.py', '_plan_yaml_bad_stations', 4), ('.claude/skills/harness/bin/check-domain.py', '_plan_yaml_bad_task_stations', 4), ('.claude/skills/harness/bin/check-domain.py', '_rule_feature_json', 4), ('.claude/skills/harness/bin/check-domain.py', '_feature_json_budget', 4), ('.claude/skills/harness/bin/check-domain.py', '_feature_json_schema_problems', 5), ('.claude/skills/harness/bin/check-domain.py', '_rule_state_yaml', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_doc', 5), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_version', 5), ('.claude/skills/harness/bin/check-domain.py', '_valid_state_version', 5), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_version_floor', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_step_schema', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_step_scan', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_evidence_offenders', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_step_findings', 5), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_step_sort', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_step_messages', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_post_seed', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_witness_uid', 5), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_prior_refusal', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_prior_parse', 4), ('.claude/skills/harness/bin/check-domain.py', '_prior_text', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_witness_refusal', 5), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_prior_doc_refusal', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_prior_identity_refusal', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_uid_refusal', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_unknown_keys', 4), ('.claude/skills/harness/bin/check-domain.py', '_rule_handoff', 4), ('.claude/skills/harness/bin/check-domain.py', '_handoff_section_problems', 4), ('.claude/skills/harness/bin/check-domain.py', '_handoff_done_when_problems', 5), ('.claude/skills/harness/bin/check-domain.py', '_rule_claude_md', 5), ('.claude/skills/harness/bin/check-domain.py', '_rule_state_md', 4), ('.claude/skills/harness/bin/check-domain.py', 'shape_problems', 4), ('.claude/skills/harness/bin/validate-digest.py', 'validate', 4), ('.claude/skills/harness/bin/validate-digest.py', '_persona_schema', 5), ('.claude/skills/harness/bin/validate-digest.py', '_optional_fields', 5), ('.claude/skills/harness/bin/validate-digest.py', '_common_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_verdict_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_headline_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_drift_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_field_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_missing_field_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_missing_field_hint', 4), ('.claude/skills/harness/bin/validate-digest.py', '_field_short_circuit', 4), ('.claude/skills/harness/bin/validate-digest.py', '_unbound_field_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_declined_gate_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_fail_value_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_field_type_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_flag_or_count_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_list_type_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_text_type_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_enum_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_near_miss', 4), ('.claude/skills/harness/bin/validate-digest.py', '_persona_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_qa_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_undeclared_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_reviewer_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_grade_2_reason_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_review_policy_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_code_grade_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_lead_rollup_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_empty_members_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_member_rank_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_worst_member', 4), ('.claude/skills/harness/bin/validate-digest.py', '_outranks', 5), ('.claude/skills/harness/bin/validate-digest.py', '_member_verdict', 4), ('.claude/skills/harness/bin/validate-digest.py', '_tail_errors', 4), ('.claude/skills/harness/bin/plan-merge.py', 'apply_merge', 4), ('.claude/skills/harness/bin/plan-merge.py', '_merge_keys', 4), ('.claude/skills/harness/bin/plan-merge.py', '_replaced_fields', 5), ('.claude/skills/harness/bin/plan-merge.py', '_fold_merge_rows', 4), ('.claude/skills/harness/bin/plan-merge.py', '_final_bytes', 5), ('.claude/skills/harness/bin/plan-merge.py', '_seed_new_plan', 4), ('.claude/skills/harness/bin/plan-merge.py', '_merge_inputs', 5), ('.claude/skills/harness/bin/plan-merge.py', '_parsed_proposal', 5), ('.claude/skills/harness/bin/plan-merge.py', '_refuse_approval_conflict', 4), ('.claude/skills/harness/bin/plan-merge.py', '_merged_key_order', 5), ('.claude/skills/harness/bin/plan-merge.py', '_merge_key', 4), ('.claude/skills/harness/bin/plan-merge.py', '_merge_union_key', 4), ('.claude/skills/harness/bin/plan-merge.py', '_aligned_items', 4), ('.claude/skills/harness/bin/plan-merge.py', '_union_key_head', 5), ('.claude/skills/harness/bin/plan-merge.py', '_indent_shift', 5), ('.claude/skills/harness/bin/plan-merge.py', '_items_by_id', 5), ('.claude/skills/harness/bin/plan-merge.py', '_carry_base_items', 4), ('.claude/skills/harness/bin/plan-merge.py', '_add_new_items', 4), ('.claude/skills/harness/bin/plan-merge.py', '_merge_plain_key', 4), ('.claude/skills/harness/bin/plan-merge.py', '_dump_merged', 4), ('.claude/skills/harness/bin/plan-merge.py', '_merged_union_list', 5), ('.claude/skills/harness/bin/plan-merge.py', '_carry_plain_keys', 4)]
```
