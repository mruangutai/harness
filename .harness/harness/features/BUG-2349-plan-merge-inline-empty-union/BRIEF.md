# BRIEF — BUG-2349 Inline-empty union additions

## Problem

An operator adding decisions or tasks with plan-merge.py apply to an existing inline-empty list receives exit 5 because the splice retains the inline empty head above new block items. The refusal prevents the intended update and currently blocks FEAT-2257's decision addition (intake and issue #2349).

## Done when — by perspective

**operator** — I can add items to an empty decisions or tasks list and reload the resulting plan. I have direct scratch-repository evidence from both the fixed and merged tool, not only a test-suite result.

**code maintainer** — I can rely on focused regressions for both affected keys without weakening the existing formatting refusal or broadening this patch.

## Success criteria

- SC-01 (operator): Regression cases independently start with decisions: [] and tasks: [], apply proposals adding items, and assert successful apply plus reloaded items present. QA demonstrates both new assertions failing against the pre-fix implementation before they pass against the fix.
  verify: automated evidence: integration
- SC-02 (code maintainer): An explicit regression with non-empty flow-style base decisions: [a] still asserts exit 5 and the one-dash-per-item alignment refusal.
  verify: automated evidence: integration
- SC-03 (code maintainer): At the review pin, git show <review_sha>:.claude/skills/harness/bin/plan_merge/union.py shows proposal-head selection exactly when the base has no items and the proposal has items; otherwise existing base-head precedence remains. The implementation/test diff from e239d88156c508c948d49cd31238ea13b3b39865 to that pin changes only this file and tests/integration/test-plan-merge.py; feature record artifacts are not implementation changes.
  verify: inspection
- SC-04 (operator): After the fix and again after merge, a fresh scratch git repository containing .harness/features/FEAT-9-x/plan.yaml with decisions: [] accepts the proposal decisions:\n- id: D-01\n  choice: x; apply exits 0 and the written YAML round-trips with D-01 and choice x. Preserve command, tool checkout SHA, stdout/stderr and reloaded value for each run; the post-merge run must use the merged checkout tool, with an explicit owner-root override rather than a deleted feature worktree default.
  verify: automated evidence: integration

## Verification gaps

No applicable null-runner kind: integration is active and discovers tests/integration/test-plan-merge.py; unit is also active if required by the bugfix matrix. Component, ui and typecheck gaps do not cover this Python CLI patch. SC-04 requires separate scratch-repository command receipts before and after merge; suite success alone does not discharge it. Applicable product guidance docs/spec.md, docs/decisions.md and docs/architecture.md are absent in the assigned product checkout; this patch uses the settled intake and existing implementation contract, not invented product guidance.

## Constraints

- DEC-174 BLOCKS governed implementation of this enforcement writer and its tests: T-01 is main-session-direct, including any task subagent edits confined to this assigned feature worktree.
- DEC-225 SUPPLIES the patch lane: one task, at most 120 brief lines, no panel or goal-check. DEC-174 governs execution despite the patch reference's generic team route.
- DEC-182 SUPPLIES the controlled plan write route and literal verification contract; only main records explicit signature under DEC-120.
- Fix only .claude/skills/harness/bin/plan_merge/union.py and tests/integration/test-plan-merge.py. Adjacent cleanup requires a separate ticket.
- Preserve existing non-empty flow-list exit-5 refusal; do not relax _aligned_items.

## Out of scope

- Any other plan-merge verb, refusal or formatting behavior — bounded known-cause patch.
- FEAT-2257's plan content — separate feature, not a workaround for this defect.

## Approval

status: pending
approved-by:
date:
