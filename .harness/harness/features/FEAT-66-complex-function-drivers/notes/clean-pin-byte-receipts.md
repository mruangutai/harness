# FEAT-66 — clean-checkout implementation-pin receipts

Written 2026-09-26T16:05:13+00:00, AFTER the pin it names; this file is not inside `f882dc3e`.

- implementation pin: `f882dc3e23dd274f4a9ed1d4b3add1b5f2891e69`
- baseline: `35c39f02bb383bba167e27d9a9b97c97798ef076` (the signed plan; production bytes identical to origin/main cb6f8050)
- pin checkout: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat66-cleanpin-f882dc3e` (detached, `git status --porcelain` empty)
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
| `tests/integration/test-validate-digest.py` | 0→0 | 05d44942d82f / 6d4722c14949 | da39a3ee5e6b / da39a3ee5e6b | yes |
| `tests/unit/test-config-shape-matrix.py` | 0→0 | 849446963b7b / 849446963b7b | da39a3ee5e6b / da39a3ee5e6b | yes |

All identical (normalised): **yes** (11/11).

### Raw-byte differences, exact lines (ledger D-09, operator-ruled not a divergence)

`tests/integration/test-validate-digest.py`:
```
-ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-66-complex-function-drivers/.omp/agents/harness-code-reviewer.md
-ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-66-complex-function-drivers/.omp/agents/harness-security-reviewer.md
-ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-66-complex-function-drivers/.omp/agents/harness-ui-reviewer.md
+ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat66-cleanpin-f882dc3e/.omp/agents/harness-code-reviewer.md
+ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat66-cleanpin-f882dc3e/.omp/agents/harness-security-reviewer.md
+ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat66-cleanpin-f882dc3e/.omp/agents/harness-ui-reviewer.md
```

## SC-01: the plan's inline grade assertion (T-01 verify) at the pin — green

run in the pin checkout → exit 0
```
FEAT-66 grades [('.claude/skills/harness/bin/check-domain.py', '_head', 5), ('.claude/skills/harness/bin/check-domain.py', 'deny', 5), ('.claude/skills/harness/bin/check-domain.py', '_rule_run_digest', 4), ('.claude/skills/harness/bin/check-domain.py', '_rule_run_identity', 5), ('.claude/skills/harness/bin/check-domain.py', '_rule_plan_yaml', 4), ('.claude/skills/harness/bin/check-domain.py', '_plan_yaml_doc', 5), ('.claude/skills/harness/bin/check-domain.py', '_plan_yaml_bad_stations', 4), ('.claude/skills/harness/bin/check-domain.py', '_plan_yaml_bad_task_stations', 4), ('.claude/skills/harness/bin/check-domain.py', '_rule_feature_json', 4), ('.claude/skills/harness/bin/check-domain.py', '_feature_json_budget', 4), ('.claude/skills/harness/bin/check-domain.py', '_feature_json_schema_problems', 5), ('.claude/skills/harness/bin/check-domain.py', '_rule_state_yaml', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_doc', 5), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_version', 5), ('.claude/skills/harness/bin/check-domain.py', '_valid_state_version', 5), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_version_floor', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_step_schema', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_step_scan', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_evidence_offenders', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_step_findings', 5), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_step_sort', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_step_messages', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_post_seed', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_witness_uid', 5), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_prior_refusal', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_prior_parse', 4), ('.claude/skills/harness/bin/check-domain.py', '_prior_text', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_witness_refusal', 5), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_prior_doc_refusal', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_prior_identity_refusal', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_uid_refusal', 4), ('.claude/skills/harness/bin/check-domain.py', '_state_yaml_unknown_keys', 4), ('.claude/skills/harness/bin/check-domain.py', '_rule_handoff', 4), ('.claude/skills/harness/bin/check-domain.py', '_handoff_section_problems', 4), ('.claude/skills/harness/bin/check-domain.py', '_handoff_done_when_problems', 5), ('.claude/skills/harness/bin/check-domain.py', '_rule_claude_md', 5), ('.claude/skills/harness/bin/check-domain.py', '_rule_state_md', 4), ('.claude/skills/harness/bin/check-domain.py', 'shape_problems', 4), ('.claude/skills/harness/bin/validate-digest.py', 'validate', 4), ('.claude/skills/harness/bin/validate-digest.py', '_persona_schema', 5), ('.claude/skills/harness/bin/validate-digest.py', '_optional_fields', 5), ('.claude/skills/harness/bin/validate-digest.py', '_common_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_verdict_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_headline_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_drift_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_field_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_missing_field_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_missing_field_hint', 4), ('.claude/skills/harness/bin/validate-digest.py', '_field_short_circuit', 4), ('.claude/skills/harness/bin/validate-digest.py', '_unbound_field_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_declined_gate_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_fail_value_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_field_type_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_flag_or_count_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_list_type_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_text_type_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_enum_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_near_miss', 4), ('.claude/skills/harness/bin/validate-digest.py', '_persona_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_qa_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_undeclared_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_reviewer_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_grade_2_reason_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_review_policy_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_code_grade_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_lead_rollup_errors', 5), ('.claude/skills/harness/bin/validate-digest.py', '_empty_members_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_member_rank_errors', 4), ('.claude/skills/harness/bin/validate-digest.py', '_worst_member', 4), ('.claude/skills/harness/bin/validate-digest.py', '_outranks', 5), ('.claude/skills/harness/bin/validate-digest.py', '_member_verdict', 4), ('.claude/skills/harness/bin/validate-digest.py', '_tail_errors', 4), ('.claude/skills/harness/bin/plan-merge.py', 'apply_merge', 4), ('.claude/skills/harness/bin/plan-merge.py', '_merge_keys', 4), ('.claude/skills/harness/bin/plan-merge.py', '_replaced_fields', 5), ('.claude/skills/harness/bin/plan-merge.py', '_fold_merge_rows', 4), ('.claude/skills/harness/bin/plan-merge.py', '_final_bytes', 5), ('.claude/skills/harness/bin/plan-merge.py', '_seed_new_plan', 4), ('.claude/skills/harness/bin/plan-merge.py', '_merge_inputs', 5), ('.claude/skills/harness/bin/plan-merge.py', '_parsed_proposal', 5), ('.claude/skills/harness/bin/plan-merge.py', '_refuse_approval_conflict', 4), ('.claude/skills/harness/bin/plan-merge.py', '_merged_key_order', 5), ('.claude/skills/harness/bin/plan-merge.py', '_merge_key', 4), ('.claude/skills/harness/bin/plan-merge.py', '_merge_union_key', 4), ('.claude/skills/harness/bin/plan-merge.py', '_aligned_items', 4), ('.claude/skills/harness/bin/plan-merge.py', '_union_key_head', 5), ('.claude/skills/harness/bin/plan-merge.py', '_indent_shift', 5), ('.claude/skills/harness/bin/plan-merge.py', '_items_by_id', 5), ('.claude/skills/harness/bin/plan-merge.py', '_carry_base_items', 4), ('.claude/skills/harness/bin/plan-merge.py', '_add_new_items', 4), ('.claude/skills/harness/bin/plan-merge.py', '_merge_plain_key', 4), ('.claude/skills/harness/bin/plan-merge.py', '_dump_merged', 4), ('.claude/skills/harness/bin/plan-merge.py', '_merged_union_list', 5), ('.claude/skills/harness/bin/plan-merge.py', '_carry_plain_keys', 4)]
```

## SC-01 / SC-04 red-first: the same assertion run in the baseline checkout — red

run in the baseline checkout (the three retained drivers grade 1 there) → exit 1
```
FEAT-66 grades [('.claude/skills/harness/bin/check-domain.py', 'shape_problems', 1), ('.claude/skills/harness/bin/validate-digest.py', 'validate', 1), ('.claude/skills/harness/bin/plan-merge.py', 'apply_merge', 1)]
```
