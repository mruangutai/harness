# FEAT-65 ship review

## Conclusion

FEAT-65 is ready for the operator's ship decision at review SHA `ffcc2dafa29fc56ae8a9634e9ed1508e1433661d`. Validate cycle 2 passed: SC-01 through SC-10 are met, `must_fix` is empty, the unit and integration matrix is green, and QA-65-01 is closed. CR-02 remains a non-blocking medium advisory.

## Definition of done

| Perspective | Signed outcome | Verdict | Discharged by | Evidence |
|---|---|---|---|---|
| operator | Preserve established fail-open/fail-closed verdicts and output bytes except ruled canonical diagnostics; keep authoritative direct commands loud and nonzero. | met | SC-01, SC-02, SC-09, SC-10 | `notes/research-FEAT-65-broad-exception-hooks-goalcheck-validate-c2.md`; `runs/validate-c2-validator/digest.md` |
| code maintainer | Use typed boundary catches, one classified `hook_guard` idiom, no process-control catches, identical DEC-234 prologues, and only two designed broad catches in `harness_boundary.py`. | met | SC-03, SC-04, SC-05 | `notes/research-FEAT-65-broad-exception-hooks-goalcheck-validate-c2.md`; `notes/clean-pin-byte-receipts.md` |
| reader | Trace all 77 sites, every operator-visible divergence, and reproducible clean-checkout evidence for the immutable implementation pin. | met | SC-06, SC-07, SC-08 | `notes/research-FEAT-65-broad-exception-hooks-goalcheck-validate-c2.md`; `notes/build-divergences.md`; `notes/clean-pin-byte-receipts.md` |

## Run record

No report round was spawned. This briefing was assembled from the seven recorded run digests:

- `runs/plan-product/digest.md`
- `runs/build-main-direct/digest.md`
- `runs/validate-validator/digest.md`
- `runs/fix-c0-main-direct/digest.md`
- `runs/validate-c1-validator/digest.md`
- `runs/fix-c1-main-direct/digest.md`
- `runs/validate-c2-validator/digest.md`

The plan run produced an approved four-task plan with five resolved panel findings. The main-session-direct build removed all 77 scoped broad catches, locked the census at zero scoped hooks and two designed boundary catches, aligned all five DEC-234 prologues, and retained clean-pin evidence. Validate c0 found missing fail-first receipts and an embedded broad catch; fix c0 closed both. Validate c1 narrowed the remaining defect to SC-01 final-pin provenance; fix c1 regenerated the receipt using the tests committed at the pin. Validate c2 independently closed QA-65-01 and passed all five reader seats.

## Validation result

- Review SHA: `ffcc2dafa29fc56ae8a9634e9ed1508e1433661d`
- Implementation pin: `97d14f0b`
- Test matrix: unit 42/42 and integration 69/69 passed.
- SC-01 provenance: 15 suites retained RED exit 1 to GREEN exit 0 with 110 RED output lines; 7 unchanged suites retained byte-identical normalized streams.
- Criteria: SC-01 through SC-10 met.
- Must-fix: none.
- Maximum remaining severity: medium advisory.
- UI: self-scoped out after a 59-file census found no UI surface.
- UAT: not required; every criterion is automated or inspection-based.

## Escalations and host gaps

Known host gap #1898 occurred exactly 7 times during validate c2: five PM lineage refusals before claim `5631b96060f7422b99a43185ba69f4c4` was bound, one validator-lead state-write refusal before claim `e46afac0294e4e469e201a0af1ac51cc` was bound, and one later validator-lead digest-rewrite refusal before active claim `2465e734dc544301a8320f0e4fd73f47` was established. The PM artifact and validator state retries succeeded under supervisor PID 2347. The requested one-block digest rewrite is main-session-direct because the validator-lead grant correctly refuses replacing a recorded run digest; no reader rerun is required. These host failures are not FEAT-65 product findings.

The terminal-yield gate also repeatedly rejected canonical reader, lead, and orchestrator returns while their durable artifacts remained recoverable. Validation relied on the artifacts after contract checks; this does not change the feature verdict.

## Spend and judgements

- Runs: 7 of the informational 20-run tripwire.
- Cycles: 3 of 10.
- Wall clock: 938 minutes total.
- Rework: 102 minutes across 2 signed rounds, exceeding the 90-minute ruling during the final successful validation. The ledger records `continue: stop`: all criteria passed, no unmet finding remains, and no further rework is authorized.
- Measured tokens: 483,588.
- Judgements: 6.

## Amendments

No builder amendment departed from the signed task text.

| At | Decision | Reason | Overruled |
|---|---|---|---|
| — | — | none | — |

Overrule rate: 0/0.

## Open questions

None block shipping. The operator's remaining decision is whether to ship the validated change and which proposed backlog rows, if any, to retain.

## Proposed backlog

| ID | Nature | Residual item |
|---|---|---|
| B-1 | bug | CR-02: constrain the embedded-program census so a harmless parseable `try/except` example in a non-executed string cannot falsely block plan routes. |
| B-2 | bug | Investigate the terminal-yield parser defect that rejected canonical reader, lead, and orchestrator returns despite valid durable artifacts. |
