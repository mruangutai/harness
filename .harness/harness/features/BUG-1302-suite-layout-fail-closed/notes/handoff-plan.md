# Handoff — BUG-1302-suite-layout-fail-closed, plan → build — written at 36311d67, seq-1

## Next

Return to the main session for signature. BRIEF `## Approval` and plan `approval.status` both
read `pending` and only the main session signs, via `plan-merge.py sign-approval`. Nothing else
proceeds first: every task T-01..T-05 is `execution_mode: main-session-direct` under DEC-174, so
there is no lead to dispatch — the build phase is the operator's own hands, not an eng-lead run.
Carry the three signature-review items up with the plan: PF-1ada4741 (the AST-pin red is
main-session-only to clear), the DEC-174 enumeration question, and the Advisor's B-6 remedy being
a labelled recommendation rather than a ruling.

## Trust

- All five B-row premises hold at source — `_literal_key_present`, `_is_inside_tests`, case 11
  else-branch and `_violations_callers` in tests/unit/test-suite-layout.py, plus case 2 in
  tests/integration/test-run-unit-tests-layout.py — verified-at c369fb1
- DEC-174 binds both test files, so main-session-direct is correct — Advisor RULING in
  runs/2026-09-05-2-validator/digest.md — verified-at c369fb1
- check-plan-routes.py exits 0 with 5 DEVIATION and 0 VIOLATION, so SC-10 is green at plan time —
  run at the orchestrator tier over plan.yaml — verified-at 36311d67
- T-05's red demonstration is executable: tree() copies run-unit-tests.sh into the temp tree and
  run() executes that copy, and the `layout_out=` anchor exists —
  tests/integration/test-run-unit-tests-layout.py:16-23,48 and run-unit-tests.sh:33 — verified-at c369fb1
- SC-02/SC-04 AST counts (any()=2, "*?["=2, ".."=2 pre-fix; 1 each post-fix) — four independent
  agreeing derivations — notes/review-harness-code-reviewer-planpanel-c1.md — verified-at c369fb1
- SC-09's named-check list is COMPLETE — every anchor it names exists, but whether it OMITS a
  pre-existing check worth protecting was assessed by nobody — UNVERIFIED

## Dead ends

- Merging T-02 into T-01 — plan-merge.py has no delete route, so a merge strands an abandoned task
  in a signed plan — runs/2026-09-05-2-eng/digest.md AL-01 — verified-at c369fb1
- Widening scope to `sole_implementations`'s silent skip — a real fail-open of B-6's own class in
  the same file, ruled out of scope and carried as backlog row B-1 —
  runs/2026-09-05-2-eng/digest.md AR-08 — verified-at c369fb1
- Re-deriving the SC-02/SC-04 AST counts a fifth time — four agreeing derivations already exist —
  runs/2026-09-05-4-validator/digest.md assessed_and_dismissed — verified-at c369fb1
- Untracking the fixture rogue as T-05's red demonstration — it falsifies all three of case 2's
  clauses at once, so the FAIL cannot discriminate the fix — plan.yaml T-05 intent — verified-at 36311d67

## Working set

- .harness/harness/features/BUG-1302-suite-layout-fail-closed/BRIEF.md
- .harness/harness/features/BUG-1302-suite-layout-fail-closed/plan.yaml
- .harness/harness/features/BUG-1302-suite-layout-fail-closed/feature.json
- .harness/harness/features/BUG-1302-suite-layout-fail-closed/runs/2026-09-05-4-validator/digest.md
- .harness/harness/features/BUG-1302-suite-layout-fail-closed/notes/research-BUG-1302-goalcheck-plan-c1.md

## Done when

Scope: the main session signs the BRIEF and the plan
Authority: approval:.claude/worktrees/harness/BUG-1302-suite-layout-fail-closed/.harness/harness/features/BUG-1302-suite-layout-fail-closed/BRIEF.md#Approval
