# Handoff — BUG-240-workspace-hard-reset-guard, validate → ship — written at bae47f3c, seq-1

## Next

Ship BUG-240 via `gh-sync.py ship .harness/harness/features/BUG-240-workspace-hard-reset-guard`
(already executed by the main session; this note documents the validate → ship seam that
could not get a normal handoff note when it was crossed, per the known worktree handoff
defect recorded in STATE.md Open Questions Q4).

## Trust

- The cycle-1 re-panel over the fixed pin passed, must_fix empty, 39/39 checks re-measured —
  verified-at bae47f3c (runs/2026-09-07-03-validator/digest.md).
- Two low-severity findings (PF-d795aab03bf4a49e7ef3ef6614024cdf,
  PF-ff733189ddbdfca901c0d587800cb8c4) were kept as recorded by the operator at signature,
  no ruling needed — verified-at bae47f3c (plan.yaml).

## Dead ends

- Do not re-open F-PANEL-01 — resolved on two independent chains at cycle 1 — source:
  runs/2026-09-07-03-validator/digest.md, verified-at bae47f3c.

## Working set

- .harness/harness/features/BUG-240-workspace-hard-reset-guard/STATE.md
- .harness/harness/features/BUG-240-workspace-hard-reset-guard/plan.yaml
- .claude/skills/harness/bin/factory_workspace.py

## Done when

Scope: ship BUG-240
Authority: approval:.harness/harness/features/BUG-240-workspace-hard-reset-guard/plan.yaml#approval
