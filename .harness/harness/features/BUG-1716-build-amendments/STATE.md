# STATE

## Current

- feature: BUG-1716-build-amendments
- run: .harness/harness/features/BUG-1716-build-amendments/runs/fix-c1-validator/digest.md
- squad: validator
- status: validate c1 failed; awaiting Main fix for V-01; V-02 through V-08 closed
- review_sha: f602c7eee7761ce4325accba7a04678794c7ed69

## Open Questions

- V-01 (T-04): Restore plan bytes for every ledger-write failure after plan replacement, preserve or explicitly report rollback failure, and prove an ordinary post-plan-write I/O exception leaves both plan.yaml and feature.json byte-identical.
