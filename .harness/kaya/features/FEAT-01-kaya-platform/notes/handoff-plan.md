# Handoff — FEAT-01-kaya-platform, plan → build — written at 6edceab0, seq-10

## Next

Nothing dispatches until the operator reviews revision c2 and signs. Main updates Kaya issue #14 from this revision, presents BRIEF.md + plan.yaml (10 tasks, D-01/D-02, panel cycle 2) + DESIGN.md + the interactive prototype once; on `plan-merge.py sign-approval --rework rounds=N,minutes=M --decision <path>` the build successor runs `gh-sync.py open` (build_entry receipt) then `gh-sync.py status <feature-dir> building`, and executes T-01 main-session-direct (plan-task:T-01.verify) before any team dispatch — T-02 (harness-qa) is the first squad task and depends on T-01.

## Trust

- plan.yaml passes `plan-merge.py check --file <feature-dir>/plan.yaml --root <PLANNING> --code-root <CODE>`: 10 tasks, 57 anchors, 0 failures, no OVERLAP — runs/2026-10-05-8-simplify-product/digest.md and the orchestrator's own re-run — verified-at 6edceab0 (CODE 6303f9f)
- Reader panel c2: scope FAIL high applied (notes/review-harness-code-reviewer-plan-c2.md), design FAIL high/med/low applied (notes/review-harness-ui-reviewer-plan-c2.md), should-not-exist SKIPPED (fable-advisor unavailable); all five PF resolved — plan.yaml `panel:` — verified-at 6edceab0
- Goalcheck: operator pass, code maintainer pass against intake PLUS notes/answers-thin-chat-review-2026-10-05.md; all ten SCs not_met until build/UAT — notes/research-FEAT-01-kaya-platform-goalcheck-plan.md — verified-at 6edceab0
- Simplify c2 four angles ran read-only; F01/F02/F04/F05/F08/F12 applied, F03/F09/F10 backlog rows, F06/F07/F11 left — runs/2026-10-05-7-simplify-eng/digest.md, notes/research-FEAT-01-kaya-platform-simplify-apply-c2.md — verified-at 6edceab0
- DESIGN.md is a real contract; needs_prototype true; prototype served at http://127.0.0.1:4179/ with screenshots/DOM under notes/prototypes/FEAT-01-kaya-platform/ — notes/mockups/design-thin-chat-c2-apply.md — verified-at 6edceab0
- Lane routing: NOBODY/SHARED paths (root config, apps/web package/next/tsconfig, .env.example, root Playwright config, .harness/harness.json) are main-session-direct T-01/T-09 — plan.yaml `lanes:` — verified-at 6edceab0
- Researched pins (Next 16.3.8, @mastra/* 1.74/1.35/1.29, @mastra/ai-sdk 1.10.6, ai 6.0.116, @ai-sdk/react 3.0.118, Astryx 0.6.5, Playwright 1.63.0, claude-sonnet-5-5) are research, not exercised compatibility — BRIEF.md `## Constraints`, notes/research-FEAT-01-kaya-platform-draft-plan-c2.md — UNVERIFIED

## Dead ends

- Opening an eng-lead run with `--squad eng` leaves its typed return unbindable; `engineering` binds — runs/2026-10-05-3-simplify-eng (refused-return) vs runs/2026-10-05-7-simplify-eng (sealed) — verified-at 6edceab0
- A plan-team run whose readers return FAIL with findings applied in-run is forced to team FAIL by validate-digest worst-member rule — feature.json runs 2026-10-05-2-plan-product and 2026-10-05-6-plan-product, judgement finding_kind — verified-at 6edceab0
- Product plan check needs `--code-root <CODE worktree>`; `--root <CODE>` exits 2 and `--root <PLANNING>` alone fails every greenfield anchor — notes/ship-review-2026-10-05-1-plan-product.md — verified-at 6edceab0
- Harness task dispatches refuse `outputSchema`/`schemaMode` on a governed task intermittently (accepted for runs 6 and 7, refused for run 8) — orchestrator return open_questions — verified-at 6edceab0

## Working set

- .harness/kaya/features/FEAT-01-kaya-platform/plan.yaml
- .harness/kaya/features/FEAT-01-kaya-platform/BRIEF.md
- .harness/kaya/features/FEAT-01-kaya-platform/DESIGN.md
- .harness/kaya/features/FEAT-01-kaya-platform/notes/uat-browser-c2.md
- .harness/kaya/features/FEAT-01-kaya-platform/notes/answers-thin-chat-review-2026-10-05.md

## Done when

Scope: operator signature recorded on revision c2, then T-01 landed main-session-direct
Authority: brief-perspective:.harness/kaya/features/FEAT-01-kaya-platform/BRIEF.md#operator
Authority: approval:.harness/kaya/features/FEAT-01-kaya-platform/BRIEF.md#Approval
Authority: plan-task:T-01.verify
