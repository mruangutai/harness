```yaml
VERDICT: PASS
DIGEST:
  headline: "B-1 QA gate passed: exact-set red proof discriminates, all 46 configured scripts pass, and protected production bytes remain unchanged."
  team: validator
  steps_run: 1
  cycles_used: 0
  members:
    - { step: T-01-qa-gate, persona: harness-qa, verdict: PASS, headline: "Exact stderr bullet-set regression is discriminating and all required configured gates are green.", files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/qa-fix-b1.md] }
  severity_max: info
  adequacy_notes: []
  must_fix: []
  matrix_kinds:
    - { kind: unit, state: satisfied, command: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 23, failed: 0 }
    - { kind: integration, state: satisfied, command: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 23, failed: 0 }
  direct_regression: { command: "python3 .agents/skills/harness/bin/test-merge-gitignore.py", named_tests: 7, failed: 0 }
  all_kinds: { command: ".agents/skills/harness/bin/run-unit-tests.sh --kind all", named_tests: 46, failed: 0 }
  mutant_red: { command: "MERGE_GITIGNORE_BIN=/tmp/fix-b1-qa.etQRim/bin/merge-gitignore.sh python3 .agents/skills/harness/bin/test-merge-gitignore.py", passed: 6, failed: 1, sole_failure: check_incomplete_reports_missing_and_is_read_only, unexpected_rule: .claude/worktrees/NOT-THE-RULE }
  runner_disposition: "No MISCONFIGURED, KIND-DRIFT, no-tests, load, import, collection, or syntax condition occurred."
  production_script_sha256: 86cfff73c88a2baa1c74d2e516e3608e38954fef1c9e4ef344113b011e425c12
  production_script_disposition: "Matches engineering pre/post evidence and has no worktree diff; byte-identical and unmodified."
  files_touched:
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/qa-fix-b1.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/fix-b1-qa-validator/state.yaml
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/fix-b1-qa-validator/digest.md
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status:
    - { id: SC-02, verdict: PASS, method: "direct/configured green plus independently reproduced controlled-mutant red", evidence: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/qa-fix-b1.md }
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/fix-b1-qa-validator/digest.md
```

QA classified the B-1 diff as requiring the feature floor of unit and integration. Both kinds ran non-zero registered suites and satisfied the gate. The literal plan verification also passed: the direct regression reported 7/7, followed by the all-kinds runner at 46/46. The independent temporary mutant caused only the strengthened exact-set assertion to fail, with the fabricated rule reported as unexpected; the real utility stayed green and retained the engineering SHA-256.
