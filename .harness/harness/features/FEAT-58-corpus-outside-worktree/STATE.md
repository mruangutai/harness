# STATE

## Current

- feature: FEAT-58-corpus-outside-worktree
- run: .harness/harness/features/FEAT-58-corpus-outside-worktree/runs/panelrecord-product/state.yaml — plan phase COMPLETE. BRIEF (11 REQ / 14 SC) and plan.yaml (16 tasks, 12 decisions) drafted, reviewed, goal-checked and panelled; panel cycle 1 recorded, severity_max high. Awaiting the operator's one batched signature review (DEC-176). Handoff: notes/handoff-plan.md
- squad: none
- status: awaiting-user

## Open Questions

- BLOCKING (panel Q1, PF-46767d8b63e7aa1a1585cd4639ff2f4c): keep T-12/D-05's gate-enforced corpus provider+ref declaration, or cut it for declaration-by-recorded-output? Cutting amends SC-14 and deletes T-12, so it must be settled before signature. pm must not touch T-12 until it is answered.
- BLOCKING (panel high finding PF-5945852660e0bd21e2b5aabb8cd48383): T-10 converges ~30 checkouts with no execution precondition on the fail-closed readers, and each worktree runs its own branch's gate copy, so the window is not closable by a dependency edge alone. Resolve by a directed fix or record an overrule; no agent may accept it.
- Panel Q2, non-blocking: T-06's `linked_worktrees` correction traces to no REQ — keep as a rider or split into its own change?
- Non-blocking: the footprint criteria carry no byte figure by design; any `du`/`df` bound is satisfied by the out-of-scope clonefile mechanism.
- Non-blocking: `lanes:` carries no row for `.claude/commands/**`, the surface T-14 now edits; `plan-merge.py` has no verb reaching a top-level key, so the routing fact sits in T-14's `execution_reason` and only the main session can add the row.
- Non-blocking, harness defects for the harness owner: `plan-merge.py` has no top-level-key verb and its `amend` re-emits a list at the wrong indent; two subagent dispatches returned exit 1 with "yield called with null data" while carrying a complete, well-formed digest.
