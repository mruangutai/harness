# Handoff — BUG-1286-test-tree-enforcement, plan → build — written at a185a41c, seq-3

## Next

Return to the operator, not to signature. The cycle-6 panel FAILED at `severity_max: high` and a
high finding may be accepted by no agent — only the main session's `sign-approval --overrule`
records acceptance. The operator must rule on three things in one sitting: F-01
(PF-c145e8377fc22dff2d33f76386c8bc6a, high) — fix by normalizing case 11's literal prefix, or
overrule; F-02 (PF-b3b6afcdbfce07dcf98d1e0fb29865e3, med) — state the governing matcher semantics;
and what REQ-09's word "counts" denotes, which narrows a requirement and is scope. Only after that
does signature, and then build entry at plan.yaml T-01, become the next action.

## Trust

- The cycle-6 panel FAILED with one high, three med, two low and one info finding, all dispositions
  `open`, no risk accepted — notes/review-plan-panel-c6.md — verified-at a185a41c by reading
  plan.yaml `panel:` (cycle 6, `last_run: 2026-09-04-20-validator`, seven findings).
- Both readers reached F-01/F-02 independently from opposite ends and landed on one root cause: case
  11 reasons lexically and segment-wise, while `code_grade._is_test_path` (`code_grade.py:466-471`)
  is the only mechanical `unit.detect` consumer and matches full relative paths with `fnmatch` —
  notes/review-plan-panel-c6.md, notes/review-harness-code-reviewer-planpanel-c6.md — UNVERIFIED at
  this tier beyond the lead's own stated re-check of the consumer census; re-read `code_grade.py`
  before acting on it.
- GAP-1 from the cycle-5 goal-check is closed and measured closed: the `docs/**`-for-`tests/unit/**`
  substitution is now RED, the `**/*.spec.*` mutant is RED, today's four globs pass —
  notes/research-BUG-1286-test-tree-enforcement-detect-partition-c6.md — verified-at a185a41c.
- Everything else the panel probed held under independent re-measurement: the one-fence contract's
  identity across T-03/T-04/SC-12, SC-06's exact-equality assertion, the 85/9/0 census, the task DAG
  and the SC-to-AC traceability — notes/review-plan-panel-c6.md — verified-at a185a41c.
- plan.yaml loads, routes clean, all five tasks carry all eleven keys, `status: plan`,
  `approval.status: pending`, and `check-state.sh` reports one violation for this feature, the
  expected unsigned BRIEF — verified-at a185a41c by the orchestrator running both checkers itself.

## Dead ends

- Do not unify the three clauses' test-shape vocabularies — notes/review-harness-eng-lead-plan-c0.md
  "Two member findings rejected at this tier" — verified-at 1977ebd6.
- Do not add a `tracked_paths_fn` injection seam to `violations()` — same note, ALTITUDE Q3 —
  verified-at 1977ebd6.
- Do not edit `.harness/harness.json` — the residual is closed guard-side by D-01's two-group
  vocabulary — plan.yaml D-01 — verified-at a185a41c; AC-11 and SC-16 freeze it.
- Do not relocate, generalise or weaken FEAT-44's exception — plan.yaml D-05 — verified-at a185a41c:
  the operator ruled it stays exactly as written.
- Do not close F-01 by deleting or weakening case 11 — notes/review-plan-panel-c6.md F-07, the
  should-not-exist reader's explicit keep verdict on the runtime-derived assertion — verified-at
  a185a41c.

## Working set

- .harness/harness/features/BUG-1286-test-tree-enforcement/plan.yaml
- .harness/harness/features/BUG-1286-test-tree-enforcement/BRIEF.md
- .harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-plan-panel-c6.md
- .harness/harness/features/BUG-1286-test-tree-enforcement/notes/research-BUG-1286-test-tree-enforcement-goalcheck-plan-c5.md
- .claude/skills/harness/bin/code_grade.py

## Done when

Scope: Operator rulings on F-01, F-02 and REQ-09's matcher semantics, then signature
Authority: approval:.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/BRIEF.md#Approval
