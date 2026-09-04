# Handoff — BUG-1286-test-tree-enforcement, plan → build — written at 1977ebd6, seq-1

## Next

Present BRIEF.md and plan.yaml to the operator for signature (main session only, via
`plan-merge.py sign-approval` for the plan and the BRIEF's `## Approval` section). Decide at the
same sitting whether to accept panel finding PF-b1381e1d1016bfebf6d3364eddb5ef59 as-is or spend one
pm edit on T-03's `--against` output contract first. On signature, enter build: the eng segment is
plan.yaml T-01, which has no `depends_on` and is the only startable task; T-02 and T-03 unblock
behind it, T-04 behind T-03, T-05 behind T-01 and T-02.

## Trust

- The panel PASSED with severity_max med and nothing high/critical/unrated, so no finding needs
  operator risk-acceptance — notes/review-plan-panel-c3.md — verified-at 1977ebd6 by reading
  plan.yaml `panel:` directly (9 findings, 1 med / 3 low / 5 info, every disposition `open`).
- All eleven issue #1286 acceptance criteria map to a falsifiable SC with a valid verify method —
  notes/research-BUG-1286-test-tree-enforcement-goalcheck-plan-c2.md plus its closing append —
  verified-at 1977ebd6 by reading BRIEF.md's SC list and AC table.
- plan.yaml loads, routes clean (`check-plan-routes.py`, 0 violations), all five tasks carry all
  eleven keys, `status: plan`, `approval.status: pending` — verified-at 1977ebd6 by the orchestrator
  running both checkers itself.
- T-01's premises hold at HEAD: `run-unit-tests.sh --check-layout` exists (line 20), the runner's
  sole `violations()` caller is line 33, the mutation snapshot's scope is line 47's
  `--mutation-check "$BIN_DIR"` — verified-at 1977ebd6 by direct read.
- `plan-merge.py apply` is ADD-ONLY and exits 7 on a differing value; changing an existing field
  uses `amend` — notes/research-BUG-1286-plan-review-application-c1.md — verified-at 1977ebd6 by pm
  at plan-merge.py:729-743.

## Dead ends

- Do not unify the three clauses' test-shape vocabularies — notes/review-harness-eng-lead-plan-c0.md
  "Two member findings rejected at this tier" — verified-at 1977ebd6: feeding `probe-*` into the
  under-`tests/` clause makes `violations()` report tests/manual/probe-omp-session-accessor.py and
  contradicts DEC-213.
- Do not add a `tracked_paths_fn` injection seam to `violations()` — same note, ALTITUDE Q3 —
  verified-at 1977ebd6: a test handed a path list proves nothing about `git ls-files`, which is the
  distinction issue #1286 demands be proved.
- Do not edit `.harness/harness.json` `unit.detect` to close the extension-agnostic residual — it is
  disclosed in BRIEF.md `## Verification gaps` and frozen by SC-14 — verified-at 1977ebd6; the panel
  recommends a follow-up ticket, not an in-scope fix.
- Do not relocate FEAT-44's `evidence/probe-session-accessors.ts` — plan.yaml D-05 — verified-at
  1977ebd6: it is the registry's single live entry by design.

## Working set

- .harness/harness/features/BUG-1286-test-tree-enforcement/plan.yaml
- .harness/harness/features/BUG-1286-test-tree-enforcement/BRIEF.md
- .harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-plan-panel-c3.md
- .harness/harness/features/BUG-1286-test-tree-enforcement/notes/research-BUG-1286-test-tree-enforcement-goalcheck-plan-c2.md
- .claude/skills/harness/bin/suite_layout.py

## Done when

Scope: Operator signature on the approval artifacts, then build entry at T-01
Authority: approval:.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/BRIEF.md#Approval
