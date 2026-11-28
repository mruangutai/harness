# FEAT-2622 sign-off: operator answers, 2026-11-28

Source: plan run `2026-11-28-01-plan-product`. VERDICT PASS in 1 cycle, and all 7 panel findings are `resolved` in `plan.yaml`. The questions are the lead's OQ-SIG-01 and OQ-01..OQ-04, asked in one form. The main session put a recommendation on each, and the operator chose it every time.

- **OQ-SIG-01: sign as written.** D-06 (amends DEC-123), D-03 (product-lead triage authority, beyond the grilling) and the T-01/T-02 verify text rewritten at apply are accepted as read-at-signature items. No re-read run.
- **OQ-01: accept containment.** A `must_fix` entry is tied to a discounted finding by containment of its summary or PF id. Move `must_fix` to a structured shape only if a reworded contrived finding is actually seen getting through.
- **OQ-02: no era marker.** Land T-01 only when no lead run is open in any in-flight feature.
- **OQ-03: med.** The severity ceiling for a discounted finding is `med`, DEC-31's non-gating band.
- **OQ-04: shared `$ref`.** QA cites the shared `common.json` `$ref` once rather than running the five schema cases for each of the six personas.
- **Signature: approved.**
- **Rework ruling: 2 rounds / 90 minutes.**
