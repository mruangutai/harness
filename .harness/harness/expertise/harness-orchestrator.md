# Expertise — harness-orchestrator

## Patterns (max 15)

## Gotchas (max 15)

## Outcomes (max 10)

## Open (max 5)
- O-01: Shared `.harness/expertise/` has no lineage protection. Nothing reconciles a landed diff
  against the plan's declared files, so an undeclared edit to a per-spawn-injected file rides any
  cluster commit and only a human notices. Whether the fix is diff-vs-plan reconciliation, write-guard
  scoping, or keeping Expertise off feature branches is undecided.
