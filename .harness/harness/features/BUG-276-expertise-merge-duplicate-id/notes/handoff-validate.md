# Handoff — BUG-276-expertise-merge-duplicate-id, validate → ship — written at a641a5b8, seq-1

## Next

Ship BUG-276 via `gh-sync.py ship .harness/harness/features/BUG-276-expertise-merge-duplicate-id`
(already executed by the main session; this note documents the validate → ship seam that
could not get a normal handoff note when it was crossed, per the known worktree handoff
defect recorded in STATE.md Open Questions Q8).

## Trust

- The narrow cycle-1 re-panel over the fix returned PASS, must_fix empty — verified-at
  a641a5b8 (runs/2026-09-07-04-validator/digest.md).
- qa's blocking gate proved the new checks with a live mutation test on a disposable
  worktree — verified-at 8d0aabeb.

## Dead ends

- Do not reopen `case_u23`'s grade-2 finding — already disposed of with a recorded reason
  — source: STATE.md, verified-at a641a5b8.

## Working set

- .harness/harness/features/BUG-276-expertise-merge-duplicate-id/STATE.md
- .harness/harness/features/BUG-276-expertise-merge-duplicate-id/plan.yaml
- .claude/skills/harness/bin/expertise-merge.py

## Done when

Scope: ship BUG-276
Authority: approval:.harness/harness/features/BUG-276-expertise-merge-duplicate-id/plan.yaml#approval
