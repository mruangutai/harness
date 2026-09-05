# Handoff — BUG-1286-test-tree-enforcement, plan → build — written at a8532ce3, seq-5

## Next

Present BRIEF.md and plan.yaml to the operator for signature. The cycle-10 panel PASSED at
`severity_max: med` with `must_fix` empty and nothing high, critical or unrated, so no `--overrule`
ruling is required; five findings ride into the batched signature review and the panel's own
recommendation is to carry them. On signature, enter build: plan.yaml T-01 is the eng segment's
first task, the only one with an empty `depends_on`; T-02 and T-03 unblock behind it, T-04 behind
T-03, T-05 behind T-01 and T-02.

## Trust

- The cycle-10 panel PASSED, `severity_max: med`, five findings `open`, the four cycle-8 findings
  carried forward `resolved_by: T-01` — notes/research-BUG-1286-test-tree-enforcement-panel-c10.md —
  verified-at a8532ce3 by reading plan.yaml `panel:` (cycle 10, `last_run: 2026-09-04-30-validator`,
  1 med / 2 low / 2 info, all `open`).
- The contract's ground truth: `code_grade.py:458-473`, `_is_test_path` unions every kind whose
  status is `active` or `locally_run` and matches `fnmatch` over the FULL relative path minus that
  kind's `exclude`; `fnmatch` has no `**` and a bare `*` crosses `/` — verified-at a8532ce3 by the
  orchestrator reading the function itself.
- STEP 0, measured independently twice: tracked 2706, counted-outside-`tests/` 0, so REQ-09 holds
  today at full breadth — notes/research-amend-c6-closure.md and the c7 goal-check — verified-at
  cab6adb2.
- plan.yaml loads, routes clean, five tasks with all eleven keys, `status: plan`,
  `approval.status: pending`; `check-state.sh` reports one violation for this feature, the expected
  unsigned BRIEF — verified-at a8532ce3 by the orchestrator running both checkers itself.
- **Every "case 11 is green/red under X" result on record is a hand-simulation of a SPECIFICATION**,
  including all six prototype results and both panels' sweeps — notes/research-BUG-1286-test-tree-enforcement-panel-c10.md
  adequacy notes — UNVERIFIED as behaviour. Three independent reimplementations agree and none is
  the artifact that ships. T-01's own mandate to re-prove the four red cases against the BUILT
  artifact is what closes this, and it is the first thing build must not skip.

## Dead ends

- Do not delete or weaken T-01 case 11 — KEEP verdict at cycles 6, 8 and 10 — verified-at a8532ce3.
- Do not reintroduce any cardinality, occupancy or corpus-membership assertion over the certified
  buckets — three cycles flagged one and all three are now gone — plan.yaml T-01 — verified-at
  a8532ce3.
- Do not narrow REQ-09, do not overrule F-01, do not edit `.harness/harness.json` or activate a test
  kind, and do not relocate or weaken FEAT-44's exception — the operator's four rulings —
  verified-at a8532ce3.
- Do not unify the three clauses' vocabularies, and do not add a `tracked_paths_fn` seam —
  notes/review-harness-eng-lead-plan-c0.md — verified-at 1977ebd6.

## Working set

- .harness/harness/features/BUG-1286-test-tree-enforcement/plan.yaml
- .harness/harness/features/BUG-1286-test-tree-enforcement/BRIEF.md
- .harness/harness/features/BUG-1286-test-tree-enforcement/notes/research-BUG-1286-test-tree-enforcement-panel-c10.md
- .harness/harness/features/BUG-1286-test-tree-enforcement/notes/research-BUG-1286-test-tree-enforcement-goalcheck-plan-c9.md
- .claude/skills/harness/bin/code_grade.py

## Done when

Scope: Operator signature on the approval artifacts, then build entry at T-01
Authority: approval:.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/BRIEF.md#Approval
