# Handoff — FEAT-01-kaya-platform, plan → build — written at ac237916, seq-7

## Next

Nothing dispatches until the operator signs. Main presents BRIEF.md + plan.yaml (10 tasks, D-01/D-02, panel PF-86e4a4c3 applied) once; on `plan-merge.py sign-approval --rework rounds=N,minutes=M --decision <path>` the build successor runs `gh-sync.py open` (build_entry receipt) then `gh-sync.py status <feature-dir> building`, and executes T-01 main-session-direct (plan-task:T-01.verify) before any team dispatch — T-02 (harness-qa) is the first squad task and depends on T-01.

## Trust

- plan.yaml passes `plan-merge.py check --file <feature-dir>/plan.yaml --root <PLANNING> --code-root <CODE>`: 10 tasks, 41 anchors, 0 failures — runs/2026-10-05-5-simplify-product/digest.md and the orchestrator's own re-run — verified-at ac237916 (CODE 6303f9f)
- Reader panel: scope PASS (notes/review-harness-code-reviewer-plan-c1.md), design FAIL med applied in-run (notes/review-harness-ui-reviewer-plan-c1.md, PF-86e4a4c3), should-not-exist SKIPPED (fable-advisor unavailable) — plan.yaml `panel:` — verified-at ac237916
- Goalcheck: operator pass, code maintainer pass against the whole intake — notes/research-FEAT-01-kaya-platform-goalcheck-plan.md — verified-at ac237916
- Simplify four angles ran read-only; R-1, R-2/F-2, S-1, F-1 applied, E-1 skipped — runs/2026-10-05-4-simplify-eng/digest.md, notes/research-FEAT-01-kaya-platform-simplify-apply.md — verified-at ac237916
- Lane routing of every planned path measured with check-domain.py --resolve against CODE; NOBODY paths (apps/web/package.json, apps/web/next.config.ts, apps/web/tsconfig.json, .env.example, .harness/harness.json) and SHARED root package.json are main-session-direct T-01/T-09 — plan.yaml `lanes:` — verified-at ac237916
- Candidate versions (Next 16.3.8, @mastra/* 1.74/1.35/1.29, @ai-sdk/anthropic 3.0.103, pg 8.23.1, Node 24, pnpm 11.2.2, claude-sonnet-5-5) are research, not exercised compatibility — BRIEF.md `## Constraints` — UNVERIFIED

## Dead ends

- Opening an eng-lead run with `--squad eng` (team-config's name) leaves its typed return unbindable: digest_destination.py LEAD_SQUADS maps harness-eng-lead to `engineering` — runs/2026-10-05-3-simplify-eng (refused-return) vs runs/2026-10-05-4-simplify-eng (sealed) — verified-at ac237916
- A plan-team run whose design reader returns FAIL (finding applied in-run) is forced to team FAIL by validate-digest worst-member rule, and check-state then demands a cycle for it — feature.json run 2026-10-05-2-plan-product, judgement finding_kind — verified-at ac237916
- Product plan check needs `--code-root <CODE worktree>`; `--root <CODE>` exits 2 and `--root <PLANNING>` alone fails every greenfield anchor — notes/ship-review-2026-10-05-1-plan-product.md — verified-at ac237916

## Working set

- .harness/kaya/features/FEAT-01-kaya-platform/plan.yaml
- .harness/kaya/features/FEAT-01-kaya-platform/BRIEF.md
- .harness/kaya/features/FEAT-01-kaya-platform/feature.json
- .harness/kaya/features/FEAT-01-kaya-platform/runs/2026-10-05-2-plan-product/digest.md
- .harness/notes/grilling-kaya-platform-2026-10-05.md

## Done when

Scope: operator signature recorded, then T-01 landed main-session-direct
Authority: brief-perspective:.harness/kaya/features/FEAT-01-kaya-platform/BRIEF.md#operator
Authority: approval:.harness/kaya/features/FEAT-01-kaya-platform/BRIEF.md#Approval
Authority: plan-task:T-01.verify
