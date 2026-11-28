# Plan panel fan-in — FEAT-2622, cycle 1

Three readers ran; every finding is transcribed at its reader's own severity and kind (no PF- ids; record-panel computes identity).
- scope: notes/review-harness-code-reviewer-plan-c1.md (VERDICT FAIL; 2 high substance carry its must_fix; open question Q1 on DEC-123 roll-up)
- should-not-exist: fable-advisor returned inline (no write grant); its three findings are below verbatim in summary. It found the mission proportionate (no mission-scope objection).
- design: notes/review-harness-ui-reviewer-plan-c1.md (self-scoped out, PASS, no findings)

Practicality note for apply (shape only, severities unchanged): each reader stated exposure. Scope's two highs are self-rated plausible/routine — not discountable. Fable's three are low/info by its own rating, two self-described contrived and no_worse; advisory.

Scope's Q1 (how a reader verdict caused only by discounted findings rolls up under DEC-123 worst-wins) is the same defect as its first high finding; apply resolves both together.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: returned FAIL carrying 4 findings; note at notes/review-harness-code-reviewer-plan-c1.md
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: resolved and returned three findings inline
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: self-scoped out (no user-facing surface); PASS with no findings
  findings:
    - reader: scope
      severity: high
      kind: substance
      summary: T-01/T-03/T-04 leave a path for a discounted finding to force FAIL after triage
    - reader: scope
      severity: high
      kind: substance
      summary: T-02 requires its record-panel test to fail even when the writer is correct
    - reader: scope
      severity: med
      kind: substance
      summary: The verification blocks omit or substitute required fail-first witnesses
    - reader: scope
      severity: low
      kind: form
      summary: Add a keep disposition for DEC-229
    - reader: should-not-exist
      severity: low
      kind: substance
      summary: "The eng-lead persona silently inherits the `unrated` loophole D-01's own rationale forbids: validate-digest refuses `unrated` only for code/security/ui reviewers (T-01 intent item 3c), yet eng-lead hosts no non-harness reader"
    - reader: should-not-exist
      severity: info
      kind: proportionality
      scope: task
      summary: T-02's two new INV-32 cases in test-check-state-records test a row record-panel already refuses to write and legacy rows cannot form — a new test for a trigger the feature's own rule would call contrived
    - reader: should-not-exist
      severity: info
      kind: form
      summary: "is_non_gating (\"none\" plus NON_GATING_SEVERITIES) creates a second non-gating set beside the one gates_signature uses, while SC-06 claims the non-gating set is defined once"
  severity_max: high
```

## should-not-exist — full `why` text (fable-advisor has no write grant)

1. eng-lead unrated (low, substance): trigger plausible — eng-lead yields findings routinely (build.yaml lead flow; digest_schema.py:46); consequence no_worse mechanically (unrated gates), but SC-04 and T-01's test list pin neither acceptance nor refusal for eng-lead. Fix: add eng-lead to the refusal list in T-01 item 3c with one SC-04 case, or one D-01 sentence saying why eng-lead counts as a transcribing lead.
2. INV-32 cases (info, proportionality task): the only path to a discounted-high panel row is a compound hand edit — contrived; omission no worse than today (gates_signature already gates; panel_findings.py:116). Keep the shape_faults predicate call; drop the two mandated integration cases.
3. is_non_gating second set (info, form): trigger contrived (no digest uses severity "none"); consequence no worse. One sentence in T-01 intent aligning the sets or stating why "none" is practicality-non-gating but signature-gating.
