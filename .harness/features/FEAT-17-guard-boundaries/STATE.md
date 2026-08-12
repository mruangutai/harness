# STATE

## Current

- feature: FEAT-17-guard-boundaries
- branch: feat/FEAT-17-guard-boundaries
- status: Building
- run: .harness/features/FEAT-17-guard-boundaries/runs/2026-08-12-07-t07-product/digest.md

ALL SEVEN TASKS HAVE LANDED. The build phase is complete and the feature is with the operator.

T-01 5854d12, T-02 f869cd3, T-03 3d327dd, T-04 a665465, T-05 0d9ba16, T-06 232fe06 — all six
main-session-direct under the DEC-174 carve-out, executed directly by the main session, not to be
re-run or re-dispatched. T-07 01d8f60 — the only team task, routed through harness-product-lead to
harness-documentor, landing DEC-193 at DECISIONS.md:5687 with the index row's ruling hand-written.

Four gates run at HEAD and all green: T-07's own verify exit 0, re-run on the committed tree with a
byte-identical regeneration; check-state.sh exit 0; check-plan-routes.py exit 0, 0 violations across
8 plans, with T-07 reading OK granted to harness-documentor; run-unit-tests.sh exit 0, 152 scripts
PASS and 0 FAIL, with test-check-domain.py, test-bash-write-guard.py, test-check-state.py and
test-gen-decisions-index.py all confirmed among them.

DEC-193 was checked against its three non-negotiables by reading the entry, not the digest: the
three deliberate divergences plus the --resolve note are all present and no parity claim was
introduced, and the one-implementation claim is scoped in both directions — mutation proof is direct
evidence for the ROOT-SIDE check on both routes, the TARGET-SIDE branch is behavioural-only and
explicitly NOT mutation-proved.

NOT DONE, and deliberately reserved to the operator: the SC goal-check has not been run, and the
feature has NOT been marked complete or moved to Review. The dispatch reserved that decision.

Cycles 6 of 10, unchanged — all six were spent in the plan phase and the T-07 run was a clean first
pass with zero send-backs. Runs 7 of 20. Seam note: notes/handoff-build.md.

## Open Questions

- Q1 plan.yaml's T-07 intent cites check-domain.sh line 676 for the domain_check gate. VERIFIED
  ROTTEN at HEAD: line 534 is `if _run_domain and not _no_parser:` and line 676 is blank. The shipped
  DEC-193 is unaffected — it quotes the condition, not the integer. plan.yaml is pm's to correct.
  Non-blocking.
- Q3 Backlog, not planned here: both guard suites sit in run-unit-tests.sh INTEGRATION_SCRIPTS
  despite matching the unit glob, so --kind unit never runs them.
- Q4 Backlog, not planned here: bash-write-guard.sh resolves RELATIVE operands against the harness
  root rather than the agent cwd. Untriaged — defect or intended conservatism.

ANSWERED and struck: INV-25 severity — it remains a FAILURE, not a warning (operator, 2026-08-11).
MOOTED by the 2026-08-11 re-scope: the two plan-phase questions on SC-03's no-PyYAML half.
