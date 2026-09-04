# Handoff — BUG-1286-test-tree-enforcement, plan → build — written at c040c319, seq-2

## Next

Present BRIEF.md and plan.yaml to the operator for signature (main session only: `plan-merge.py
sign-approval` for the plan, the BRIEF's `## Approval` section for the brief). Two cycle-4 panel
findings carry `remedy_window: closes at signature` and must be ruled on in the same sitting —
PF-8de8d64458a4a30d8c7ba0b111546ccd (med) and PF-8da87ee5041dd05ed45864fd98318883 (low). On
signature, enter build: plan.yaml T-01 is the eng segment's first task, the only one with an empty
`depends_on`; T-02 and T-03 unblock behind it, T-04 behind T-03, T-05 behind T-01 and T-02.

## Trust

- The cycle-4 panel PASSED at severity_max med with nothing high, critical or unrated, so no finding
  needs operator risk-acceptance — notes/review-plan-panel-c4.md — verified-at c040c319 by reading
  plan.yaml `panel:` directly (cycle 4, 6 findings, 1 med / 1 low / 3 info / 1 none, all `open`).
- The cycle-4 goal-check found no surviving gap and all eleven acceptance criteria delivered —
  notes/research-BUG-1286-test-tree-enforcement-goalcheck-plan-c4.md — verified-at c040c319 by
  reading BRIEF.md's 18 SC and its AC table.
- Widening `*_test.*` and `*.test.*` to any extension is inert on the present tree: zero tracked
  matches outside `tests/**`, one inside (`tests/unit/omp-hooks.test.ts`) —
  notes/research-BUG-1286-vocabulary-split.md, corroborated by three independent enumerations in the
  panel — verified-at c040c319.
- plan.yaml loads, routes clean (`check-plan-routes.py`, 0 violations), all five tasks carry all
  eleven keys, `status: plan`, `approval.status: pending`; `check-state.sh` reports one violation
  for this feature, the expected unsigned BRIEF — verified-at c040c319 by the orchestrator running
  both checkers itself.
- T-01's premises hold at HEAD: `run-unit-tests.sh --check-layout` exists (line 20), the runner's
  sole `violations()` caller is line 33, the mutation snapshot's scope is line 47's
  `--mutation-check "$BIN_DIR"` — verified-at 1977ebd6 by direct read.

## Dead ends

- Do not unify the three clauses' test-shape vocabularies — notes/review-harness-eng-lead-plan-c0.md
  "Two member findings rejected at this tier" — verified-at 1977ebd6: feeding `probe-*` into the
  under-`tests/` clause makes `violations()` report tests/manual/probe-omp-session-accessor.py and
  contradicts DEC-213.
- Do not add a `tracked_paths_fn` injection seam to `violations()` — same note, ALTITUDE Q3 —
  verified-at 1977ebd6: a test handed a path list proves nothing about `git ls-files`.
- Do not edit `.harness/harness.json` — the `unit.detect` residual is closed from the guard's side by
  D-01's two-group vocabulary — plan.yaml D-01 — verified-at c040c319; AC-11 and SC-16 freeze it.
- Do not relocate, generalise or weaken FEAT-44's `evidence/probe-session-accessors.ts` exception —
  plan.yaml D-05 — verified-at c040c319: the operator ruled it stays exactly as written.

## Working set

- .harness/harness/features/BUG-1286-test-tree-enforcement/plan.yaml
- .harness/harness/features/BUG-1286-test-tree-enforcement/BRIEF.md
- .harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-plan-panel-c4.md
- .harness/harness/features/BUG-1286-test-tree-enforcement/notes/research-BUG-1286-test-tree-enforcement-goalcheck-plan-c4.md
- .claude/skills/harness/bin/suite_layout.py

## Done when

Scope: Operator signature on the approval artifacts, then build entry at T-01
Authority: approval:.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/BRIEF.md#Approval
