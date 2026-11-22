# Receipt — harness-data-engineer — r-20261121-simplify-eng — FEAT-2229 (simplification angle)

BLUF: two LOW plan-surface restatement findings, both fold-in to pm as wording merges. No structural simplification: no pass-through layer, no new seam, no dead reference. Nothing weakens a plan assertion.

Read-only; no edits, no checks run. Angle: `.agents/skills/harness-simplify/references/angle-simplification.md` (plan surface: same fact twice, rule restated in two places, dead references). Craft leaf `delete-first.md` read.

## Findings

### S-1 (low) — T-01 states the drafted_at rule in two spellings
- File/line: `plan.yaml:168-172` (creation paragraph: "Existing plan edits never acquire or change this stamp as a side effect; legacy plans with no drafted_at remain legacy") vs `plan.yaml:226-236` (appended paragraph: refuse caller rewrite/insert on an existing plan via set-key or apply/merge; unchanged stamp may be preserved).
- Test duplication: `plan.yaml:216-217` ("legacy pending edits and byte preservation outside the intentional edit") vs `plan.yaml:232-235` (CLI regressions per route, identical bytes before/after refusal, controls that ordinary edits preserve the stamp or its absence).
- Cost: one invariant (an existing plan's drafted_at is never changed by any caller route) is asserted twice with different scope words ("side effect" vs "caller attempts"). A later edit to one paragraph can leave the other stale, and the implementer must reconcile which spelling governs.
- Alternative: fold the 168-172 sentence into the 226-236 reservation. Keep creation-stamp and caller-rejection-on-creation at 168-172. Keep the test list once. Preserves every assertion; it removes the duplicated wording only.
- Route: fold-in to pm.

### S-2 (low) — T-03 restates the exclusion list twice, and BRIEF already carries it
- File/line: `plan.yaml:347` ("Do not strike DEC-188 wholesale, revive stale markers, restore propagation checks, require reciprocal links, or append dated amendment history") vs `plan.yaml:348` ("No new validate script, relied_on_by field or reciprocal-link check"). BRIEF `BRIEF.md:48-50` is the canonical out-of-scope. Reciprocal-link appears in both T-03 lines.
- Cost: the same exclusions in three places. The two T-03 lines can drift, for example one gaining relied_on_by and the other not.
- Alternative: one exclusion sentence in T-03 (merge 347's tail and 348's last sentence); BRIEF stays canonical. No assertion weakened.
- Route: fold-in to pm.

## Checks performed (empty result elsewhere)
- Anchors resolve in the worktree (no dead references): `check.py:223 cmd_check`, `panel.py:389 _set_top_key`, `union.py:321 _seed_new_plan`, `union.py:544 _merge_plain_key`, `harness_yaml.py:377 validate_plan_doc`, `"seam_era_start"` in `.harness/harness.json:6` and `templates/harness.json:7`, `tests/integration/test-plan-team.py:130 scope = steps_by_id`, `test-plan-merge.py:717 case_create_path_approval`.
- New-module deletion test: T-01 adds no module or command. It extends `cmd_check`, `validate_plan_doc` and the existing writer, with two test scripts that are the unit/integration surface. T-02 adds no script (pm Mode 2 reuses `sc_status`). Nothing is a pass-through.
- Per-task restatements judged as not drifting, so left: T-02 template/draft-prompt/scope prompts restating row fields and check obligations (separate agent contexts, P-14); SPEC documenting fields (T-03:348, which already defers to canonical instructions for detail); harness.json note beside the key (matches existing `_seam_era_start_note` convention at `.harness/harness.json:5`).
- Settled set not re-raised: five-field rows, era gate, drafted_at reservation, the three T-02 trims, exclusions, DEC-174 lanes.
