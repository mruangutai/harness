# STATE

## Current

- feature: FEAT-30-worktree-per-feature
- run: none — plan phase complete, awaiting the operator's signature
- squad: none
- status: awaiting-user

plan.yaml is drafted, simplified, applied and architecture-reviewed: 9 tasks, 9 decisions, 1171
lines, approval pending, lanes.resolved_at eeabc59. All three DEC-195 segments returned; the review
ruled all six architecture questions in the plan's favour and asked for no cycle. cycles_used 3 of
10, four runs recorded.

Two things must be settled before the plan is final, and both are the operator's: the blocking
question of whether REQ-04 binds 15 or all 16 agents, and one must_fix on T-09's removal actor. I did
NOT spend a cycle applying the must_fix, because the answer to the blocking question changes T-05 and
possibly T-09 too — one pm round after the operator rules discharges both instead of two.

## Open Questions

- BLOCKING: REQ-04 binds 15 of 16 governed agents. bash-write-guard.sh:56 returns before any rule for
  harness-dev-ops, so T-05's rule never reaches it, and T-01/T-02 are laned to that persona. The
  review recommends binding all 16 by placing the matcher ahead of the exemption, arguing DEC-151
  scopes the exemption to write targets and moving HEAD is not a write target. A scope statement on
  an approved requirement is the operator's to write.
- must_fix M-1: T-09 tells the orchestrator's own preloaded playbook to remove the worktree it stands
  in; three guards and three tests already refuse that guidance. Remedy is one sentence attributing
  removal to the main session from outside the tree.
- Also for the operator: SC-01b is deliverable by no task (four live orchestrators, operator
  judgement); D-09 accepts that a directory under WORKTREES_SEGMENT with no git pointer stops being
  budget-checked; DEC-193's and DEC-95's spelling of the worktree location goes stale and no task
  touches it; where Expertise close-out writes land once runs are isolated.
