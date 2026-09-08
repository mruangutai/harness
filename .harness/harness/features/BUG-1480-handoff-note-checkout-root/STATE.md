# STATE

## Current

- feature: BUG-1480-handoff-note-checkout-root
- run: none
- squad: none
- status: in-flight

Plan phase opened 2026-09-07 from `origin/main` (`6d969ed3`), standalone per the operator's
binding decision: this prerequisite ships on its own PR, is not cherry-picked into BUG-201, and
does not wait on the BUG-1290 reconciliation.

The defect is filed as issue #1480 and measured at `check-domain.sh:1141-1149` / `:1746-1748`:
`_norm` takes the checkout-relative path from `harness_boundary.checkout_relative` and discards
the checkout root `_ck[0]`, so `handoff_done_when.problems` is handed a worktree-relative path
together with the MAIN checkout root and looks for the feature directory where it does not exist.

## Open Questions

- none
