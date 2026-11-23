# BUG-2420 — pending patch ready for signature

BRIEF.md and plan.yaml encode the settled first-station repair without implementation. One T-01 owns stations.py, the existing integration script and a new focused unit script. Three SCs cover the three-row unit contract, signed approval byte preservation and the apply-to-first-station integration path. No UAT is required. decisions and decisions_affected are empty: this implements existing policy, not an amendment.

## Binding inputs and findings

- Binding grilling: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-plan-merge-first-task-station-2026-11-22.md, especially Settled; its verified reproduction at 9eb07b4f was accepted without rerunning.
- Precedent read from control-plane BUG-2349 BRIEF.md, plan.yaml and its worktree source tests/unit/test-plan-merge-union-head.py: adopt pinned red/green receipts and intentional writer-test environment isolation, not its signature or union tests.
- Assigned product checkout docs/spec.md, docs/decisions.md and docs/architecture.md are absent. CLAUDE.md points to AGENTS.md; both were consulted. No substitute product documents were invented.
- Actual gate: .claude/skills/harness/bin/code_grade.py _record assigns production bar 4 and test bar 3 using configured test-kind detection. code-grade.py supports paired --base/--head and --json. Its exit status alone allows grade-2 advisories; verify explicitly asserts every changed function meets its bar, with no ungraded files and a nonempty graded set.
- .harness/harness.json bugfix runtime predicate requires unit. Active unit and integration kinds discover the chosen test directories. Unresolved component/ui and TypeScript checking do not cover this patch.
- .github/workflows/tests.yml checks include unit, routes and the canonical-reader audit; integration shards feed the required aggregation. The literal task verify includes focused unit/integration scripts, scoped routes, strict diff grades and the exact python3 .agents/skills/harness/bin/check-plan-routes.py --canonical-reader-audit command. Full configured runners remain validate/CI obligations.
- DEC-174 overrides the generic patch team route. DEC-225 omits readers, panel and goal-check. Source scope excludes adjacent cleanup, production documentation, apply behavior changes and the blocked feature's content.

## Controlled write and check receipt

plan-merge.py apply was invoked from the current control plane with an stdin proposal, not a temporary file. It emitted APPLIED for this feature plan, exit 0; no APPROVAL-RESET receipt and no gh-sync call. Automatic writer feedback reported the intentionally pending BRIEF, absent Build-entry receipt and historical run attribution; these are not evidence of an approved or built feature.

Required command:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station
```

Exact output and exit status:

```text
OK T-01 3 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station/.harness/harness/features/BUG-2420-plan-merge-first-task-station/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2420-plan-merge-first-task-station: 1 task(s), 3 anchor(s) resolved, 0 failure(s)
EXIT STATUS: 0
```

On-disk confirmation: plan.yaml approval.status is pending; top-level status is plan; source_issues is [2420]; T-01.execution_mode is main-session-direct and T-01.status is ready. The seeding proposal explicitly supplied ready. BRIEF Approval remains pending. No temporary proposal was created. No implementation, tests, builds, linters, formatters, smoke runs, readers, panel or goal-check were executed.

## Principles applied

- Redesign From First Principles: operator and maintainer perspectives include first-station and preservation outcomes together, rather than adding a workaround perspective for the blocked feature.

## Open questions

None. Main must obtain signature before eventual tests-first execution; the pending artifacts do not claim any SC already delivered.
