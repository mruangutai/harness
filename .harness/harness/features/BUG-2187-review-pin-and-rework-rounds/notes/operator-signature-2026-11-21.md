# Operator signature: BUG-2187, 2026-11-21

At grilling, the operator chose "presigned". That pre-approves the intake built on the four settled decisions:
- INV-33 ignores station values.
- `rework_rounds` counts regate judgements.
- Pin verb plus guidance.
- A pre-signed signature.

- The intake (run `2026-11-21-01-patch-product`, PASS) carries those four decisions unchanged, as SC-01..SC-03 under one T-01.
- T-01 is main-session-direct under DEC-174.
- Rework ruling: 1 round / 45 minutes.
- No panel ran (patch mission), so nothing is overruled.
- One build note, made by the main session, not by the operator. SC-02's guidance regressions will assert that every `feature-record.py` verb the guidance names exists in the CLI. They will not pin the guidance's prose.
- Amendment during build: `tests/integration/canonical-reader-classification.json` was added to T-01 `files:` and to the lanes table. It was recorded as an `amendment` judgement on `T-01.files`, because the canonical-reader audit requires a row for INV-33's new plan-text reader. The operator reviewed the diff and chose "accept" under the existing signature. No re-sign.
