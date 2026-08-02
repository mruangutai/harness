# Expertise — harness-eng-lead

## Patterns (max 15)
- P-01: WHEN a member reports a receipt in prose instead of the observed value DO send it back
  for the verbatim output and the invocation form — a lead-tier send-back costs one member
  spawn; the same gap found later by the review panel costs a feature cycle.
- P-02: WHEN dispatching a task that inverts or retires an existing assertion DO put the
  adjacent labels, docstrings and usage strings explicitly in scope — prose asserting the
  superseded contract is the same defect class, and a stale test label propagates upward as
  though it were a measurement.
- P-03: WHEN a task's verify list is greps plus a test suite DO ask which changed module the
  suite actually executes — a module the runner never imports is left unproven by a green gate,
  not proven by it.

## Gotchas (max 15)
- G-01: `.claude/skills/harness/bin/**` sits in both backend-dev's and dev-ops's domain in
  team-config.yaml, so the domain hook cannot keep their writes disjoint there — serialize any
  two tasks touching one file under it and attribute each write.

## Outcomes (max 10)

## Open (max 5)
