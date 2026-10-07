# Plan correction — FEAT-2081

The pending plan now follows the corrected brief: T-03 and T-06 carry SC-06/SC-10 evidence through the structure test's in-process calls and the consolidation-audit CLI. No real check-state audit entry or unresolved real-entry prerequisite is required; wiring one remains out of scope. BRIEF.md and approval were not edited.

## Task summary

- T-01 — Add deterministic weighted suite sharding and completed-file manifests — SC-01, SC-07, SC-08 — main-session-direct.
- T-02 — Validate shard conclusions against independent tested-commit discovery — SC-02, SC-03, SC-05 — main-session-direct.
- T-03 — Dispatch all structure rules from one fresh per-file AST index — SC-06, SC-08, SC-10 — main-session-direct.
- T-04 — Parallelize integration jobs without weakening the required context — SC-02, SC-03, SC-04, SC-05, SC-09, SC-10 — main-session-direct.
- T-05 — Document the shipped sharding and required-check contract — SC-01, SC-04, SC-05, SC-07, SC-08 — team: harness-documentor.
- T-06 — Prepare the throwaway-PR UAT and pinned performance record — SC-04, SC-05, SC-06, SC-09, SC-10 — main-session-direct.

## Evidence

- Control-plane plan-merge.py check against the feature worktree: exit 0; six tasks, 19 anchors, zero failures.
- Control-plane check-plan-routes.py with this plan's absolute file path: exit 0; zero violations across one plan. Declared main-session deviations remain expected DEC-174/direct routing.
- Amendment receipts retained pending approval. Their automatic scoped check-state output reports unsigned BRIEF and INV-37; these are expected draft-state notices, not failed plan checks. Per settled OQ-04, Main runs gh-sync.py open after the user signs the plan; no GitHub command was attempted here.

## Open questions

None. User approval is still required; SC outcomes were not evaluated by this planning correction.
