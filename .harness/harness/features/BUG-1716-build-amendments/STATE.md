# STATE

## Current

- feature: BUG-1716-build-amendments
- run: .harness/harness/features/BUG-1716-build-amendments/runs/validate-validator/digest.md
- squad: validator
- status: validate c0 failed; awaiting Main fixes V-01 through V-08
- review_sha: c2bf2f3a2ffba5faf243867a915f082da17f387d

## Open Questions

- V-01 (T-04): Make `record-amendments` genuinely all-or-nothing across `plan.yaml` and `feature.json`, including failure after ledger transformation but before plan commit, and prove that failure mode.
- V-02 (T-03): Raise `_select_amendment` from production code grade 3 to the required grade 4.
- V-03 (T-04): Raise `cmd_record_amendments` from production code grade 3 to the required grade 4.
- V-04 (T-05): Raise `case_inv40_signed_text` from test code grade 1 to the required grade 3.
- V-05 (T-04): Raise the deterministic task-hash scenario from test code grade 1 to the required grade 3.
- V-06 (T-04): Raise the BUG-285 record-amendments scenario from test code grade 1 to the required grade 3.
- V-07 (T-03): Raise the feature-schema runner `main` from test code grade 1 to the required grade 3.
- V-08 (T-02): Raise `_amendment_entry_errors` to clear the required unit code-grade gate.
