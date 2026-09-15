# Code review — BUG-285-canonical-reader — c2

**FAIL.** The pinned target is `afec455b6a513dc1989608faab92378646b58d77`; the exact reviewed feature range is `276a7d11fe30dae7901411570a14a0dbbe336207..afec455b6a513dc1989608faab92378646b58d77`. The worktree is clean. The post-review delta cannot inherit/extend the accepted `5be21a432b87ed648c0bed50fbf9a2642c84e0a9` review because its final plan compaction breaks the feature's permanent route-accounting contract.

## Stage 1 — spec compliance: FAIL

1. **F-01 — rank 1, high/substance, must-fix (T-03/T-07; SC-01/SC-04).** `plan.yaml:229` and `plan.yaml:384` replace explicit `factory_claim.py` / `factory_config.py` scope entries with `.claude/skills/harness/bin/factory_c[ol][an]*.py`. The glob itself expands only to those two intended files, so it does not broaden into unrelated files. But the canonical-reader route checker does not expand task globs: `_task_files` stores each file claim literally (`check-plan-routes.py:1217-1226`) and `_route_finding` requires exact string membership for each classified source (`check-plan-routes.py:1141-1155`). Consequently the classified T-03 `factory_claim.py` and `factory_config.py` rows (`canonical-reader-classification.json:819-830,870-881`) and T-07 `factory_config.py` row (`canonical-reader-classification.json:857-868`) are reported as omitted from their task scopes, with `PLAN AMENDMENT REQUIRED`. Specific failure scenario: run the required canonical-reader audit or either classification-task check against this pinned plan; the literal glob never equals either classified file path, so a fully canonical tree fails its permanent zero-drift gate. Restore explicit paths or make the already-required route check resolve plan globs consistently.

The updated T-02 symbol is valid: `plan.yaml:195` names `feature_json_write.py#write_feature_json`, which resolves to the public writer at `feature_json_write.py:131`. The strict-reader fixture changes are scoped compatibility repairs: the shared fleet fixture now supplies `default_branch`, dependent tests remove a duplicate local insertion, the factory integration plan fixture becomes schema-valid, and the two unit-runner fixtures include the newly imported accessor module. No separate defect was found in those changes.

**SC-06 inspection:** semantic cutover and mechanical relocation remain separated by signed D-04 and the T-03/T-04 task/commit split; the delta does not collapse them.

## Stage 2 — code quality: PASS apart from the stage-one gate

No new shipped-reader implementation or error path changed after the prior accepted review. The fixture edits do not introduce a silent failure or broaden their fixtures. Mechanical Python grading over `merge-base(origin/main, afec455b)..afec455b` is `grade_2`; `tests/integration/test-check-omp-port.py:71 case_live_tree_passes` remains one cohesive live-tree integration scenario whose setup and observations belong together.

## History and human-edit reconciliation

The post-review range contains no `[harness:human]` commit and the worktree has no uncommitted changes. Commit `efd7b9194c7116d5a253b5ed07ef3c05534b2699` merges `origin/main` parent `276a7d11fe30dae7901411570a14a0dbbe336207`; incoming mainline records (including BUG-1507 state) were reconciled as merge ancestry rather than attributed to BUG-285. The feature-authored post-review commits are the fixture compatibility fixes and plan compaction described above. Because F-01 is introduced by final commit `afec455b6a513dc1989608faab92378646b58d77`, the delta is not acceptable and cannot extend the prior PASS without remediation and re-review.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Pinned afec455b6a513dc1989608faab92378646b58d77 fails: compact T-03/T-07 globs break exact canonical-reader route accounting."
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      summary: "Compact factory globs are not expanded by the permanent route checker, so required T-03/T-07 classified rows fail as omitted."
      why: "A canonical-reader audit against the pinned plan compares classified source paths to literal task entries and emits PLAN AMENDMENT REQUIRED for factory_claim.py and factory_config.py."
  must_fix:
    - "Restore exact factory_claim.py and factory_config.py task scope entries, or make canonical route accounting resolve the signed globs without broadening their two-file scope."
  spec_violations:
    - kind: mismatch
      path: .harness/harness/features/BUG-285-canonical-reader/plan.yaml
      ref: SC-01/SC-04
  code_grade: grade_2
  grade_2_reasons:
    - "tests/integration/test-check-omp-port.py:71 case_live_tree_passes is one cohesive live-tree integration scenario whose setup and observations belong together."
  reviewed: "276a7d11fe30dae7901411570a14a0dbbe336207..afec455b6a513dc1989608faab92378646b58d77"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/.harness/harness/features/BUG-285-canonical-reader/notes/review-harness-code-reviewer-c2.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/.harness/harness/features/BUG-285-canonical-reader/notes/review-harness-code-reviewer-c2.md
```
