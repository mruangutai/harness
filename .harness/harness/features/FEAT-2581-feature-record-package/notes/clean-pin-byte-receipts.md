# FEAT-2581 clean-pin byte receipts — summary

Authoritative lines: `clean-pin-byte-receipts.generated.md` (derived by `receipt-scripts/feat2581-cleanpin.py`
from `measurements/{baseline,pin}.jsonl.gz`). Baseline e12381fd, implementation pin c91df7a5.

- Every verdict PASS: grade_bar, unit_files, integration_files, case_identity, cli_identity
  (210 checkout, 1 copied, 12 bun records per side), replay_identity (43 records x 9 steps,
  byte-identical), d02_inventory (items 2, 7, 10, 11 measured; 1, 3-6, 8, 9 source-only), audit.
- 631 divergences, all ruled by the operator on 2026-11-27 in `divergence-rulings.json`:
  A 21 relocation/renames (D-02 diagnostics, traceback frames, test labels, audit count),
  B 481 corpus growth from this feature's own files (check-plan-routes ordinal shift; content-matched),
  C 129 nondeterminism outside the change (concurrency order, random names, clock SHAs, timings).
- A first measurement was discarded: the bun preload did not reach Bun's spawn env, so bun-class
  records were zero; the preload was fixed and both sides re-measured once.
- Validate fix round 1 (`answers-2026-11-27-validate-escalate.md`): the receipt scripts were refactored
  to DEC-209 grade 4 (CR-1), `ruled` now requires non-blank string by/date/reason (CR-2, generator half),
  and the scratch directories are private and fail-loud (SEC-1). The receipt was regenerated with
  `--reuse` from the unchanged measurements. Every line except the five changed `script_sha256` lines
  and the `generated` stamp is identical, and `build-divergences.md` is byte-identical. The measurements
  were taken with the pre-refactor recorder, ledger-driver and replay bytes, which are recorded at `c65ceb81`.
