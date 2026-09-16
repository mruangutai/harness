# Handoff — BUG-240-workspace-hard-reset-guard, build → validate — written at bae47f3c, seq-1

## Next

Ship BUG-240 once its PR merges: `gh-sync.py ship
.harness/harness/features/BUG-240-workspace-hard-reset-guard`. Validate is already complete
(cycle-1 panel PASS at the fixed pin, must_fix empty) — this note documents the build seam
that could not get a normal handoff note when it was crossed (worktree handoff defect, see
STATE.md Open Questions Q4).

## Trust

- T-01 and T-02 landed, both verified independently against their own `verify:` commands
  (not trusted from receipts alone) — verified-at 6cd80e1b.
- The blocking qa gate passed, 39/39 checks — verified-at d5a9f60b.
- A real HIGH finding found at validate (self-checkout guard compared realpath as raw
  strings; case-mismatch could hard-reset the control-plane checkout) was fixed and the
  fix independently re-verified — verified-at bae47f3c.
- The cycle-1 re-panel over the fixed pin returned PASS, must_fix empty — verified-at
  bae47f3c (runs/2026-09-07-03-validator/digest.md).

## Dead ends

- Do not re-open F-PANEL-01 — it is RESOLVED on two independent chains at cycle 1, not
  merely dismissed — source: runs/2026-09-07-03-validator/digest.md, verified-at bae47f3c.

## Working set

- .harness/harness/features/BUG-240-workspace-hard-reset-guard/STATE.md
- .harness/harness/features/BUG-240-workspace-hard-reset-guard/plan.yaml
- .claude/skills/harness/bin/factory_workspace.py
- tests/unit/test-factory-workspace.py

## Done when

Scope: ship BUG-240 once its PR merges
Authority: approval:.harness/harness/features/BUG-240-workspace-hard-reset-guard/plan.yaml#approval
