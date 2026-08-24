```yaml
VERDICT: PASS
DIGEST:
  headline: T-01 satisfies the unit and integration matrix floor with seven red-capable behavioral cases and unchanged production.
  team: validator
  steps_run: 1
  cycles_used: 0
  members:
    - step: qa-T-01
      persona: harness-qa
      verdict: PASS
      headline: Both required kinds passed without misconfiguration or kind drift; controlled-mutant and untouched-production audits passed.
      files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/qa-T-01.md]
  must_fix: []
  severity_max: info
  adequacy_notes:
    - The unit command binds the changed runner/config registration through its pre-test union-drift and exact-kind cross-check; the seven user-visible behaviors are exercised by the integration kind.
    - No review panel or goal-check ran, as excluded by this validation segment.
  files_touched:
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/qa-T-01.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/qa-validator/state.yaml
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/qa-validator/digest.md
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/qa-validator/digest.md
```

QA evidence: `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/qa-T-01.md` records the pinned diff, matrix classification, exact per-kind commands, named-test evidence and counts, exit statuses, controlled-mutant red proof, and identical production tree objects.
