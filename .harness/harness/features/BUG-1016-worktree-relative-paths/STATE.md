# STATE

## Current

- feature: BUG-1016-worktree-relative-paths
- run: t02-docs-product (PENDING, opened, never dispatched — host blocked the `task` tool)
- squad: product
- status: blocked
- mission: plan
- station: building
- verdict: none
- approval: BRIEF approved, plan.yaml approved (2026-10-04, molchairuangutai; rework 2 rounds / 90 min)
- T-01: done (main-session-direct, commit 10f38a42; receipts notes/t01-receipts-main-session.md, verify 123/0 per main session)
- T-02: building (plan.yaml station building; gh-sync start-task #2018 recorded); run t02-docs-eng closed BLOCKED 0 cycles (misrouted to eng squad, undispatched; documentor is product)
- handoff: notes/handoff-plan.md written at 17fd638b, seq-3; succession continue recorded on t02-docs-eng run-start
- github: build_entry opened; station building on #1016 #1570 #2016 #2017 #2018
- cycles_used: 0/10
- review_sha: none
- next: dispatch t02-docs-product to harness-product-lead (documentor, DEC-251) once the host lets this orchestrator call `task`; then simplify (eng-lead), seam commit, pin review_sha, status review, validate

## Open Questions

- Q1 (harness defect, non-blocking): governed `write agent://<peer>` and `write xd://report_issue` were refused by check-domain as filesystem paths `agent:/`, `xd:/` in two squads during plan — BUG-2003's scheme pass-through is not reaching the gate for the live hook. Harness owner to triage.
- Q3 (blocking, host): every `task` call from this orchestrator (Bug1016Build, resumed via IRC after T-01) is refused by the live hook with "Harness requires OMP's runtime lineage capability" — `tool_call` sees `runtimeAgentId` empty (harness-hooks.ts ~L1052), so no lead can be spawned. Main session to re-dispatch the orchestrator in a session where `before_agent_start` carries `ctx.agent.id`, or triage the hook.
