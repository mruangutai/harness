# T-03 residual split amendment — applied

## Conclusion

The operator-approved residual split is applied to the governed plan. T-08 through T-13 are ready, parallel team tasks that depend only on T-03. The normal add-tasks lifecycle reset moved approval to pending and feature status to plan; Main must re-sign from notes/answers-fix-c3-split.md with cumulative rework 7 rounds and 315 minutes.

## Governed mutations

- plan-merge.py add-tasks added exactly T-08 through T-13 and emitted the expected APPROVAL-RESET receipt.
- T-08 solely owns feat-53.e2e.spec.ts trimming to SRC-TOKENS, VIS-DENSITY, and VIS-PROTOTYPE plus e2e/geometry.e2e.spec.ts for C1-HEADER-GEOMETRY and KPI-R1.
- T-09 through T-12 each solely own their ruled e2e spec and check pair, except T-10, which owns C3-KEYBOARD alone.
- T-13 is routed to harness-backend-dev and solely owns ui-reporter.probe.spec.ts plus ui-reporter.ts. Its intent requires all seven named cases and requires both a failing ui-reporter summary and ui_contract.py gate refusal for every case.
- The five browser task verifies list only their owned specs and require contributions of 9, 4, 2, 4, and 4 tests, respectively, which compose to the unchanged exact total of 23.
- plan-merge.py record-amendments removed the two transferred files from T-03 ownership, replaced T-03's signed intent with the delivered-versus-residual boundary, and appended one amendment judgement per changed field to feature.json. Both ledger reasons cite notes/answers-fix-c3-split.md.

## Scoped check

The scoped command was:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane
```

With the ruled future e2e parent present for new-file resolution, the check resolved all T-08 through T-13 anchors and reported no overlap or route failure for any new task. It resolved 26 anchors overall. Its sole failure remains the pre-existing T-05 anchor .claude/agents/harness-ui-reviewer.md because that directory is absent; the prior blocked artifact recorded the same baseline failure, and this amendment did not change T-05.

## Result

- Plan: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/plan.yaml
- Approval: pending solely from the governed add-tasks reset
- Feature station: plan, with resume station building
- BRIEF, DESIGN, success criteria, and production code: unchanged
