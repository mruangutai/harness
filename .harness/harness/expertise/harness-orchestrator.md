# Expertise — harness-orchestrator

## Patterns (max 15)
- P-01: WHEN reading `run-unit-tests.sh` output DO count `^FAIL ` lines and capture the runner's exit
  status in a variable — its final line is the last script's own `N/N checks passed`, so a tail read
  reports a red suite as green, and a piped `$?` returns the pipe's last command.

## Gotchas (max 15)
- G-01: WHEN running `check-state.sh` DO treat it as expensive — INV-26 reads every board card at
  roughly 500 GraphQL points per invocation, against a 5,000-point budget. Run it at entry and before
  a commit, not as a progress poll.
- G-02: WHEN invoking `validate-digest.py` DO pass the PERSONA first and the path second. Path-only
  prints `BLOCKED (contract violation) — unknown persona '<the path>'`, which reads exactly like a
  malformed digest and will make you reject a valid one.
- G-03: WHEN a distillation returns ops for an agent you think holds no write path DO check the
  grant first — all three reviewers hold `Write` and both Expertise tiers, so ops go back to the
  owner via its lead; the orchestrator can write no Expertise file but its own.

## Outcomes (max 10)

## Open (max 5)
- O-01: Shared `.harness/expertise/` has no lineage protection. Nothing reconciles a landed diff
  against the plan's declared files, so an undeclared edit to a per-spawn-injected file rides any
  cluster commit and only a human notices. Whether the fix is diff-vs-plan reconciliation, write-guard
  scoping, or keeping Expertise off feature branches is undecided.
