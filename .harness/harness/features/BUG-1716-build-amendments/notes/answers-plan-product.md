# Operator answers — plan-product

## Q1 — targeted PM correction

Authorized. One pm dispatch, bounded to:

1. Place T-09 after T-07 and T-08 in `tasks:` file order (its `depends_on` is correct; the order is what INV/sign refuses). No other reordering.
2. Apply the three open `proportionality` findings, all `scope: task` (DEC-228: trimmed at apply, never a downgrade):
   - PF-ac6288f9c: T-01 does not embed the BUG-285 T-03 specimens in the eng-lead role file; they live in the T-02/T-04 fixtures only.
   - PF-15492c981: drop T-04's idempotent-replay success mode; a replay is a refusal like any other CAS miss.
   - PF-001fc3bd0: drop T-03's overrule-rate unit test; the ledger alone is the evidence.
   Mark each `resolved` with the resolving task.
3. Re-run `plan-merge.py check`. Touch nothing else.

Approved by: mruangutai (blanket session authorization 2026-09-15)
Date: 2026-09-15
