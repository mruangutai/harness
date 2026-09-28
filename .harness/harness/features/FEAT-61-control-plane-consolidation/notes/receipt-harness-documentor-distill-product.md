# Documentor Expertise distillation receipt

```yaml
verdict: PASS
sources:
  total_read: 13
  feature_records:
    count: 11
    paths:
      - plan.yaml
      - notes/research-FEAT-61-control-plane-consolidation.md
      - notes/research-FEAT-61-control-plane-consolidation-goalcheck-plan.md
      - notes/research-FEAT-61-control-plane-consolidation-goalcheck-validate-c1.md
      - notes/research-FEAT-61-control-plane-consolidation-goalcheck-validate-c2.md
      - notes/research-FEAT-61-control-plane-consolidation-goalcheck-validate-c3.md
      - notes/answers-2026-09-20-validate-c2.md
      - notes/review-harness-code-reviewer-plan-c1.md
      - notes/review-harness-code-reviewer-plan-c2.md
      - notes/receipt-harness-documentor-docs-product.md
      - notes/ship-review-docs-product.md
  expertise_layers:
    count: 2
    paths:
      - .harness/expertise/harness-documentor.md
      - .harness/harness/expertise/harness-documentor.md
  observations:
    path: .harness/harness/features/FEAT-61-control-plane-consolidation/observations/harness-documentor.md
    status: absent
candidates:
  - id: C1
    result: accepted
    layer: craft
    section: Patterns
    entry: "WHEN intentional code duplication cannot be shared because each copy establishes the seam needed to import helpers DO put a reciprocal pointer beside every copy and record the constraint in one durable decision — readers encounter the copy before the rationale."
    reason: "Passes the six-spawns test: it changes how unavoidable duplication is explained in any repository. No existing entry covered reciprocal at-copy pointers plus one durable rationale. Patterns was full, so it displaced the narrower integration-branch numbering rule at P-02."
  - id: C2
    result: accepted
    layer: craft
    section: Patterns
    entry: "WHEN one false present-tense claim turns up in documentation DO sweep every live section with the concept's vocabulary, not only the struck phrasing, and classify historical hits before editing — paraphrases survive literal negative grep, while old records can remain true as evidence of what was previously decided."
    reason: "Passes the six-spawns test: future audits must distinguish stale live guidance from truthful historical records. Existing P-16 covered conceptual sweeps but not this classification, so it was sharpened in place without consuming another capped slot."
  - id: C3
    result: accepted
    layer: repository
    section: Patterns
    entry: "WHEN auditing Harness lifecycle documentation DO compare present-tense prose in `.harness/harness/docs/SPEC.md` with both `.harness/glossary.md` and `.claude/skills/harness/bin/factory_config.py` — the glossary explains reader-facing distinctions, while the station table decides the live vocabulary and board/terminal split."
    reason: "Passes the six-spawns test for this repository and points to living exemplars rather than copying values. Repository G-04 already resolves code-versus-SPEC conflict; this adds the missing joint vocabulary check against the glossary. The section had room."
rejected_candidates: []
exact_ops:
  craft:
    - op: replace
      target: P-02
      section: Patterns
      entry: "WHEN intentional code duplication cannot be shared because each copy establishes the seam needed to import helpers DO put a reciprocal pointer beside every copy and record the constraint in one durable decision — readers encounter the copy before the rationale."
      why: "The shipped bootstrap audit showed that a durable rationale alone is not enough: readers need a pointer at every unavoidable copy. This general rule is more broadly reusable than the displaced numbering rule."
    - op: replace
      target: P-16
      section: Patterns
      entry: "WHEN one false present-tense claim turns up in documentation DO sweep every live section with the concept's vocabulary, not only the struck phrasing, and classify historical hits before editing — paraphrases survive literal negative grep, while old records can remain true as evidence of what was previously decided."
      why: "The documentation audit found stale live lifecycle prose while historical decision and build records remained accurate in context; the existing concept-sweep rule needed the live-versus-historical classification."
  repository:
    - op: add
      target: P-07
      section: Patterns
      entry: "WHEN auditing Harness lifecycle documentation DO compare present-tense prose in `.harness/harness/docs/SPEC.md` with both `.harness/glossary.md` and `.claude/skills/harness/bin/factory_config.py` — the glossary explains reader-facing distinctions, while the station table decides the live vocabulary and board/terminal split."
      why: "The post-validation audit found SPEC stale while the glossary and station table jointly exposed the correct reader vocabulary and executable station split."
section_counts:
  craft:
    line_budget: "45 -> 45 of 150"
    Patterns: "15 -> 15"
    Gotchas: "15 -> 15"
    Outcomes: "10 -> 10"
    Open: "0 -> 0"
  repository:
    line_budget: "18 -> 19 of 40"
    Patterns: "6 -> 7"
    Gotchas: "7 -> 7"
    Outcomes: "0 -> 0"
    Open: "0 -> 0"
scoped_checks:
  - command: "python3 .agents/skills/harness/bin/check-expertise.py .harness/expertise/harness-documentor.md"
    result: "exit 0; OK"
  - command: "python3 .agents/skills/harness/bin/check-expertise.py .harness/harness/expertise/harness-documentor.md"
    result: "exit 0; OK"
files_touched:
  - .harness/expertise/harness-documentor.md
  - .harness/harness/expertise/harness-documentor.md
open_questions: []
artifact: /Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-61-control-plane-consolidation/notes/receipt-harness-documentor-distill-product.md
```
