# BUG-2171 T-01 budget trim — PASS

T-01 machine-field count is **75 → 25** (budget 50); the feature-scoped check-plan-routes.py changed from one violation/exit 1 to zero violations/exit 0. PM amended verify and intent through plan-merge verbs only.

PM preserved every non-heredoc verify byte, including full live smoke; the three heredocs now reference the existing main-owned helper steps. Only settled-cause justification moved to the research note. All normative intent, BRIEF, SCs, helper and product source/tests/config stayed unchanged. The helper is a read dependency, not an implementation target, so files stayed unchanged.

Evidence: notes/research-BUG-2171-task-structured-budget-trim.md, sections Meaning preservation and Commands and receipts. Its structural comparison covers all loaded plan fields except the two intended replacements; PM also records live-smoke and final-verify hashes. Lead assessed that receipt; no implementation checks were repeated.

Member: harness-pm / trim / PASS. Files: plan.yaml, notes/research-BUG-2171-task-structured-budget-trim.md, feature.json (automatic plan-merge side effect); scratch /tmp/bug2171-verify.txt.

Approval remains pending and requires main-session re-signature; existing stale review_sha must be refreshed through normal review provenance flow. This is not implementation verification or shipment approval. No prototype gate applies: no user-facing interaction changed. Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: T-01 trimmed from 75 to 25 machine-field lines; check-plan-routes reports
    zero violations, meaning preserved.
  open_questions: []
  files_touched:
  - .harness/harness/features/BUG-2171-task-structured/plan.yaml
  - .harness/harness/features/BUG-2171-task-structured/feature.json
  - .harness/harness/features/BUG-2171-task-structured/notes/research-BUG-2171-task-structured-budget-trim.md
  - /tmp/bug2171-verify.txt
  expertise_update: []
  team: patch
  steps_run: 1
  cycles_used: 0
  members:
  - step: trim
    persona: harness-pm
    verdict: PASS
    headline: "75 \u2192 25 machine lines; zero route violations; normative requirements\
      \ and non-heredoc verify bytes preserved."
    files_touched:
    - .harness/harness/features/BUG-2171-task-structured/plan.yaml
    - .harness/harness/features/BUG-2171-task-structured/feature.json
    - .harness/harness/features/BUG-2171-task-structured/notes/research-BUG-2171-task-structured-budget-trim.md
    - /tmp/bug2171-verify.txt
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'PM ran feature-scoped route checker: before exit 1 with 75 machine lines and
    one violation; after exit 0 with zero violations. Same checker counting function
    measured 25 final machine lines.'
  - All non-heredoc verify bytes, including live smoke, preserved; existing main-owned
    helper unchanged and treated as read dependency, so files unchanged.
  - Approval remains pending; main must refresh stale review provenance and obtain
    re-signature. No commits or implementation verification performed.
  - feature.json changed automatically through plan-merge; no manual source, tests,
    config, BRIEF or SC edits.
  - 'No prototype required: form-only contract maintenance introduces no user interaction.'
  sc_status: []
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/runs/2026-11-21-06-patch-product/digest.md
```
