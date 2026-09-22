# FEAT-53 signed-plan preimage restoration

## Conclusion

All six contracted task fields in `plan.yaml` were initially structure-equivalent to the engineering digest's exact `now` values and were restored, one field at a time, to its exact `was` value through the control-plane `plan-merge.py amend --show` plus hash-checked `amend` workflow. The scoped plan diff contains only those six field changes. No T-32/UI amendment or other plan field was changed.

Source: `runs/2026-09-22-ledger-repair-eng/digest.md:20-56`.
Target: `plan.yaml` tasks T-02, T-20, T-24 and T-25.

## Approval state

Before restoration (`plan.yaml:6-9`):

- status: approved
- approved_by: operator
- date: 2026-09-16

After restoration (`plan.yaml:6-9`):

- status: approved
- approved_by: operator
- date: 2026-09-16

No approval reset receipt was emitted by any amendment.

## Six compare-and-splice actions

1. `T-02.verify`: initial `--show` matched digest `now` (`merge-gitignore.py`; field-block SHA-256 `21c3ab07b389a0728c73244fb5e05fb1c5ab47cfe87c3d9d410ade7027c85b94`); hash-checked amend restored digest `was` (`merge-gitignore.sh`); post-show SHA-256 `d93f70276f72088f940d646b3b4b5f6b27226f66089a5cf9b85974f36d17cbf2`.
2. `T-20.files`: initial `--show --yaml-value` matched the five-entry digest `now` list (SHA-256 `7789a939d4037ed4dca85353fe81b0ab8b2f1b372cdc8e44dcd366d2caccc2f9`); hash-checked amend restored the three-entry digest `was` list; post-show SHA-256 `fd8edb19c79bc5c96d59c6af26b14dc45569393f87557d4521740eda6678edff`.
3. `T-24.files`: initial `--show --yaml-value` matched the four-entry digest `now` list (SHA-256 `031af060fc9b40eb33a6818f632ea2e2d280ea30297ec0a8a66f227c63a7e000`); hash-checked amend restored the five-entry digest `was` list; post-show SHA-256 `eaa89c71b1f928d3574363d21d7f7c8dda58aa92242f34c2e2760973b8e08962`.
4. `T-24.verify`: initial `--show` matched the digest `now` integration/layout/upgrade command (SHA-256 `d04d66e26c38f7d6a38e200d4bb671f87183c14b52388a4766dc69587462582f`); hash-checked amend restored the digest `was` bin-test/check-kinds command; post-show SHA-256 `6ef8e2347a40bb28b26f5e901b7906671e60cd922a4e2380a8ff9e14c63b51ca`.
5. `T-25.files`: initial `--show --yaml-value` matched the thirteen-entry digest `now` list (SHA-256 `df9d88f1bdba142e1e278c4ac819c08280d6fb208eb7778c2cbecc2d197c2770`); hash-checked amend restored the twelve-entry digest `was` list; post-show SHA-256 `6a94b921740013927564853b256ce1d30c2a3188ac3fc0745876afaeb1738c7e`.
6. `T-25.verify`: initial `--show` matched the digest `now` integration/backfill/adapters/layout command (SHA-256 `3831ac8288ea8b2986deac801385833cb1a99b243722f95203ece9beb5b2b9f9`); hash-checked amend restored the digest `was` bin-test/backfill command; post-show SHA-256 `4d257eecc6cee7aea7e779f428b37e161b5db9e78448e8e4e5cd5f6a91f16f22`.

Each amend emitted `AMENDED tasks:<task>.<field>` and `APPLIED <target plan>`. A file-scoped `git diff -- plan.yaml` showed four hunks containing exactly the six named fields and no approval or other-field change.

## Verification boundary

Per dispatch, no test, build, formatter, linter, validator, or project-wide command was run. Proof is the six pre-mutation and six post-mutation `plan-merge.py amend --show` reads, the six successful hash-checked amend receipts, the unchanged approval read, and the file-scoped diff.
