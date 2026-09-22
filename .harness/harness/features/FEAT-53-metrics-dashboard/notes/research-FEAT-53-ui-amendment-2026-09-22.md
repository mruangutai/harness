# FEAT-53 UI amendment — PM research receipt

The operator-signed resume ruling is applied to the approval-gated plan. T-32 is complete enough to build but remains at backlog while approval is pending; no UI implementation began.

## Binding authority and resulting plan

- Authority: `notes/answers-2026-09-22-resume-ui-lane.md`, read in full.
- Evidence amendment: `plan.yaml` D-34 records automated `ui` evidence for SC-26, SC-27, and SC-28 while preserving `uat` as the final operator gate and leaving SC-02 unchanged (`plan.yaml:330-335`).
- Build task: T-32 is assigned to `harness-frontend-dev`, traces only SC-26/27/28, depends on T-16, is `backlog`, and owns only `client/src/**` and `client/dist/**` (`plan.yaml:1914-1925`).
- Verification: T-32 requires the FEAT-53 UI lane to exit zero, the independent `ui_contract.py gate` to pass, and the complete results/WebP/trace bundle to be tracked (`plan.yaml:1926-1932`).
- Guardrails and validation: predicate and DESIGN weakening is forbidden; a wrong predicate routes to `harness-visual-designer`; QA retains `unit` and `component` and adds `ui`; UI review Mode B opens all eight T-17 traces (`plan.yaml:1933-1940`).
- Approval is pending with `reset_reason: apply T-32`; the prior signer remains historical only (`plan.yaml:6-12`). No approval verb was invoked.

## Commands and receipts

1. Task-changing mutation, using the control-plane writer:
   `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py apply --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml --proposal -`

   Exact receipt:
   `ADDED D-34`
   `ADDED T-32`
   `APPROVAL-RESET: the plan was approved and its task set or a task field changed; approval.status is pending until the main session signs again`
   `APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml`

2. Required reset mirror:
   `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/gh-sync.py status /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard plan`

   Receipt: local plan station became `plan`; issues #1787 through #1818 were mirrored to Plan.

3. Sole scoped non-test check after mutation:
   `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53`

   Scoped evidence: `OK T-32 2 anchor(s) resolved`; all 32 tasks were inspected and 125 anchors resolved. The command exited 1 only for four pre-existing missing `.claude/commands/` anchors on completed T-20/T-25; those unrelated tasks were intentionally not amended under this ruling. Existing overlap notices were likewise left unchanged.

## Scope integrity

The separate budget repair was already durable in `feature.json`: `max_total_cycles` is 50 and rework is 13 rounds / 585 minutes (`feature.json:7`, `feature.json:1153-1156`). It was intentionally untouched. No code, DESIGN.md, predicate, Checks row, BRIEF.md, automated assertion, or implementation file was edited. No formatter, linter, build, test, or project-wide validation ran.

## Principles applied

- Experience First — retained UAT as the final operator judgment rather than treating deterministic UI predicates as a substitute for the experience.
- Redesign From First Principles — integrated the lane across evidence, task verification, QA kinds, and Mode B review instead of adding an isolated frontend fix instruction.
