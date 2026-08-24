```yaml
VERDICT: PASS
DIGEST:
  headline: T-01 now has red-capable real-subprocess coverage for REQ-01..REQ-05; the untouched utility passed and remains byte-identical.
  team: build
  steps_run: 1
  cycles_used: 0
  members:
    - step: T-01
      persona: harness-dev-ops
      verdict: PASS
      headline: Seven named real-subprocess cases passed the untouched utility, the controlled mutant reddened the complete-check case, and both registries classify the suite as integration.
      files_touched: [.agents/skills/harness/bin/test-merge-gitignore.py, .agents/skills/harness/bin/run-unit-tests.sh, .harness/harness.json, .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-T-01-c0.md]
  assessment:
    production_changed: false
    utility_byte_evidence: "SHA-256 86cfff73c88a2baa1c74d2e516e3608e38954fef1c9e4ef344113b011e425c12 before and after"
    red: "MERGE_GITIGNORE_BIN controlled mutant: 6 passed, 1 failed; exit 1; check_complete_is_read_only failed"
    green: "untouched real utility: 7 passed, 0 failed; exit 0"
    verification: "python3 .agents/skills/harness/bin/test-merge-gitignore.py && .agents/skills/harness/bin/run-unit-tests.sh --kind all: exit 0 in 145.18s; test-merge-gitignore.py passed; no MISCONFIGURED or KIND-DRIFT output"
    classification: "INTEGRATION_SCRIPTS and test_kinds.integration.detect contain the exact path; UNIT_SCRIPTS does not"
    evidence: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-T-01-c0.md
  requirement_status:
    - { id: REQ-01, verdict: PASS, evidence: "preserves_existing_content" }
    - { id: REQ-02, verdict: PASS, evidence: "check_complete_is_read_only; check_incomplete_reports_missing_and_is_read_only" }
    - { id: REQ-03, verdict: PASS, evidence: "absent_target_receives_each_rule_once; partial_target_retains_present_rule_and_adds_missing_once" }
    - { id: REQ-04, verdict: PASS, evidence: "second_merge_is_byte_identical" }
    - { id: REQ-05, verdict: PASS, evidence: "explicit_project_root_ignores_caller_cwd" }
  must_fix: []
  files_touched:
    - .agents/skills/harness/bin/test-merge-gitignore.py
    - .agents/skills/harness/bin/run-unit-tests.sh
    - .harness/harness.json
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-T-01-c0.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/t01-eng/state.yaml
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/t01-eng/digest.md
  branch: feat/FEAT-36-merge-gitignore-coverage
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/t01-eng/digest.md
```

Lead assessment: the suite crosses the utility's public process seam rather than reaching into implementation details. Its seven independent cases pin preservation, both check-mode exits and read-only behavior, absent/partial merge behavior, byte idempotence, and explicit-root selection. The receipt records the required command/output/exit evidence; registry inspection confirms the test is integration-only in the executable runner. No send-back was warranted.
