# STATE

## Current

- feature: FEAT-68-complex-function-third-wave
- run: validate-c3-validator
- squad: validator
- status: awaiting-user

## Open Questions

- VF-04-C3 (blocking, form/med, T-01, main-session-direct): the receipt's literal control-plane-root command still points at an absent relative receipt-scripts path and exits 2. Remedy: align the declared working directory and script home, then prove the exact preserved command without changing the implementation pin or A-1..A-4.
- VF-05-C3 (blocking, substance/high, new class, T-01, main-session-direct): the runnable generator overwrites the Reproduction section and uses separate suite executions for hashes/comparisons and raw differences, so D-02..D-05 cannot bind to the table streams. Remedy: generate one durable receipt whose invocation, raw streams, hashes, comparisons, differences, and ledger bytes derive from the same per-suite execution.
- Operator decision required: A-4's third and final evidence-only round is exhausted. Recommendation: do not ship while SC-02 and SC-04 remain unmet; authorize another bounded main-session-direct evidence fix only if continuing the feature.
- Lead digest: .harness/harness/features/FEAT-68-complex-function-third-wave/runs/validate-c3-validator/digest.md
