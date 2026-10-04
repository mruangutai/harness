# Code review — FEAT-69 — c0

## Verdict

FAIL. Stage 1 does not pass: SC-02 requires normalized byte identity unless the operator rules otherwise, but the committed clean-pin receipt reports `All identical (normalised): NO` and no operator judgement rules the five remaining lines acceptable. Per the two-stage protocol, Stage 2 was not begun.

## Stage 1 — spec compliance

- **SC-01 passes:** the post-pin generated and red-first receipts identify baseline `a726bad8f74d23e6c1f07409383bb88d1da8fbcf` and pin `db488aa7c78e392c788bd5839a43ebf4ba562ea1`, show the baseline red on the four named below-bar functions, and show all 295 pin functions across the entry plus 12 package files at grade 4–5 (`notes/clean-pin-byte-receipts.generated.md`, `notes/red-first-receipts.md`).
- **SC-02 fails:** 12/13 measurements are identical, but `full_table` stdout differs by five exact lines (`notes/clean-pin-byte-receipts.generated.md`, “Differences after the one normalisation”). The four INV-32 lines arise from the resolved panel findings carried by the pin; the fifth arises because the pin records `plan-product` at `.harness/harness/features/FEAT-69-long-file-check-state-package/feature.json:8-20` while its ignored run directory is absent in a clean checkout. `notes/build-divergences.md` contains implementer rulings, but SC-02 says any difference leaves the criterion unmet “unless the operator rules otherwise”; the pin’s only operator judgements are the baseline-SHA amendments at `feature.json:37-48`, not rulings on D-02/D-03.
- **SC-03 passes by inspection of the pin and the receipt evidence:** `check-state.py` remains the sole executable entry; `check_state/table.py` owns the exact ordered table and all family imports; `check_state/runner.py` owns selection/execution; the settled family roster matches `ROW_FAMILIES`; and the package-aware lock builds one module-qualified function table, resolves imports and `Ctx` methods transitively, checks family placement, authority, module body, no-reparse, declared reads, and a zero broad-catch ceiling. The committed lock receipt is byte-identical baseline-to-pin.
- **SC-04 passes inspection:** pin `db488aa7…` predates receipt commits `778175ab…` and `e851891e…`; the scripts and records name full baseline/pin identities, clean detached checkouts, commands, one-execution provenance, raw/normalized hashes, grade records, and exact divergence lines.
- Amendments were checked against the BRIEF/decisions: the T-03 file addition follows the moved `features` reader; the two baseline-SHA amendments align the proof with SC-01/SC-02. No further mismatch found.

## Finding

1. **High · substance · T-04 · SC-02 mismatch** — `.harness/harness/features/FEAT-69-long-file-check-state-package/feature.json:8-20` at the reviewed pin records `plan-product`, and the pin also contains four resolved panel findings; in clean detached baseline-versus-pin full-table runs this state produces five pin-only stdout lines, so normalized stdout is not byte-identical. Expected bytes are no pin-only bytes at all: the pin’s normalized `full_table` stdout must equal the baseline’s byte-for-byte, or the operator must explicitly rule these exact five lines otherwise as SC-02 permits. The unexpected exact lines are:
   - `  note       INV-32: FEAT-69-long-file-check-state-package finding PF-c2128122a0bb540f061d16fb1410fe65 disposition resolved.`
   - `  note       INV-32: FEAT-69-long-file-check-state-package finding PF-340baf59ff3499fe4a22647112179b9a disposition resolved.`
   - `  note       INV-32: FEAT-69-long-file-check-state-package finding PF-8df76c10f1a644c190f4873f2bcb3ccd disposition resolved.`
   - `  note       INV-32: FEAT-69-long-file-check-state-package finding PF-bc67c8325e2128cacd86013cfd559654 disposition resolved.`
   - `  note       FEAT-69-long-file-check-state-package: run plan-product is referenced but its dir is absent (pruned, or never created).`

## Assessed and dismissed

- The package lock’s unreadable package-file path is fail-closed: `_checker_trees` emits `source_parse: unreadable`; it does not silently omit the failure.
- Imported family calls and `ctx.<method>` calls are resolved through `_PackageFunctions`; the cross-module boundary is not vacuous.
- The full-table differences are fully and exactly ledgered, so there is no receipt-form omission; the blocker is the missing operator ruling required by SC-02, not missing evidence.
- The changed-test mechanical grade-2 record in `tests/unit/test-check-skill-refs.py:52` is advisory and unrelated to SC-01’s explicitly bounded production surface; because Stage 2 is gated off, no code-quality finding is raised from it.

## Principles applied

None.
