# Handoff — BUG-2399-run-records-staged-at-ship, build → validate — written at 9db1ba98, seq-1

## Next

Dispatch ONE `validate` team to `harness-validator-lead` over `review_sha`
9db1ba98209df49017e73fae13da56f3e240086c (base 9eb07b4f3cd235c234a10edddbfe5542c1e85fba) with
inputs `feat` = BUG-2399-run-records-staged-at-ship and the pinned sha; readers grade T-01
(SC-01, SC-02 automated: unit; SC-03 inspection). Any `must_fix` returns to the main session:
T-01 is `execution_mode: main-session-direct`, so no dev inside the validator lead's run owns it.

## Trust

- T-01 built main-session-direct at 54265700; simplify pass empty at 700cc4e2 — `git -C <worktree> log --oneline 9eb07b4f..9db1ba98` — verified-at 9db1ba98
- T-01 `verify:` exits 0; run-unit-tests rc 0 for unit and integration; code-grade --base 9eb07b4f 18 PASS — main session's dispatch text to this orchestrator — UNVERIFIED
- Red-first evidence (9 assertion failures against the 9eb07b4f pruner, 36/36 green) — notes/red-first-T-01.md — UNVERIFIED
- Approval signed: BRIEF `## Approval` approved and plan.yaml `approval.status: approved`; rework 1 round / 45 min — notes/answers-2026-11-23-signoff.md, feature.json `rework` — verified-at 9db1ba98
- Judgements the main session recorded for validate (no force-add text existed in harness-ship.md; failed `git add` exits 1 not 2; unsafe run ids never staged; only top-level ui/ excluded; missing = absent on disk) — main session's dispatch text — UNVERIFIED

## Dead ends

- No build/SIMPLIFY engineering-lead run exists or is owed: every task is main-session-direct — check-state INV-17 note at the 9db1ba98 seam — verified-at 9db1ba98
- The harness-ship.md "remove manual force-add" clause of SC-03 has no removal diff to show: the main session reports no such text existed at base — main session's dispatch text — UNVERIFIED

## Working set

- .harness/harness/features/BUG-2399-run-records-staged-at-ship/BRIEF.md
- .harness/harness/features/BUG-2399-run-records-staged-at-ship/plan.yaml
- .harness/harness/features/BUG-2399-run-records-staged-at-ship/notes/red-first-T-01.md
- .harness/harness/features/BUG-2399-run-records-staged-at-ship/notes/simplify-pass.md
- .harness/harness/features/BUG-2399-run-records-staged-at-ship/feature.json

## Done when

Scope: validate run dispatched over 9db1ba98 and closed with its lead digest
Authority: brief-perspective:.harness/harness/features/BUG-2399-run-records-staged-at-ship/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-2399-run-records-staged-at-ship/BRIEF.md#code maintainer
