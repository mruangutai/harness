```yaml
VERDICT: FAIL
DIGEST:
  headline: "Merge-gitignore coverage is spec-compliant and focused, but the mandatory integration matrix is red at the review pin."
  team: review
  review_sha: ce29a059e37af5133ae5b4f87df6f622ed966a92
  base_sha: 0fa8f336e55dc57bca09a9f7df0524a35195ee7e
  steps_run: 4
  cycles_used: 0
  severity_max: high
  members:
    - step: code
      persona: harness-code-reviewer
      verdict: PASS
      headline: "Spec compliance passed before code quality; one med diagnostic-assertion weakness is advisory."
      files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-c0.md]
    - step: qa
      persona: harness-qa
      verdict: FAIL
      headline: "The pinned feature matrix failed in integration because test-bash-write-guard.py failed 1 of 27 cases."
      files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-qa-c0.md]
    - step: security
      persona: harness-security-reviewer
      verdict: PASS
      headline: "The test-only subprocess and filesystem surface has no exploitable security regression."
      files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-security-reviewer-c0.md]
    - step: ui
      persona: harness-ui-reviewer
      verdict: PASS
      headline: "Scoped out after the changed-file census established that no built or user-facing UI changed."
      files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-ui-reviewer-c0.md]
  stage_order:
    spec_compliance: PASS
    code_quality_entered_after_spec_pass: true
    code_quality: PASS
    evidence: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-c0.md
  matrix_result:
    matrix_ok: false
    change_type: feature
    required_kinds: [unit, integration]
    eval: not_required
    prescribed_command: |-
      python3 .agents/skills/harness/bin/test-merge-gitignore.py &&
      .agents/skills/harness/bin/run-unit-tests.sh --kind all
    exit_code: 1
    unit:
      verdict: PASS
      discovery_count: 23
    integration:
      verdict: FAIL
      discovery_count: 24
      changed_test: "PASS: direct 7/7 and registered all-kinds execution"
      failing_test: .agents/skills/harness/bin/test-bash-write-guard.py
      observed: "26/27 worktree-boundary cases passed; ONE IMPLEMENTATION mutant observed bash=0 and write=0 instead of (2, 2)."
    evidence: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-qa-c0.md
  findings:
    - id: F-01
      reviewers: [harness-qa]
      severity: high
      failure_scenario: "A mandatory feature matrix rerun exits 1 because the ONE IMPLEMENTATION mutation proof in test-bash-write-guard.py leaves both guarded routes allowed (0) rather than refused (2), so required integration evidence is not green even though test-merge-gitignore.py itself passes."
      evidence: ".harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-qa-c0.md; runner aggregation at .agents/skills/harness/bin/run-unit-tests.sh:134-148"
      disposition: must_fix
      disposition_reason: "The repository policy requires unit and integration for feature changes, and review is advisory only below high; this observed high-severity matrix failure therefore blocks this pin."
      owning_lane: Engineering/harness-dev-ops
      exact_rerun: |-
        python3 .agents/skills/harness/bin/test-merge-gitignore.py &&
        .agents/skills/harness/bin/run-unit-tests.sh --kind all
    - id: F-02
      reviewers: [harness-code-reviewer]
      severity: med
      failure_scenario: "If --check prints a fabricated longer value such as .claude/worktrees/NOT-THE-RULE, the substring assertion accepts it as naming the canonical .claude/worktrees/ rule and the diagnostic regression can remain green."
      evidence: ".agents/skills/harness/bin/test-merge-gitignore.py:62-72 uses `rule in result.stderr`; production emits exact bullet lines at .agents/skills/harness/bin/merge-gitignore.sh:55-62."
      disposition: advisory
      disposition_reason: "This is a real resilience gap in a diagnostic assertion, not evidence of a current production defect or a failure of the approved user-visible behavior at the pin."
      owning_lane: Engineering/harness-dev-ops
      recommended_action: "Compare the exact emitted bullet-rule set with RULES[1:] in a later approved change."
  dismissed_findings:
    - id: D-01
      reviewer: harness-security-reviewer
      severity: info
      failure_scenario: "A project-supplied .gitignore symlink or shell-side rule reporting could retain pre-existing utility risk."
      disposition: dismissed
      reason: "The production utility is byte-identical across base and review pins, while the new test uses only temporary regular files and adds no production invocation path."
    - id: D-02
      reviewer: harness-ui-reviewer
      severity: info
      failure_scenario: "No UI failure scenario exists because the census found no rendered or interactive surface in the pinned diff."
      disposition: scoped_out
      reason: "Changed files are a standalone test, runner registration, and test-kind configuration; the unchanged utility also has no altered terminal interaction."
  must_fix:
    - id: MF-01
      finding: F-01
      owner: Engineering/harness-dev-ops
      action: "Resolve or establish the environmental cause of the test-bash-write-guard.py ONE IMPLEMENTATION failure, then rerun the exact T-01 command at the pinned candidate."
      rerun: |-
        python3 .agents/skills/harness/bin/test-merge-gitignore.py &&
        .agents/skills/harness/bin/run-unit-tests.sh --kind all
  adequacy_notes:
    - "The gate binds the changed test non-vacuously: it is in INTEGRATION_SCRIPTS, its exact path is in integration.detect, and it executed successfully both directly and inside the all-kinds run."
    - "Only the complete-check assertion has retained controlled-mutant evidence; the other behavioral cases have direct state/exit assertions but no reported mutation probes, so the panel cannot claim mutation-strength assurance for every case."
    - "The panel did not run a base-pin control for test-bash-write-guard.py, so it cannot distinguish a pre-existing or environment-sensitive failure from a regression introduced elsewhere; that uncertainty does not turn the required red review-pin gate green."
  files_touched:
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-c0.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-qa-c0.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-security-reviewer-c0.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-ui-reviewer-c0.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-validator/state.yaml
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-validator/digest.md
  branch: none
  open_questions: []
  escalations:
    - id: E-01
      raised_by: harness-validator-lead
      question: "The required integration matrix is red in test-bash-write-guard.py outside FEAT-36's declared changed-file set; engineering must remediate or diagnose it before the review pin can clear."
      domain: Engineering
      routed_to: harness-eng-lead
      resolution: pending
      decided_by: harness-validator-lead
      recorded_as: MF-01
  expertise_update: []
  sc_status: []
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-validator/digest.md
```

The panel's single blocking result is the mandatory integration matrix failure. The merge-gitignore behavioral test itself passed all seven cases and both registrations are bound; the separate diagnostic-substring weakness remains advisory.
