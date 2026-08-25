# UI reviewer expertise distillation

BLUF: Accepted all three digest-skim candidates as one craft gotcha; no observation-derived knowledge or repository-specific update qualified.

## Sources and candidate judgments

- Observation source: `.harness/harness/features/FEAT-36-merge-gitignore-coverage/observations/harness-ui-reviewer.md` was absent. Accepted: 0.
- Digest-skim source: accepted 3, rejected 0.
  1. **Accept** — a pinned changed-object census is the evidence needed before a zero-surface decline; it closes the extension-only blind spot in existing P-01.
  2. **Accept** — comparing potentially interactive production utilities across pins distinguishes a test/config-only delta from a CLI interaction change.
  3. **Accept** — accessibility, theme parity, fidelity, and interaction states become not-applicable only after the relevant changed surface is measured absent.
- Rejected candidates: none.

## Curation and receipts

- Craft counts before → after: Patterns 15→15; Gotchas 10→11; Outcomes 4→4; Open 0→0.
- Repository counts before → after: Patterns 1→1; Gotchas 0→0; Outcomes 0→0; Open 0→0.
- Stale dispositions: no stale entries found; all existing craft and repository entries retained. Repository P-01 remains a repository fact, while new knowledge is cross-repository review craft.
- Exact applied op: `{ op: add, section: Gotchas, entry: "WHEN a changed-path extension census appears UI-free DO compare all pinned changed objects and potentially interactive production utilities before scoping out — extensionless CLI changes remain possible, and every not-applicable design or accessibility dimension requires measured absence.", why: "Consolidates three independently accepted digest-skim candidates into one durable cross-repository rule." }`
- Assigned ID and merge receipt: `ADDED G-11`; `APPLIED .harness/expertise/harness-ui-reviewer.md`.
- Changed-file check: `OK   .harness/expertise/harness-ui-reviewer.md`.
- Repository Expertise was unchanged, so no check was required.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Three digest candidates distilled into one checked craft gotcha; no observation or repository-tier update qualified."
  mode: B
  in_scope: true
  severity_max: info
  findings: 0
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  accepted_counts: { observation: 0, digest_skim: 3 }
  rejected_candidates: []
  stale_dispositions: ["No stale entries found; all existing craft and repository entries retained."]
  section_counts:
    craft: { Patterns: "15->15", Gotchas: "10->11", Outcomes: "4->4", Open: "0->0" }
    repository: { Patterns: "1->1", Gotchas: "0->0", Outcomes: "0->0", Open: "0->0" }
  check_results: ["OK   .harness/expertise/harness-ui-reviewer.md"]
  open_questions: []
  files_touched: [.harness/expertise/harness-ui-reviewer.md, .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-ui-reviewer-distill-validator.md]
  expertise_update:
    - { op: add, section: Gotchas, entry: "WHEN a changed-path extension census appears UI-free DO compare all pinned changed objects and potentially interactive production utilities before scoping out — extensionless CLI changes remain possible, and every not-applicable design or accessibility dimension requires measured absence.", why: "Consolidates three independently accepted digest-skim candidates into one durable cross-repository rule." }
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-ui-reviewer-distill-validator.md
```
