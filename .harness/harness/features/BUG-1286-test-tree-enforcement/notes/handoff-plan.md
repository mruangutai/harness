# Handoff — BUG-1286-test-tree-enforcement, plan → build — written at cab6adb2, seq-4

## Next

Present BRIEF.md and plan.yaml to the operator for signature. The cycle-8 panel PASSED at
`severity_max: med` with nothing high, critical or unrated, so no `--overrule` ruling is required;
four findings ride into the batched signature review, and the panel's own assessment is that all
four close in ONE edit to T-01 case 11 plus SC-19. On signature, enter build: plan.yaml T-01 is the
eng segment's first task, the only one with an empty `depends_on`; T-02 and T-03 unblock behind it,
T-04 behind T-03, T-05 behind T-01 and T-02.

## Trust

- The cycle-8 panel PASSED, `severity_max: med`, four findings all `disposition: open`, no risk
  accepted — notes/review-plan-panel-c8.md — verified-at cab6adb2 by reading plan.yaml `panel:`
  (cycle 8, `last_run: 2026-09-04-25-validator`, 2 med / 2 low).
- The Advisor consultation the operator directed is answered and readable in plan.yaml's
  `panel.advisor_consultation` — notes/review-plan-panel-c8.md — verified-at cab6adb2.
- The contract's ground truth: `code_grade.py:458-473`, `_is_test_path` unions every kind whose
  status is `active` or `locally_run` and matches `fnmatch` over the FULL relative path minus that
  kind's `exclude`; `fnmatch` has no `**` and a bare `*` crosses `/` — verified-at cab6adb2 by the
  orchestrator reading the function itself.
- STEP 0, measured twice independently: tracked 2706, counted-outside-`tests/` 0 at cab6adb2, so
  REQ-09 holds today at full breadth — notes/research-amend-c6-closure.md and
  notes/research-BUG-1286-test-tree-enforcement-goalcheck-plan-c7.md — verified-at cab6adb2.
- plan.yaml loads, routes clean, five tasks with all eleven keys, `status: plan`,
  `approval.status: pending`; `check-state.sh` reports one violation for this feature, the expected
  unsigned BRIEF — verified-at cab6adb2 by the orchestrator running both checkers itself.
- Every "case 11 is green/red under X" result on record is a hand-simulation of a SPECIFICATION, not
  an execution: no code exists yet — notes/review-plan-panel-c8.md adequacy notes — UNVERIFIED as
  behaviour and only verifiable once T-01 lands.

## Dead ends

- Do not delete or weaken T-01 case 11 — notes/review-plan-panel-c6.md F-07, an explicit KEEP
  verdict, reaffirmed at cycle 8 — verified-at cab6adb2.
- Do not narrow REQ-09 to basename-only discovery, and do not overrule F-01 — the operator's third
  ruling — verified-at cab6adb2 against plan.yaml REQ-09 and case 11's normalization clause.
- Do not edit `.harness/harness.json` or activate a test kind — the three-kind blast radius is
  DISCLOSED, not fixed — BRIEF.md `## Verification gaps` — verified-at cab6adb2.
- Do not relocate, generalise or weaken FEAT-44's exception — plan.yaml D-05 — verified-at cab6adb2.
- Do not unify the three clauses' vocabularies, and do not add a `tracked_paths_fn` seam —
  notes/review-harness-eng-lead-plan-c0.md — verified-at 1977ebd6.

## Working set

- .harness/harness/features/BUG-1286-test-tree-enforcement/plan.yaml
- .harness/harness/features/BUG-1286-test-tree-enforcement/BRIEF.md
- .harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-plan-panel-c8.md
- .harness/harness/features/BUG-1286-test-tree-enforcement/notes/research-BUG-1286-test-tree-enforcement-goalcheck-plan-c7.md
- .claude/skills/harness/bin/code_grade.py

## Done when

Scope: Operator signature on the approval artifacts, then build entry at T-01
Authority: approval:.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/BRIEF.md#Approval
