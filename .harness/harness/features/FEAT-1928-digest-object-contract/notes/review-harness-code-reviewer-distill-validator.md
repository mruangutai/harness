# Code-reviewer distillation recovery

**PASS: two repository-specific review invariants are durable and genuinely new; one control-plane incident is rejected from Expertise while its historical BLOCKED outcome remains unchanged.** This was proposals-only distillation: no Expertise mutation, source review, grader, checker, test, build, lint, formatter, or probe was performed.

## Candidate judgments

1. **Accept — repository Patterns P-02.** The append correction established that a durable record writer must prove the prospective bytes select the exact submitted object through the production reader before its first write; otherwise malformed prose can report success while successors read stale or absent data (`notes/review-harness-code-reviewer-append.md`, “Original T-02 F2 disposition”).
2. **Accept — repository Patterns P-03.** Harness keeps lexical feature placement separate from trusted run/destination authority, and lifecycle transitions clear and rebind the latter; treating cached placement as authority would permit an intervening append under stale identity (`notes/review-harness-code-reviewer-finalmerge.md`, “Lifetimes do not alias”).
3. **Reject — harness defect, not Expertise.** The original rejected PASS yield, released claim, refused correction/message, and resulting shape/claim-only BLOCKED remain historical; the later successful receipt write does not reclassify or erase them (`notes/review-harness-code-reviewer-finalmerge.md`, “Form-only terminal reconciliation”). Per the observation/defect boundary, this stays an outside-feature control-plane question rather than reusable Expertise.

## Proposed write-less operations

Destination: repository-tier `.harness/harness/expertise/harness-code-reviewer.md`. These operations were not applied.

- `add` `Patterns` `P-02`: “WHEN reviewing Harness durable-record appenders DO require the production reader to select the exact submitted object from prospective bytes before the first write — unreadable or stale selection must refuse with existing bytes unchanged.”
- `add` `Patterns` `P-03`: “WHEN reviewing Harness run revival or digest writes DO keep lexical feature placement separate from trusted run and destination authority, clearing and rebinding authority at lifecycle boundaries — cached placement alone must never authorize a write.”

## Gate fields

- `code_grade: n_a`
- `reviewed: none`
- Open questions: none.
