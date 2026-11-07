# BUG-2161 — simplify apply

PASS: both consolidated task-scope findings are folded into T-01.intent; the required structural check exited 0.

- Input: runs/2026-11-02-03-simplify-plan-eng/digest.md, F-01 and F-02.
- F-01: explicitly reuse _feature_station to guard _record_station on already-abandoned re-entry; preserve D-02/SC-04's actual no-rewrite requirement and retained-runs pruning.
- F-02: explicitly generalize _post_abandon_reason and _report_abandon_gaps in place for source targets from the existing plan/executor, not a parallel reporter. Reporting must remain consistent for source comments without a parent; original reason_file argument and settled order remain intact.
- Read inputs: BRIEF.md; PRODUCT AGENTS.md; mapped SPEC.md sections 9 and 11; DECISIONS.md DEC-138, DEC-203 section 8 and DEC-238; existing gh-sync.py helpers at _feature_station, _post_abandon_reason and _report_abandon_gaps.
- Mutation: control-plane plan-merge.py apply, proposal containing only T-01.id and T-01.intent; exit 0, REPLACED T-01.intent and APPLIED receipts. No APPROVAL-RESET receipt; no remote sync performed.
- Preserved: BRIEF and all seven SCs; D-01 through D-03; existing panel including cycle 0; both tasks, file anchors, verify commands, routing and operator constraints. Approval remains pending; no approval writes. No scope change, new task, panel, goal-check or implementation.

## Verification

Exact assigned command:

    python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2161-abandon-source-tickets/.harness/harness/features/BUG-2161-abandon-source-tickets/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2161-abandon-source-tickets

Exit status: 0. Output: T-01 3 anchors resolved; T-02 2 anchors resolved; 2 tasks, 5 anchors, 0 failures.

Apply's automatic check-state hook separately reported unsigned BRIEF and absent github.build_entry, plus pending-plan and absent-run notes. These are not a structural-check failure or permission to sign/open/build; no remediation attempted in this bounded specification edit. No builds, tests, linters, formatters or implementation verify commands ran.

Files touched: plan.yaml and this research artifact, both inside this feature directory. Open questions: none.
