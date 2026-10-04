```yaml
VERDICT: PASS
DIGEST:
  headline: "All three relayed PM lessons remain accepted; repository P-10 now preserves both candidate judgments within the merged-authoring length limit."
  source_count: 11
  sources_read:
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
  observations: "No observations/harness-pm.md exists for this feature."
  judgments:
    - candidate: 1
      outcome: accepted
      reason: "Recurs whenever a signed plan carries an unsupported classification; correcting the malformed record prevents vocabulary drift. Existing Expertise does not cover unsupported change_type values."
      op: "repository Patterns add P-10"
    - candidate: 2
      outcome: accepted
      reason: "The authoring-side prevention is independently useful across future plans and combines cleanly with candidate 1. Existing repository G-06 covers test_kinds parsing, not test_matrix classification."
      op: "repository Patterns add P-10"
    - candidate: 3
      outcome: accepted
      reason: "Direct builds may delegate parallel edits again; explicitly binding relative paths to the assigned feature worktree prevents cross-checkout writes. Existing repository G-09 covers edit headers, not delegated worktree confinement."
      op: "repository Patterns add P-12"
  exact_ops:
    - op: add
      target: P-10
      section: Patterns
      layer: repository
      entry: "WHEN selecting a plan task's change_type DO cite a value from .harness/harness.json test_matrix so the hard gate can resolve required test kinds; an unsupported value is a malformed plan record to correct, never grounds to extend the matrix."
      why: "Original merge of candidates 1 and 2; this 38-word authoring result exceeded the 21-word longer input and is superseded by the corrective replace below."
    - op: add
      target: P-12
      section: Patterns
      layer: repository
      entry: "WHEN DEC-174 routes a build main-session-direct and the main session parallelizes task subagents DO state that all relative-path edits must remain inside the assigned feature worktree."
      why: "Captures candidate 3 at the repository layer because it depends on a repository decision and execution route."
    - op: replace
      target: P-10
      section: Patterns
      layer: repository
      entry: "WHEN selecting change_type DO cite the configured test-matrix vocabulary; correct unsupported values as malformed records, never extend the matrix."
      why: "Corrects the original overlong merge while preserving candidate 2's prevention and candidate 1's malformed-record correction."
      word_count: 19
      input_word_counts: [21, 19]
  final_entry:
    target: P-10
    section: Patterns
    layer: repository
    entry: "WHEN selecting change_type DO cite the configured test-matrix vocabulary; correct unsupported values as malformed records, never extend the matrix."
  counts:
    craft:
      lines: "45 -> 45"
      Patterns: "15 -> 15"
      Gotchas: "15 -> 15"
      Outcomes: "10 -> 10"
      Open: "0 -> 0"
      displacement: none
    repository:
      lines: "31 -> 33"
      Patterns: "10 -> 12"
      Gotchas: "15 -> 15"
      Outcomes: "1 -> 1"
      Open: "0 -> 0"
      displacement: none
      correction: "P-10 replace changed no counts; final repository counts are 33 lines, 12 Patterns, 15 Gotchas, 1 Outcome, and 0 Open."
  rejected_candidates: []
  scoped_checks:
    - command: "python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-expertise.py /Users/molchairuangutai/GitHub/harness/.harness/harness/expertise/harness-pm.md"
      result: "OK   /Users/molchairuangutai/GitHub/harness/.harness/harness/expertise/harness-pm.md"
  files_touched:
    - .harness/harness/expertise/harness-pm.md
    - .harness/harness/features/FEAT-61-control-plane-consolidation/notes/research-FEAT-61-control-plane-consolidation-distill-product.md
  open_questions: []
  expertise_update:
    - "add repository Patterns P-10"
    - "add repository Patterns P-12"
    - "replace repository Patterns P-10"
artifact: /Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-61-control-plane-consolidation/notes/research-FEAT-61-control-plane-consolidation-distill-product.md
```
