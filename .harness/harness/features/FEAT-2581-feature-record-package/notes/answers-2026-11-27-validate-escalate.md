# FEAT-2581: operator answers to the validate ESCALATE, 2026-11-27

Run `2026-11-27-01-validate-validator` (review_sha 62da4501) returned ESCALATE with two open
questions. The operator answered through the main session's form after asking how likely CR-2's
failure was.

- **OQ-V2 (CR-1):** refactor. DEC-209's code grade covers notes/receipt-scripts/ as the policy
  reads today, and no exemption is sought. All twelve below-bar records are brought to grade 4:
  the seven high ones and the five grade-2 ones (`code-grade.py` exits 1 on any of them).
- **OQ-V1 / ESC-1 (CR-2, verifier half):** dispositioned as an accepted risk, so T-03's signed
  verify stays unamended. The evidence at the time: all 1,893 by/date/reason values in the
  631 committed rulings are non-blank strings, no committed tool writes ruling metadata (the
  generator only seeds an empty `[]` file when none exists),
  and the scripts are frozen proof artefacts after ship. The generator half is fixed:
  `Derived.ruled` requires non-blank strings. A null-metadata mutant on `audit:stdout` gives
  `divergence: audit:stdout UNRULED` and `overall: FAIL`, and the real rulings still pass.
- **SEC-1:** folded into the same rewrite. The replay scratch, the ledger, the fixtures and the
  replay ledger are now removed fail-loud (a tree that cannot be removed, or a symlink in its
  place, stops the run) and recreated mode 0700. Their fixed paths are unchanged. Fix round 2,
  after validate 02: the shared `/tmp/feat2581-ledger` parent is created mode 0700, or accepted
  only when it is a real directory owned by this user and closed to group and other writes.
- **SEC-2:** not routed, as the validator lead recommended.
