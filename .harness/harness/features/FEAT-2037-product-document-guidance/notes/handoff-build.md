# Handoff — FEAT-2037-product-document-guidance, build → validate — written at 50ab19ab (pin commit 17c3cd5b), seq-7

## Next

Once STATE.md Q-08 (main checkout fast-forwarded past 37cfcfd4 and hooks reloaded) and Q-09 (BRIEF `## Verification gaps` bullet reworded under an operator ruling) are closed, re-pin if the BRIEF commit moved plan bytes (it does not; BRIEF is not plan.yaml, so the pin 17c3cd5b stands unless the four production paths move) and dispatch ONE `validate` team to `harness-validator-lead` (run id `validate-c1-validator`, `--squad validator`) over `review_sha` 17c3cd5b: qa (gate-only; under #2131 QA may PASS with fail_first [] because every SC is uat/inspection), code, security, ui (self-scopes out), pm goalcheck (`notes/research-FEAT-2037-product-document-guidance-goalcheck-validate-c1.md`). SC-04 is re-inspected at 17c3cd5b: upstream edits to harness-spec-driven/SKILL.md and SPEC.md merged in since the c0 inspection at 1e69bf14. SC-01..SC-03 are operator-only UAT, NOT RUN, graded unproven.

## Trust

- simplify-c1-eng PASS, zero accepted findings, no production edits — runs/simplify-c1-eng/digest.md, notes/receipt-harness-ai-dev-simplify-c1-eng-{reuse,simplification,altitude}.md, notes/receipt-harness-dev-ops-simplify-c1-eng-efficiency.md — verified-at 17c3cd5b
- T-01 diff 37cfcfd4..17c3cd5b on the four paths is 4 files +33/-3, unchanged since 1e69bf14 — `git diff --stat 37cfcfd4 17c3cd5b -- <four paths>` — verified-at 17c3cd5b
- eng-lead binding needs run `squad: engineering` (digest_destination.LEAD_SQUADS); `eng` yields the "no trusted hook-owned digest binding" refusal — feature.json runs simplify-eng vs simplify-c1-eng — verified-at 17c3cd5b
- T-01 signed hash f5538093…671b unchanged; plan approval approved; plan.yaml status review — feature.json, plan.yaml — verified-at 17c3cd5b

## Dead ends

- Any must_fix routes to MAIN: all four production paths resolve NOBODY/main-session-direct; no fix run can edit them — plan.yaml T-01 execution_mode — verified-at 17c3cd5b
- Dispatching validate before Q-08/Q-09 reproduces QA ESCALATE: host validate-digest.py (main checkout, pre-#2131) refuses PASS + fail_first []; the #2131 copy fails closed on the BRIEF's `- SC-01–SC-03 are NOT RUN YET.` bullet — STATE.md Q-08, Q-09 — verified 2026-10-07 by probe against the worktree copy
- check-state --feature exits 1 only on INV-29 (standing worktree BUG-2037-readiness-contracts, main-session removal) — not feature-local — verified-at 50ab19ab

## Working set

- .harness/harness/features/FEAT-2037-product-document-guidance/STATE.md
- .harness/harness/features/FEAT-2037-product-document-guidance/feature.json
- .harness/harness/features/FEAT-2037-product-document-guidance/plan.yaml
- .harness/harness/features/FEAT-2037-product-document-guidance/BRIEF.md

## Done when

Scope: validate-c1-validator dispatched over review_sha 17c3cd5b and its consolidated digest closed
Authority: brief-perspective:.harness/harness/features/FEAT-2037-product-document-guidance/BRIEF.md#reader
Authority: brief-perspective:.harness/harness/features/FEAT-2037-product-document-guidance/BRIEF.md#orchestrator
