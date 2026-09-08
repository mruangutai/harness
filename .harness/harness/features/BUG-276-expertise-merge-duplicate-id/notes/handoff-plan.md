# Handoff — BUG-276-expertise-merge-duplicate-id, plan → build — written at 7f924326, seq-1

## Next

Build BUG-276 per its signed plan: dispatch harness-eng-lead for T-01 then T-02, per
plan-task:T-01.verify. expertise-merge.py's apply --entries union path should refuse a
duplicated section+id within one incoming proposal at exit 11 (matching the existing
ops-path exit-11 CONFLICT convention) instead of silently keeping only the last-seen entry.

## Trust

- BRIEF (4 REQ, 6 SC) and plan.yaml (2 tasks, 9 decisions, panel record) are drafted and
  panel-reviewed — verified-at 7f924326.
- Operator signature landed on both BRIEF.md and plan.yaml — verified-at 7f924326.

## Dead ends

- Do not touch check-expertise.sh — D-04 keeps the fix scoped to expertise-merge.py alone;
  the format checker is structurally blind here because the drop precedes the write —
  source: plan.yaml decisions, verified-at 7f924326.

## Working set

- .claude/skills/harness/bin/expertise-merge.py
- tests/integration/test-expertise-merge.py
- .harness/harness/features/BUG-276-expertise-merge-duplicate-id/plan.yaml
- .harness/harness/features/BUG-276-expertise-merge-duplicate-id/BRIEF.md

## Done when

Scope: build BUG-276's two tasks
Authority: plan-task:T-01.verify
