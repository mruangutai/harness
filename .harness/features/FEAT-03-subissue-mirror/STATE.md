# STATE

## Current

- feature: FEAT-03-subissue-mirror
- run: .harness/features/FEAT-03-subissue-mirror/runs/2026-07-31-02-eng/state.yaml
- squad: none
- status: awaiting-user
- phase: plan — at the approval gate, which is this phase's exit predicate (DEC-148)
- note: BRIEF.md and PLAN.md written, both `## Approval` `status: pending`. Segment 1 (pm) PASS;
  segment 2 (eng-lead architecture review) FAIL with six must_fix on task specs — the destination,
  the shared-module design and the Feature B razor all judged sound. The must_fix are NOT routed to
  pm: Q7 (the plan phase alone consumed ~$44 of the $40 feature budget) is a signature-time decision
  that may change the decomposition those fixes would apply to. Next action: notes/handoff-plan.md.
  Segments 1b (visual-designer) and 3 (ui-reviewer) skipped — see feature.yaml skipped_segments.

## Open Questions

- Q7 (BLOCKING, eng-lead + orchestrator) — budget. ~$44 spent of `max_cost_usd: 40`, entirely in
  planning, with the whole build ahead; eight member spawns remain. Raise the budget, cut the task
  count, or re-scope. The broader question: is `budgets.per_feature_usd: 40` right for SELF-HOSTED
  features at all, where the codebase under change is the docs every agent must read?
- Q1 (pm) — `.claude/skills/harness/SKILL.md:137,144` state the mirror contract this feature
  reverses; no agent domain covers that file, so it needs a main-session edit.
- Q2 (pm) — the BRIEF-H1 parent-title contract needs `.claude/skills/harness-brief/SKILL.md`;
  same uncovered-domain problem.
- Q3 (pm) — freezing an adopted wayfinding map issue's body at hand-off is settled in the grilling
  but scoped out of this BRIEF; nobody owns it.
- Q4 (pm) — prototype gate: pm judged NO prototype required, substituting for visual-designer,
  which never ran. Overridable.
- Q5 (pm) — PLAN adds an `attached:` receipt list to `feature.yaml github:`, a local-state schema
  addition the grilling did not name. eng-lead judged it safely writable under the regex constraint,
  with one sharp edge: the issues reader `^\s{4}(T-\d+):\s*(\d+)` would misread a nested form.
- Q6 (pm) — pm judges the slug `subissue-mirror` narrower than the feature; id not renamed.
- Q8 (eng-lead) — T-08's owner harness-documentor is in the Product squad; the build segment needs
  lateral routing, eng-lead cannot spawn it.
- Q9 (eng-lead) — no `build` team yaml exists (only gate-probe.yaml, review.yaml); pre-existing gap.
- Q10 (orchestrator, harness defect) — check-state.sh infers a cycle from any FAIL run, so it fires
  a VIOLATION on the legitimate "FAIL held at the user gate, not routed back" state that DEC-157
  defines as zero cycles. Also asymmetric: a pending PLAN is a `note`, a pending BRIEF is a
  VIOLATION — yet a plan mission necessarily ends with both pending.
- Q11 (orchestrator, harness defect) — the playbook's `cost-report.py --yaml >> <run_dir>/state.yaml`
  append produces a duplicate top-level `cost:` key beside the lead's `cost: pending_orchestrator`,
  which check-state.sh rejects per DEC-156. Fixed by hand in both run dirs this feature; the
  instruction and the invariant still disagree.
- Q12 (orchestrator, tree dirt) — `.claude/skills/harness/bin/__pycache__/gh-sync.cpython-314.pyc`
  is untracked dirt I created at 09:23 running the test suite, and `bash-write-guard` correctly
  refused my `rm` (not my domain), so I cannot restore the tree. `dirty_tree_whitelist` covers only
  `.harness/**` and `.claude/worktrees/**`, so this HALTS the next team with BLOCKED. Also:
  `validate-digest.cpython-314.pyc` is already TRACKED, and neither `.gitignore` nor
  `templates/gitignore.snippet` has any pycache rule. `.claude/settings.json.harness-bak` sits in
  the same non-whitelisted position.
