# Handoff — FEAT-53-metrics-dashboard, plan → build — written at 5c52c2fb, seq-1

## Next

Enter build from the approved 2026-09-16 bundle. Record T-01 as already done at `a18d6a9f`, complete the remaining `main-session-direct` prerequisites through the main session, then dispatch the dependency-ready engineering tasks from `plan.yaml` to `harness-eng-lead` through the build team.

## Trust

- Both approval gates read `approved`; the operator re-signed the BRIEF, plan and accepted prototype as one DEC-75 bundle with rework ruling 10 rounds / 450 minutes — `BRIEF.md#Approval`, `plan.yaml:6-9`, `feature.json:rework` — verified-at 5c52c2fb
- T-01 is already implemented in the feature history and must be recorded, not repeated — commit `a18d6a9f`, `plan.yaml#T-01` — verified-at 5c52c2fb
- T-05 is completed evidence for the immutable accepted prototype, not executable build work — `plan.yaml#T-05`, `notes/prototypes/FEAT-53/README.md` — verified-at 5c52c2fb
- The binding root order is Header, Repository KPIs, then Work List; Status cards open the Work List before filters, toggle and rows — `BRIEF.md#Done when — by perspective`, `DESIGN.md` — verified-at 5c52c2fb

## Dead ends

- Do not rebuild, edit or restyle T-05's accepted prototype — `plan.yaml#T-05` — verified-at 5c52c2fb
- Do not route `main-session-direct` tasks through the build team; their `execution_mode` is the authority for the lane — `plan.yaml#Tasks` — verified-at 5c52c2fb
- Do not touch hooks, validators or gate scripts in this checkout under DEC-174; a task that still requires such a change is an escalation — signed dispatch constraint — verified-at 5c52c2fb

## Working set

- `.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml`
- `.harness/harness/features/FEAT-53-metrics-dashboard/BRIEF.md`
- `.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md`
- `.harness/harness/features/FEAT-53-metrics-dashboard/feature.json`
- `.harness/harness/features/FEAT-53-metrics-dashboard/STATE.md`

## Done when

Scope: Enter the approved build and start the dependency-ready implementation lanes
Authority: brief-perspective:.harness/harness/features/FEAT-53-metrics-dashboard/BRIEF.md#operator (dashboard `/`)
Authority: plan-task:T-01.verify
Authority: approval:.harness/harness/features/FEAT-53-metrics-dashboard/BRIEF.md#Approval
