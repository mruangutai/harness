# Handoff — BUG-1129-validate-handoff-sweep, plan → build — written at 142026456c64c80c3dd3aa776636dadbc0e21881, seq-1

## Next

The main session records the operator's approval and rework ruling, then executes T-01 as the single `main-session-direct` build segment before validation.

## Trust

- The pending BRIEF states the four operator and maintainer outcomes — .harness/harness/features/BUG-1129-validate-handoff-sweep/BRIEF.md — UNVERIFIED
- The one-task patch plan names all seven required implementation anchors and traces SC-01 through SC-04 — .harness/harness/features/BUG-1129-validate-handoff-sweep/plan.yaml — UNVERIFIED
- The product run completed in one PM pass with zero send-backs — .harness/harness/features/BUG-1129-validate-handoff-sweep/runs/plan-product/digest.md — UNVERIFIED

## Dead ends

- Do not move the guard into post-merge-sweep.py alone; cmd_ship is the shared writer boundary — /tmp/grilling-1129.md — UNVERIFIED
- Do not sign either approval surface from a governed agent; approval belongs to the main session — .harness/harness/features/BUG-1129-validate-handoff-sweep/BRIEF.md — UNVERIFIED

## Working set

- .harness/harness/features/BUG-1129-validate-handoff-sweep/BRIEF.md
- .harness/harness/features/BUG-1129-validate-handoff-sweep/plan.yaml
- .harness/harness/features/BUG-1129-validate-handoff-sweep/feature.json
- .harness/harness/features/BUG-1129-validate-handoff-sweep/runs/plan-product/digest.md

## Done when

Scope: T-01 main-session-direct build segment
Authority: brief-perspective:.harness/harness/features/BUG-1129-validate-handoff-sweep/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-1129-validate-handoff-sweep/BRIEF.md#code maintainer
Authority: plan-task:T-01.verify
