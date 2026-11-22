# BUG-2187 intake — pending signature

The bounded patch is specified in BRIEF.md and plan.yaml, both pending. T-01 is main-session-direct under DEC-174 (BUG-2239 routing precedent), with six owned files, three SCs and no plan-local decisions. Main alone signs. No production edits, implementation tests, panel, simplify readers or goal-check were run; the dispatch expressly excludes readers. Prototype: not required by runs/2026-11-21-01-patch-product/acceptance.md.

## Inputs and scope

- Operator-confirmed source: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-BUG-2187-review-pin-and-rework-rounds-2026-11-21.md; exclusions copied verbatim to BRIEF. Verified facts were reused, not re-derived.
- PRODUCT checkout and feature tree: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2187-review-pin-and-rework-rounds, intake HEAD 5bd9efd411a4b4a7a6a09dcf7517946c75c5f220. docs/spec.md, docs/decisions.md and docs/architecture.md are absent (docs listing contains PRINCIPLES.md and invalid-states-audit.html); task intent preserves those input pointers without inventing contents. CLAUDE.md delegates to AGENTS.md; its DEC-174 worktree rule applies.
- Consulted control-plane DEC-174, DEC-182 and DEC-225 entries via DECISIONS-INDEX.md; active unit/integration runners in .harness/harness.json. gh issue list --repo mruangutai/harness --state open --limit 100 succeeded; the four settled source issues remain open. Adjacent backlog items are not added to this patch.
- Reversible wording choices: keep existing seam order; success APPLIED pin-review <full-commit-id>, refusal REFUSED: with nonzero exit. Existing writer refusal codes remain unchanged. Judgement timestamp vocabulary is judgements[].at. No new architectural decision needs signature beyond the settled scope.

## Criterion to regression mapping

| Criterion | Carrying suite | New defect-exposing base red | Required fixed behavior and retained safety |
|---|---|---|---|
| SC-01 | tests/integration/test-check-state-records.py | Station-only plan mutation falsely emits STALE | Loaded equality excluding only root/task status, reformat acceptance, content/nested-status STALE, five silences and restored content |
| SC-02 | tests/unit/test-feature-record.py | Actual pin-review CLI is absent | HEAD/default and explicit full commit pin through shared writer; noncommit/unresolved refusal without mutation; both guidance documents name verb |
| SC-03 | tests/unit/test-feature-record.py | Recorded regate for direct fix reports zero | At/after first validate started_at, exact boundary/multiple rounds, exclusion of earlier/non-regate, fallback only for empty regate window, cycles_used unchanged |

Each SC requires authentic same-regression base-red/fix-green receipts at implementation time. Existing safety assertions need not fail at base. Neither intake gate proves those outcomes; implementation remains unverified. Future literal task verify expects both suites exit 0, no FAIL output, under 60 seconds; duration has not been measured in intake.

## Bounds and limitations

BRIEF: 44 physical lines / 120. T-01: 16 machine-field lines / 50: files 6, verify 1, traces 3, depends_on 0, change_type 1, execution_mode 1, execution_agent 0, execution_reason 1, status 1, id 1, title 1. Intent is excluded by the DEC-182 metric. Counts measured after apply. One task, no panel.

Plan apply returned APPLIED, exit 0; its automatic check-state callback reported unsigned BRIEF and missing Build-entry receipt (INV-37), pending approval and historical cycle attribution notes. These are disclosed, not repaired by unauthorized signature or feature.json mutation. No APPROVAL-RESET receipt was emitted, so no gh-sync status call was made. The required checks below both pass; the route invocation is intentionally unscoped per assignment and scans another live plan too. Their success does not approve the brief, create a Build receipt, test behavior, prove guidance adequacy or discharge any SC. Open questions: none.

## Exact required gate receipts

Working directory for both: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2187-review-pin-and-rework-rounds

Command:
```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2187-review-pin-and-rework-rounds/.harness/harness/features/BUG-2187-review-pin-and-rework-rounds/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2187-review-pin-and-rework-rounds
```
Output (exit 0; no separate stderr emitted):
```text
OK T-01 6 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2187-review-pin-and-rework-rounds/.harness/harness/features/BUG-2187-review-pin-and-rework-rounds/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2187-review-pin-and-rework-rounds: 1 task(s), 6 anchor(s) resolved, 0 failure(s)
```

Command:
```sh
python3 .claude/skills/harness/bin/check-plan-routes.py
```
Output (exit 0; no separate stderr emitted):
```text
scanning /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2187-review-pin-and-rework-rounds/.harness/*/features/*/{plan.yaml,PLAN.md}
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01: declared main-session-direct (.claude/skills/harness/references/build-phase.md, .claude/skills/harness/SKILL.md ungranted)
OK T-01: declared main-session-direct (apps/web/package.json, apps/web/tsconfig.json, apps/web/next.config.ts, apps/web/next-env.d.ts, eslint.config.mjs, apps/web/vitest.config.ts, playwright.config.ts, .node-version, .npmrc, .env.example, .gitignore ungranted)
OK T-02 granted to harness-backend-dev, harness-data-engineer, harness-dev-ops, harness-frontend-dev, harness-qa
OK T-03 granted to harness-backend-dev, harness-frontend-dev
OK T-04 granted to harness-data-engineer
OK T-05 granted to harness-backend-dev, harness-frontend-dev
OK T-06 granted to harness-backend-dev, harness-frontend-dev
OK T-07 granted to harness-backend-dev, harness-frontend-dev
OK T-08 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-09: declared main-session-direct (.harness/harness.json ungranted)
OK T-10 granted to harness-documentor
0 violation(s) across 2 plan(s)
examined 15 feature dir(s); 13 skipped as shipped
```

The invoking shell printed PLAN_CHECK_EXIT=0 and ROUTE_CHECK_EXIT=0 immediately after the respective commands.
