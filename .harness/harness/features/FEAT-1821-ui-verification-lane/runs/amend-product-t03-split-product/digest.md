```yaml
VERDICT: BLOCKED
DIGEST:
  headline: "The T-03 residual split cannot land under the mandated writer while approval must remain unchanged: adding T-08..T-13 necessarily resets the approved plan, so no plan or ledger mutation was made."
  team: amendment
  steps_run: 1
  cycles_used: 0
  members:
    - step: amendment
      persona: harness-pm
      verdict: BLOCKED
      headline: "The required apply verb has no operator-exception path and automatically resets approved plans when tasks are added."
      files_touched:
        - .harness/harness/features/FEAT-1821-ui-verification-lane/notes/research-amend-product-t03-split.md
  must_fix:
    - "Provide a governed plan-merge path that can add the operator-approved T-08..T-13 task set without resetting approval, or explicitly permit the normal reset and main-session reapproval path."
  files_touched:
    - .harness/harness/features/FEAT-1821-ui-verification-lane/notes/research-amend-product-t03-split.md
  branch: none
  open_questions:
    - id: Q1
      question: "Will the control-plane owner provide an operator-authorized apply path that adds tasks without resetting approval, or revise the ruling to permit reset and reapproval?"
      blocking: true
  escalations: []
  expertise_update: []
  adequacy_notes:
    - "Lead assessment confirmed the tool path: apply records added task ids as changed tasks, then _maybe_reset_approval rewrites approved to pending and feature status to plan; there is no dry-run or exception flag."
    - "The plan still has approved approval, T-08..T-13 remain absent, T-03 is unchanged, and feature.json has no amendment judgement for this run."
    - "The scoped pre-mutation plan check resolved 20 anchors but retained one pre-existing T-05 missing-anchor failure; it is outside this amendment and was not changed."
  needs_approval: false
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/amend-product-t03-split-product/digest.md
```
