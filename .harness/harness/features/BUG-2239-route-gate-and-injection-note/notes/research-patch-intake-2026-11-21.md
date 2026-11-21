# Pending patch intake — BUG-2239 / #2240

Ready for operator signature, not implementation: BRIEF is 49 lines; plan approval is pending; T-01 is bugfix, main-session-direct, 18/50 machine-field lines, six exact owned paths, traces SC-01 through SC-05. No new D-NN choice meets the hard-to-reverse bar. Exact note wording is fixed in BRIEF SC-02 and task intent. Proposed rework: 1 round, 45 minutes; no ruling recorded.

## Scope and sources

The settled source is /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-BUG-2239-route-gate-and-injection-note-2026-11-21.md, Settled and Facts I verified; causes were not re-derived. Send-back requirements: runs/2026-11-21-01-patch-product/digest.md. T-01 owns only plan_merge/check.py, harness-hooks.ts and the four named tests. No rules, CI, sign-approval, BUG-2171 refusal text or #2241 changes; no implementation, tests, panel or goalcheck performed. Existing product guidance: AGENTS.md project map and .harness/harness/docs/SPEC.md dispatch contract/plan declaration. Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent; no substitutes invented. Backlog read from configured mruangutai/harness confirms #2239 and #2240; #2241 stays separate. An initial repository-name guess failed and was corrected using harness.json github.repo.

Unit/integration runners cover the named test paths. The unresolved typecheck null runner is disclosed at signature; unit runtime assertions do not claim static type correctness. Every verification-created durable fixture/run/feature plan must mint a fresh identity. No SC requires personal UAT. Regression outcomes remain unmeasured until direct implementation and QA; intake gates alone do not discharge any SC.

## Exact gate receipts

Invocation 1: python3 /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2239-route-gate-and-injection-note/.claude/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2239-route-gate-and-injection-note/.harness/harness/features/BUG-2239-route-gate-and-injection-note/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2239-route-gate-and-injection-note

Exit 0; stdout (2 lines), stderr empty:

```text
OK T-01 6 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2239-route-gate-and-injection-note/.harness/harness/features/BUG-2239-route-gate-and-injection-note/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2239-route-gate-and-injection-note: 1 task(s), 6 anchor(s) resolved, 0 failure(s)
```

Invocation 2: python3 /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2239-route-gate-and-injection-note/.claude/skills/harness/bin/check-plan-routes.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2239-route-gate-and-injection-note/.harness/harness/features/BUG-2239-route-gate-and-injection-note/plan.yaml

Exit 0; stdout (3 lines), stderr empty; zero VIOLATION:

```text
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01: declared main-session-direct (.omp/extensions/harness-hooks.ts ungranted)
0 violation(s) across 1 plan(s)
```

The control-plane plan-merge.py check was also invoked with identical file/root arguments: exit 0, identical two output lines. Control-plane interfaces were consulted first: check-plan-routes accepts positional plan files, not --help (the discovery attempt exited 2 and printed MANIFEST plus ERROR: --help does not exist). That failed interface probe was not a plan gate result.

## Rework and write receipts

Control-plane feature-record.py propose-rework --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2239-route-gate-and-injection-note/.harness/harness/features/BUG-2239-route-gate-and-injection-note/feature.json returned exit 0:

```json
{"rounds": 1, "minutes": 45, "basis": "patch mission: 1 round; 45 min per round (budgets.rework_round_minutes)"}
```

Plan created only through control-plane plan-merge.py apply; stdout ended APPLIED with no APPROVAL-RESET receipt, so no remote reset call was made. Its changed-state advisory reported unsigned BRIEF and absent Build-entry receipt; both belong to the later explicit signature, not authority for this agent to approve or edit feature.json. Count measured using the canonical _budget_lines: 18; approval mapping contains only status: pending. A first count probe incorrectly called nonexistent harness_yaml.load_plan; corrected measurement used YAML loading and the canonical budget function. Temporary merge proposal removed. Feature.json and STATE.md were not edited.

## Principles applied

- Redesign From First Principles: integrate both remedies into operator/maintainer outcomes and the existing processor/task-return seams, rather than add parallel rules or a separate notification mechanism.

## Open questions

None. Pending user signature is intentional; regression red/green evidence belongs to the direct implementation and validation phase.
