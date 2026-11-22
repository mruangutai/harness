# Validator distillation

PASS — four members completed independent judgments; all rejected redundant candidates. Lead replaced repository G-02 to require pin-bound durable artifact evidence rather than assume ignored run digests never survive. No diff reviewed, suite run, grading, render or source edits performed in distillation.

QA accepted 0/2 relayed candidates: unshown assertion discrimination is already covered, and pinned artifact tracking is already craft G-15. Code accepted 0/1: required grading versus forbidden execution is already explicit skill guidance; its historical authorization request was resolved. Security accepted 0/0 relayed and 0/3 independent candidates; UI accepted 0/0 relayed and 0/1 independent theme. Their rejection reasons and source anchors are in notes/qa-distill.md and notes/review-harness-{code-reviewer,security-reviewer,ui-reviewer}-distill.md. PM's goalcheck was skimmed as cross-lens evidence; PM distillation belongs to the product run, not a duplicate dispatch here.

Lead accepted 1/1 Main-sourced candidate: local presence under ignored runs/** is not proof of repository-state completeness or survival. QA c0 records the superseded repo-state failure and successful final pin; Main supplies the force-tracking cause. Repository G-02's old unconditional absence/survival claim was too strong. The replacement records the evidence check, not a force-tracking workaround or a finding that Harness is defective. Applied batch: 633ea7df6ef1eea50f8ea6b054b5cb2d81f5fbdec02460213ebc66be00aa223d; receipt: notes/expertise-receipt-0c2622b4cfd35185061668a20dfc6119b1162ad049a17ce00b40bc1b5dc29fd4.json. Tool reports REPLACED G-02 and successful check/application.

Counts below are Patterns/Gotchas/Outcomes/Open, before → after. Member no-op counts come from their supplied Expertise and durable reports; lead repository counts come from the application receipt. No member applied ops or fabricated a no-op receipt.

| Persona | Craft before → after | Harness repository before → after |
|---|---|---|
| QA | 15/15/10/1 → 15/15/10/1 | 0/11/0/0 → 0/11/0/0 |
| Code | 15/15/10/0 → 15/15/10/0 | 3/11/0/0 → 3/11/0/0 |
| Security | 15/15/10/0 → 15/15/10/0 | 8/9/1/0 → 8/9/1/0 |
| UI | 15/15/10/0 → 15/15/10/0 | 4/0/0/0 → 4/0/0/0 |
| Validator lead | 15/15/10/0 → 15/15/10/0 | 2/4/0/0 → 2/4/0/0 |

Open question (nonblocking, retained from QA): does Main's ignored direct-run artifact incident identify a Harness defect? The supplied QA note proves the failed and successful run identities, not that causal classification. No defect workaround enters Expertise. No content remediation, additional review or operator decision is inferred from the historical grading request or A-2 assurance limit.

```yaml
VERDICT: PASS
DIGEST:
  headline: Four members completed distillation; one validator repository rule sharpened,
    with all section counts unchanged.
  open_questions:
  - id: OQ-1
    question: Does Main's report that ignored direct-run digests caused repository-state
      failure identify a Harness defect? QA independently established only the failed
      superseded run and successful final pin; no force-tracking workaround was retained.
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2257-typescript-typecheck/.harness/harness/expertise/harness-validator-lead.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2257-typescript-typecheck/.harness/harness/features/FEAT-2257-typescript-typecheck/runs/distill-validator/state.yaml
  expertise_update:
  - persona: harness-validator-lead
    op: replace
    target: G-02
    section: Gotchas
    entry: "WHEN a gate relies on this repository's run digests DO establish that\
      \ required artifacts are tracked at the reviewed pin before crediting them as\
      \ durable evidence \u2014 `runs/**` is gitignored by default, so local presence\
      \ neither proves repository-state completeness nor survival after worktree removal."
    why: Main's feature-close observation reports missing ignored direct-run digests
      caused repository-state failure until tracked; QA c0 independently records the
      failed superseded run and green final pin. Existing G-02 overstates absence
      and survival as unconditional; replace with the weaker evidence-retention check,
      not a force-tracking workaround.
  team: distill
  steps_run: 4
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Rejected both relayed candidates as redundant or possible defect workaround;
      no operations.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Rejected grading-authorization candidate as existing skill guidance;
      no operations.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Rejected three independent candidates as established boundaries; no
      operations.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Rejected census/visual-assurance theme as existing Expertise; no operations.
    files_touched: []
  must_fix: []
  branch: feat/FEAT-2257-typescript-typecheck
  escalations: []
  adequacy_notes:
  - No diff review, grading, suites, builds, lint, formatters or renders executed
    during distillation.
  - 'Accepted relayed candidates: QA 0/2, code 0/1, security 0/0, UI 0/0. Independent
    candidates: security 0/3 and UI 0/1. Lead accepted 1/1 Main-sourced observation.'
  - 'All counts unchanged, ordered Patterns/Gotchas/Outcomes/Open: QA craft 15/15/10/1
    and repository 0/11/0/0; code 15/15/10/0 and 3/11/0/0; security 15/15/10/0 and
    8/9/1/0; UI 15/15/10/0 and 4/0/0/0; lead 15/15/10/0 and 2/4/0/0.'
  - Member counts are their no-op baseline reports; lead repository counts are tool-receipted
    before/after. Members made no Expertise applications.
  - Applied lead batch 633ea7df6ef1eea50f8ea6b054b5cb2d81f5fbdec02460213ebc66be00aa223d;
    receipt notes/expertise-receipt-0c2622b4cfd35185061668a20dfc6119b1162ad049a17ce00b40bc1b5dc29fd4.json.
  - PM goalcheck was skimmed; its distillation belongs to the product run and was
    not duplicated.
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2257-typescript-typecheck/.harness/harness/features/FEAT-2257-typescript-typecheck/runs/distill-validator/digest.md
```
