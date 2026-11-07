# Patch intake assessment — BUG-2141

Pending BRIEF and one-task plan are ready for operator signature. Implementation, tests, panel and goal-check were not run. BRIEF has 46 lines (wc -l, exit 0); plan station is plan, source_issues is [2141], and plan-merge seeded pending approval. No feature.json changes.

## Scope and source evidence

- Settled operator decision: https://github.com/mruangutai/harness/issues/2141; open backlog read with gh issue list --repo mruangutai/harness --state open --limit 100 (exit 0). Other issues remain outside this patch.
- DECISIONS-INDEX.md DEC-120 points to the ordinary thin layer-0 channel; DECISIONS.md DEC-174 supplies the enforcement carve-out. Task reconciles them with a cross-reference, not a new organization.
- dispatch-guard.py omp_main already recognizes the trusted OMP Main identity; resolved root/repository precedes _start_preflight and live_claim. The new refusal consumes handoff_policy.exempt_reason, whose _all_direct already owns nonempty all-direct classification. No helper changes are planned.
- Existing regression sources: tests/unit/test-lead-start-preflight.py uses isolated_bin and disposable registered checkouts; tests/integration/test-dispatch-guard.py exercises real subprocess payloads and private claim fixtures. T-01 owns both and all five documentation/production files; it traces all four SCs.
- Existing ledger authority: .claude/skills/harness/references/ledger.md. Header authority: harness-zero-micro-management. AGENTS.md Organization and .omp/commands/harness.md are the bounded entrypoint changes.
- Routing baseline: origin/main resolved to 0b17e9bbf7ef4baafa0eb0844ec0edbb753dd86f. Implementation must freshly pin origin/main and preserve real fail-first receipts before production edits; intake does not supply that evidence.

## Authorized intake checks

Commands below use the read-only control-plane tools; PLAN means the absolute file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2141-dec174-main-orchestrator/.harness/harness/features/BUG-2141-dec174-main-orchestrator/plan.yaml.

1. Exact command: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2141-dec174-main-orchestrator/.harness/harness/features/BUG-2141-dec174-main-orchestrator/plan.yaml --root /Users/molchairuangutai/GitHub/harness
   Result: exit 0; OK T-01 7 anchor(s) resolved; CHECK reports 1 task, 7 anchors, 0 failures.
2. Exact command: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-plan-routes.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2141-dec174-main-orchestrator/.harness/harness/features/BUG-2141-dec174-main-orchestrator/plan.yaml
   Result: exit 0; owner manifest used; OK T-01 declared main-session-direct (AGENTS.md, .omp/commands/harness.md ungranted); 0 violations across 1 plan.

Plan apply exited 0 and printed APPLIED, with no APPROVAL-RESET receipt. Its automatic changed-state check disclosed unsigned BRIEF and missing github.build_entry INV-37; these are pending-intake/later-main lifecycle conditions, not a claim that state is merge-ready. No remote sync or approval was attempted. A preliminary check-plan-routes.py --help exited 2 because this script treats arguments as plan paths; corrected scoped invocation above passed.

## Assessment

Bounded seven-file patch, one main-session-direct task, no new interface. Four SCs: two pinned-content inspections and two future automated outcomes. Active unit/integration kinds cover the actual test paths; unrelated null runners are not claimed as evidence. No UAT needs the operator personally beyond the pending signature. No new D-NN: issue #2141 already settles the choice. Open questions: none.
