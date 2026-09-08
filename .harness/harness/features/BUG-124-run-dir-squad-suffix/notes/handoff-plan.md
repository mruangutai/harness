# Handoff — BUG-124-run-dir-squad-suffix, plan → build — written at 80ce35d1, seq-1

## Next

Build BUG-124 per its signed plan: dispatch harness-eng-lead for T-01 then T-02
(dispatch-guard.sh refuses a run-dir slug matching no callee grant), per
plan-task:T-01.verify. T-03 (SKILL.md docs) is main-session-direct, deferred to after
build closes.

## Trust

- BRIEF and plan.yaml (cycle-1 revision, 3 prior high findings closed) are panel-PASS at
  severity_max med — verified-at 6dc3c0e2.
- Operator signature landed on both, with 5 findings explicitly overruled in
  approval.rulings — verified-at 80ce35d1.

## Dead ends

- Do not re-litigate D-01's callee-independent rule — already accepted at signature, with
  the disclosure line in BRIEF.md — source: plan.yaml decisions, verified-at 80ce35d1.

## Working set

- .harness/harness/features/BUG-124-run-dir-squad-suffix/plan.yaml
- .claude/skills/harness/bin/dispatch-guard.sh
- .harness/team-config.yaml

## Done when

Scope: build BUG-124's tasks
Authority: plan-task:T-01.verify
