# Handoff — BUG-1129-validate-handoff-sweep, build → validate — written at 8d2d793224fe980287c57b3a92487e6d66905147, seq-1

## Next

Validate over review_sha (pinned after this commit): one validate dispatch to harness-validator-lead (qa, code, security, ui, goalcheck); any fix is main-session-direct (DEC-174).

## Trust

- T-01 built direct by Main: `cmd_ship` refuses (exit 1, no SKIP) before its first write when notes/handoff-validate.md is absent and `handoff_policy.exempt_reason` grants no exemption; the predicate is check-state's INV-17 one, moved not changed — .claude/skills/harness/bin/gh-sync.py, handoff_policy.py, check-state.py — VERIFIED
- Fail-first: on origin/main the unvalidated feature ships, its milestone is PATCHed and the sweep removes its worktree — notes/receipt-main-session-T-01-fail-first.md — VERIFIED
- 5 ship cases + 3 sweep cases for BUG-1129; every ship/record/open/abandon/sweep/hooks-install fixture that models a validated feature now writes the note; both matrices green; code-grade 0 FAIL — tests/integration/ — VERIFIED

## Dead ends

- A directory-shaped fixture is not needed here; the refusal is exercised through the real verb.

## Working set

- .harness/harness/features/BUG-1129-validate-handoff-sweep/plan.yaml
- .harness/harness/features/BUG-1129-validate-handoff-sweep/feature.json
- .harness/harness/features/BUG-1129-validate-handoff-sweep/notes/receipt-main-session-T-01-fail-first.md

## Done when

Scope: validate segment
Authority: brief-perspective:.harness/harness/features/BUG-1129-validate-handoff-sweep/BRIEF.md#operator
Authority: brief-sc:SC-01
Authority: brief-sc:SC-02
Authority: brief-sc:SC-03
Authority: brief-sc:SC-04
