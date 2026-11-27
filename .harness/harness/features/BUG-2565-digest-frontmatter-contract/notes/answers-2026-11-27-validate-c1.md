# Operator rulings on validate run 2026-11-27-06-validate-validator (ESCALATE)

Answered 2026-11-27 through the main session's form. Every ruling took the recommended option.

- **OQ-1: amend T-03.** T-03's `files:` now owns `tests/integration/canonical-reader-classification.json`. The fix round adds the rows for `digest_projection.py` and `gen-agent-output.py` after the T-03 refactor.
- **OQ-2: accept a named residual and open a follow-up issue.** The yield still allows a `validate-digest.py` exit 0 with empty, malformed or unknown stdout (`classifyAnswer`). This is not a regression, and every class SC-01 enumerates is refused. The positive-acknowledgement protocol moves to its own issue.
- **OQ-3: accept QA's execution as SC-08's evidence.** QA ran the T-03 parity command at the pin and got 16/16 `parity ok`. The reviewer's read-only guard refused it.
- **OQ-4: narrow the claim.** D-03 bounds task data only: no refused object reaches the parent as task data. The child's own final prose may quote it. README, BUILD and a correction line in `notes/research-yield-refusal-probe.md` say so.
