```yaml
VERDICT: PASS
DIGEST:
  headline: "Pinned c1 review clears MF-01 with a green non-vacuous matrix; F-02 remains a med advisory and no must-fix remains."
  team: review
  review_sha: df23bdaa7113700977ec43e617e293c854c0854e
  base_sha: 0fa8f336e55dc57bca09a9f7df0524a35195ee7e
  steps_run: 4
  cycles_used: 0
  severity_max: med
  members:
    - step: code
      persona: harness-code-reviewer
      verdict: PASS
      headline: "Spec compliance passed before code quality; MF-01 is closed and F-02 remains a med advisory."
      files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-c1.md]
    - step: qa
      persona: harness-qa
      verdict: PASS
      headline: "The exact T-01 command passed with 23 unit and 24 integration registrations executed at the review SHA."
      files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-qa-c1.md]
    - step: security
      persona: harness-security-reviewer
      verdict: PASS
      headline: "The changed subprocess, environment, filesystem, and config surfaces introduce no exploitable security regression."
      files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-security-reviewer-c1.md]
    - step: ui
      persona: harness-ui-reviewer
      verdict: PASS
      headline: "Scoped out after a pinned census found no rendered or interactive product surface."
      files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-ui-reviewer-c1.md]
  stage_order:
    spec_compliance: PASS
    code_quality_entered_after_spec_pass: true
    code_quality: PASS
    evidence: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-c1.md
  matrix_result:
    matrix_ok: true
    change_type: feature
    required_kinds: [unit, integration]
    eval: not_required
    prescribed_command: |-
      python3 .agents/skills/harness/bin/test-merge-gitignore.py &&
      .agents/skills/harness/bin/run-unit-tests.sh --kind all
    execution_context: "detached worktree at df23bdaa7113700977ec43e617e293c854c0854e"
    exit_code: 0
    duration_seconds: 155.16
    unit:
      configured_command: .agents/skills/harness/bin/run-unit-tests.sh --kind unit
      verdict: PASS
      discovery_count: 23
      execution: "executed through --kind all; all registrations passed"
    integration:
      configured_command: .agents/skills/harness/bin/run-unit-tests.sh --kind integration
      verdict: PASS
      discovery_count: 24
      execution: "executed through --kind all; all registrations passed"
      changed_test: "direct 7/7 PASS and registered PASS"
      repaired_probe: "test-bash-write-guard.py ONE IMPLEMENTATION retained and passed with (2, 2); 27/27 cases passed"
    registration_checks: "No MISCONFIGURED or KIND-DRIFT output; exact test path is registered in both integration registries and absent from UNIT_SCRIPTS."
    evidence: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-qa-c1.md
  findings:
    - id: F-01
      prior_id: MF-01
      reviewers: [harness-code-reviewer, harness-qa, harness-security-reviewer, harness-ui-reviewer]
      prior_severity: high
      failure_scenario: "An equal-size source mutation within one filesystem timestamp tick could reuse baseline bytecode, observe (0, 0) instead of the required (2, 2), and leave the mandatory integration matrix red."
      disposition: closed
      disposition_reason: "At the review pin both isolated hook children receive PYTHONDONTWRITEBYTECODE=1 while the retained assertion still requires (2, 2); QA then ran the exact matrix and observed the repaired 27/27 program pass. The change is test-only and does not alter either production guard."
      owning_lane: Engineering/harness-dev-ops
      evidence: ".agents/skills/harness/bin/test-bash-write-guard.py:469-506; .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-qa-c1.md"
    - id: F-02
      reviewers: [harness-code-reviewer, harness-qa]
      severity: med
      failure_scenario: "If --check emits a fabricated superset such as .claude/worktrees/NOT-THE-RULE, substring membership still accepts it as naming the missing canonical .claude/worktrees/ rule."
      disposition: advisory
      disposition_reason: "The weakness can mask a future diagnostic regression but is not a current production defect, required-matrix failure, or security boundary bypass; this repository's review gate is advisory below high."
      owning_lane: Engineering/harness-dev-ops
      recommended_action: "In a later approved change, compare the exact emitted bullet-rule set with the expected missing-rule set."
      evidence: ".agents/skills/harness/bin/test-merge-gitignore.py:69-73; .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-c1.md"
  new_findings: []
  dismissed_findings:
    - id: D-01
      reviewer: harness-security-reviewer
      disposition: dismissed
      reason: "The unchanged production utility's symlink handling and unquoted missing-rule report are pre-existing and not newly reachable through this test/config delta."
    - id: D-02
      reviewer: harness-ui-reviewer
      disposition: scoped_out
      reason: "The pinned 43-path census found zero rendered-UI paths and no production CLI interaction change; merge-gitignore.sh is byte-identical across the pins."
    - id: D-03
      reviewer: harness-qa
      disposition: not_applicable
      reason: "No AI behavior or interaction-flow predicate fires, so eval and UI/E2E kinds are not required by the feature matrix."
  must_fix: []
  adequacy_notes:
    - "The green matrix is non-vacuous: QA reported 23 unit and 24 integration registrations, the changed program passed directly and through the registry, and the runner emitted no configuration or kind-drift error."
    - "MF-01 closure has both mechanism inspection and fresh falsification evidence: the controlled ONE IMPLEMENTATION probe remained live and produced the required (2, 2) result."
    - "SC-01 through SC-05 have direct state/exit assertions; SC-06 was verified by pinned inspection. Only the complete-check path has reported controlled-mutant evidence, so the panel does not claim mutation-strength assurance for every behavioral case."
    - "The retained UI decline is evidence-based rather than predicted: it measured 43 changed paths, zero rendered-UI extensions, and an unchanged production utility."
  files_touched:
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-c1.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-qa-c1.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-security-reviewer-c1.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-ui-reviewer-c1.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-c1-validator/state.yaml
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-c1-validator/digest.md
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-c1-validator/digest.md
```

The c1 panel independently grades the immutable review SHA. The prior high-severity matrix failure is closed by the repaired live mutation probe and a fresh green required matrix; the only remaining item is the non-blocking F-02 diagnostic assertion advisory.
