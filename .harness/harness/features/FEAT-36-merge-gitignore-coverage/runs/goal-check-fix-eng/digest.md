```yaml
VERDICT: PASS
DIGEST:
  headline: "SC-05 now has direct real-process proof that an explicit project root changes only the requested project's .gitignore and preserves a pre-existing caller file byte-for-byte."
  team: engineering
  steps_run: 1
  cycles_used: 0
  members:
    - { step: T-01-SC05, persona: harness-dev-ops, verdict: PASS, headline: "Strengthened the existing explicit-root case and captured an exit-0 run with all seven named cases passing.", files_touched: [.agents/skills/harness/bin/test-merge-gitignore.py, .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-goal-check-fix-eng.md] }
  must_fix: []
  verification:
    command: "python3 .agents/skills/harness/bin/test-merge-gitignore.py"
    exit_status: 0
    result: "7 passed; 0 failed"
    named_case: "PASS explicit_project_root_ignores_caller_cwd"
    evidence: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-goal-check-fix-eng.md
  assessment: "The outside-both-paths topology and existing requested-project assertion remain. The case now seeds caller/.gitignore with distinctive bytes, snapshots them before the subprocess, and compares the post-run bytes; the weaker absence assertion alone was replaced. No production utility or registry change was made in this run."
  files_touched: [.agents/skills/harness/bin/test-merge-gitignore.py, .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-goal-check-fix-eng.md, .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-fix-eng/state.yaml, .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-fix-eng/digest.md]
  branch: FEAT-36-merge-gitignore-coverage
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-fix-eng/digest.md
```

The dev-ops receipt preserves the exact standalone invocation, all seven named PASS lines, the 7/0 summary, and exit status 0. The prohibited all-kinds and project-wide suites were not run in this engineering fix step.
