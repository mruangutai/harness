# Build QA rerun — PASS

BQ-01 is resolved: with the signed Homebrew Python selected, both configured commands resolve the harness root, discover their explicit named-script sets, and exit successfully. The previous `python3` 3.9.6 rejection of runner-required `-P` is no longer on the execution path.

## Environment and configured matrix

- Environment change only: `PATH=/opt/homebrew/bin:$PATH`.
- Selected interpreter: `/opt/homebrew/bin/python3`, `Python 3.14.5`.
- `unit` (configured command exactly): `PATH=/opt/homebrew/bin:$PATH .agents/skills/harness/bin/run-unit-tests.sh --kind unit` — exit 0; 29/29 named scripts passed; 0 failed; 28.91 s.
- `integration` (configured command exactly): `PATH=/opt/homebrew/bin:$PATH .agents/skills/harness/bin/run-unit-tests.sh --kind integration` — exit 0; 28/28 named scripts passed; 0 failed; 255.67 s.
- The rerun executed the configured `.agents/skills/harness/bin/run-unit-tests.sh` matrix commands as assigned. T-03's distinct plan verify clause, carried verbatim for traceability, is `.claude/skills/harness/bin/run-unit-tests.sh --kind integration`; it was not the command this rerun was asked to execute.
- The runner emits one `PASS`/`FAIL` per explicitly enumerated named script (`run-unit-tests.sh:30-32,148-163`); no runner, load, import, collection, or assertion failure occurred.

## Gate assessment

The prior direct-coverage assessment remains adequate and is not contradicted by this rerun: it found behavioral coverage for grading, CLI, gate-policy, digest-validation, and route-resolution contracts. The matrix floor remains satisfied: T-03 is `logic`, requiring `unit`; this rerun additionally executed the configured active `integration` command as required by build QA. `functional` remains signed excluded; no other kind is required by the prior assessment.

Prior artifacts preserved and reconciled:

- `.harness/harness/features/FEAT-43-code-risk-grading/runs/build-qa-validator/digest.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/qa-build-qa.md`

Send-backs: 1 (lead attribution correction received). Open questions: none.
