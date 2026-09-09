# Handoff — BUG-276-expertise-merge-duplicate-id, build → validate — written at a641a5b8, seq-1

## Next

Ship BUG-276 once its PR merges: `gh-sync.py ship
.harness/harness/features/BUG-276-expertise-merge-duplicate-id`. Validate is already
complete (cycle-1 panel PASS, must_fix empty) — this note documents the build seam that
could not get a normal handoff note when it was crossed (worktree handoff defect, STATE.md
Open Questions Q8).

## Trust

- T-01 and T-02 landed and the blocking qa gate passed with a strong mutation-testing proof
  (all six new checks reddened when the guard was disabled on a disposable worktree) —
  verified-at 8d0aabeb.
- SIMPLIFY ran empty (four readers, zero applies) — verified-at 8d0aabeb.
- The validate panel's one gating blocker (a new test function graded 1 against the
  test-code bar of 3) was fixed and re-measured directly by the orchestrator: grade 1 to
  grade 5 — verified-at a641a5b8.
- The narrow cycle-1 re-panel over the fix returned PASS, must_fix empty — verified-at
  a641a5b8 (runs/2026-09-07-04-validator/digest.md).

## Dead ends

- Do not reopen `case_u23`'s grade-2 finding — the panel already disposed of it correctly
  with a recorded reason; it is not part of the same blocker — source: STATE.md, verified-at
  a641a5b8.

## Working set

- .harness/harness/features/BUG-276-expertise-merge-duplicate-id/STATE.md
- .harness/harness/features/BUG-276-expertise-merge-duplicate-id/plan.yaml
- .claude/skills/harness/bin/expertise-merge.py
- tests/integration/test-expertise-merge.py

## Done when

Scope: ship BUG-276 once its PR merges
Authority: approval:.harness/harness/features/BUG-276-expertise-merge-duplicate-id/plan.yaml#approval
