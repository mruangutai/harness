# Handoff — BUG-151-check-domain-fail-aggregation, validate → ship — written at 9b7b27d0, seq-1

## Next

Ship BUG-151 via `gh-sync.py ship .harness/harness/features/BUG-151-check-domain-fail-aggregation`
(already executed by the main session; this note documents the validate → ship seam that
could not get a normal handoff note when it was crossed, per the known worktree handoff
defect corroborated across all five parallel BUG flows this session).

## Trust

- The cycle-1 panel over the fix returned PASS, must_fix empty — verified-at 9b7b27d0
  (runs/2026-09-07-3-validator/digest.md).

## Dead ends

- Do not expand scope to the two sibling suites with the identical un-safeguarded shape —
  out of scope by an approved BRIEF constraint — source: STATE.md, verified-at 9b7b27d0.

## Working set

- .harness/harness/features/BUG-151-check-domain-fail-aggregation/STATE.md
- .harness/harness/features/BUG-151-check-domain-fail-aggregation/plan.yaml
- tests/integration/test-check-domain.py

## Done when

Scope: ship BUG-151
Authority: approval:.harness/harness/features/BUG-151-check-domain-fail-aggregation/plan.yaml#approval
