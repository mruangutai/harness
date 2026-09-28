# FEAT-69 — build divergences (SC-02 ledger)

Source: the committed clean-pin execution in `notes/clean-pin-byte-receipts.generated.md` (implementation pin `db488aa7c78e392c788bd5839a43ebf4ba562ea1`, baseline `a726bad8f74d23e6c1f07409383bb88d1da8fbcf`). Normalisation: each measurement's absolute root → `<checkout>`, nothing else. Full-table scope per amendment 2: every feature except this feature's own record.

**Thirteen measurements; thirteen identical; no differences.** The ledger is empty.

## Superseded executions (recorded because they were measured)

Two earlier executions over the same pin and baseline measured the full table over every feature INCLUDING FEAT-69's own record and differed in lines the split does not produce:

- **D-02** (both earlier runs) — four `note INV-32: FEAT-69-long-file-check-state-package finding PF-… disposition resolved.` lines and **D-03** — one `note FEAT-69-long-file-check-state-package: run plan-product is referenced but its dir is absent (pruned, or never created).` line: the feature's own record exists only at the pin (INV-32 notes each resolved panel finding; `.gitignore:7` excludes `runs/**`, so INV-8 notes the recorded run's absent directory in any clean checkout). Validate c0 VAL-01 refused them under SC-02's operator-ruling clause; the operator ruled the measurement be fixed instead (amendment 2), which removes them from the measurement rather than excusing them.
- **D-01** (first run only) — a foreign worktree's `The tree is dirty: …` clause in an INV-29 line changed between that run's two executions, seventy seconds apart, as another session committed; identical in every later execution. Environment, not the split.
