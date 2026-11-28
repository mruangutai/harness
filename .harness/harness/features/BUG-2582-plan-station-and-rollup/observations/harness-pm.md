# Observations — harness-pm — BUG-2582-plan-station-and-rollup

- 2026-11-27: Plan panel findings[].reader is not a stable key: the corpus holds code-reviewer, harness-code-reviewer and should-not-exist for the same slots (BUG-2565, BUG-2566), so any tie from a member entry to its findings must canonicalize and fail closed on no-match or multi-match.
- 2026-11-27: A writer-side fix that turns one record type into another must reproduce the creation path's seeded fields (approval pending, drafted_at); dropping only the illegal key leaves a record INV-3 misreads and the DEC-254 era check exempts.
- 2026-11-27: A reader premise that a gate refuses some record held only for a hand-written shape: the prescribed writer route (plan-merge apply) seeds approval pending on creation, stub included, so the guard already admitted it. Running the real guard fixture on both shapes (1s) replaced a planned guard change with a witness task.
- 2026-11-27: plan-merge set-lanes, set-key and set-panel accept --value-file /dev/stdin, so no value file outside pm's write grant is needed; the new apply prompt relies on this.
