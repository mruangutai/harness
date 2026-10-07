# Direct readiness-contract repair authorization

On 2026-10-05 MAIN asked: “Authorize a separate repair of Harness’s QA and receipt/state blockers before resuming #2037?” Operator selected **Repair blockers separately**: keep #2037’s four-file scope intact; investigate and repair enforcement separately, outside the enforcement path being changed, then resume review/UAT.

Repair checkout: `.claude/worktrees/harness/BUG-2037-readiness-contracts`, created using `feature-worktree.py create --repo harness --id BUG-2037-readiness-contracts`. DEC-174 governs: MAIN makes ordinary direct edits and explicitly runs regression tests; no governed implementation team executes changes to its own validators, hooks, gates or their tests. Read-only research is not an implementation run. No PR or merge authorization is implied.

Observed failures, retained in the separate FEAT-2037 guidance worktree:
- `validate-digest.py` rejects QA PASS with matrix_ok true and fail_first [] even though the BRIEF declares zero automated SCs. Existing docs matrix has no required kinds. Hypothesis: the fail-first predicate is unconditional and loses the feature’s declared verification modes. Discriminating regression must accept an explicitly known zero-automated feature while still refusing missing evidence for automated criteria and unknown context.
- Two engineering lead returns were refused; later evidence reports a custom outputSchema/schemaMode dispatch followed by premature claim release. Do not assume a binding root cause until source/raw records distinguish it. No binding may be reconstructed or forged.
- A canonically closed refused-return run with state.yaml complete and a prose-only digest still trips INV-15. Hypothesis: state validation treats a host-refused terminal run as an accepted lead result. Distinguishing tests must retain rejection of invalid ordinary completed runs and prove honest refused-return history stays BLOCKED rather than PASS.

No historical ESCALATE/BLOCKED result becomes PASS through repair. Preserve the guidance feature’s real failed checks, invalid advancement, independent SC-04 inspection and 27 NOT RUN UAT assertions. Resume only after genuine runtime receipts establish the required gates.
