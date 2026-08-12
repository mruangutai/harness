# STATE

## Current

- feature: FEAT-17-guard-boundaries
- branch: feat/FEAT-17-guard-boundaries
- status: Building
- head: 0d9ba16

BUILD IN PROGRESS, six of seven tasks landed. plan.yaml is signed (approval.status approved,
operator, 2026-08-11) and carries ruling R-01 dated 2026-08-12 re-scoping T-06 to a receipt.

Committed on the feature branch, all six main-session-direct under the DEC-174 carve-out and
executed directly by the main session — none is to be re-run or re-dispatched:
T-01 5854d12 (harness_boundary.py extracted, check-domain.sh rewired), T-02 f869cd3 (Write route
refuses an out-of-place worktree, target-side and root-side), T-03 3d327dd (Bash route decides from
the shared module, closing #261), T-04 a665465 (worktree creation outside .claude/worktrees refused),
T-05 0d9ba16 (INV-25 at session entry), T-06 232fe06 (re-scoped to a truthful receipt under R-01).

REMAINING: T-07 only — record the boundary rule in docs/harness/DECISIONS.md and regenerate
DECISIONS-INDEX.md with gen-decisions-index.py. It is execution_mode team, execution_agent
harness-documentor, routed through harness-product-lead. Next free decision number is DEC-193,
measured at 0d9ba16: DECISIONS.md holds 190 entries, highest DEC-192.

Three constraints carried into the T-07 dispatch: the index is GENERATED and never hand-edited, and
the regeneration must be committed or T-07's own verify fails its clean-diff assertion; the three
surviving divergences between the two write routes must land as written, not tidied into a parity
claim; and the one-implementation claim is scoped no wider than the evidence — the mutation proof is
direct evidence for the ROOT-SIDE check on both routes, while the TARGET-SIDE branch is covered by
behavioural cases only and is NOT mutation-proved.

Cycles 6 of 10, all spent in the plan phase. No build cycle has been consumed: the six task commits
were direct, and T-07 has not yet run. Feature is NOT to be moved to Review — the operator decides
that after the gates report.

## Open Questions

- Q3 Backlog, not planned here: both guard suites sit in run-unit-tests.sh INTEGRATION_SCRIPTS
  despite matching the unit glob, so --kind unit never runs them.
- Q4 Backlog, not planned here: bash-write-guard.sh resolves RELATIVE operands against the harness
  root rather than the agent cwd. Untriaged — defect or intended conservatism.

ANSWERED and struck: INV-25 severity — it remains a FAILURE, not a warning (operator, 2026-08-11).
MOOTED by the 2026-08-11 re-scope: Q1 (SC-03's no-PyYAML half) and Q2 (whether SC-03 survives — it
does, narrowed).
