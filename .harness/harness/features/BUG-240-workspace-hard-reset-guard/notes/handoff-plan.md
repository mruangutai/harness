# Handoff — BUG-240-workspace-hard-reset-guard, plan → build — written at 3e3147eb, seq-1

## Next

Build BUG-240 per its signed plan: dispatch harness-eng-lead for T-01
(tests/unit/test-factory-workspace.py, red-first) then T-02
(.claude/skills/harness/bin/factory_workspace.py), per plan-task:T-01.verify.

## Trust

- BRIEF (6 REQ, 6 SC) and plan.yaml (2 tasks, panel record) are drafted and panel-reviewed —
  verified-at 3e3147eb.
- Operator signature landed on both BRIEF.md and plan.yaml — verified-at 3e3147eb
  (plan.yaml approval.status: approved).

## Dead ends

- Do not dispatch harness-visual-designer — the lead's own plan-phase decision (no end-user
  surface, one stderr refusal line) already covers this; re-litigating wastes a spawn —
  source: runs/2026-09-07-02-product/digest.md, verified-at 3e3147eb.

## Working set

- .harness/harness/features/BUG-240-workspace-hard-reset-guard/plan.yaml
- .harness/harness/features/BUG-240-workspace-hard-reset-guard/BRIEF.md
- .claude/skills/harness/bin/factory_workspace.py
- tests/unit/test-factory-workspace.py

## Done when

Scope: build BUG-240's two tasks
Authority: plan-task:T-01.verify
