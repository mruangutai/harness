```yaml
VERDICT: FAIL
DIGEST:
  headline: "Overall FAIL: SC-05 lacks automated proof that only the explicit project's .gitignore changes; SC-01 through SC-04 and SC-06 are met."
  team: product
  steps_run: 1
  cycles_used: 0
  members:
    - step: goal-check
      persona: harness-pm
      verdict: FAIL
      headline: "SC-05 does not prove its quantified only-this-project clause; the other five criteria are met."
      files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/research-goal-check-product.md]
  overall: FAIL
  needs_approval: false
  uat_disposition: "None required because no criterion declares verify: uat."
  no_waivers: true
  t01:
    status: done
    verify_matches_exactly: true
    verify: |-
      python3 .agents/skills/harness/bin/test-merge-gitignore.py &&
      .agents/skills/harness/bin/run-unit-tests.sh --kind all
  must_fix:
    - "SC-05: add automated evidence that the explicit-root invocation changes only the requested project's .gitignore, not merely that it creates the requested target and leaves the caller without one."
  files_touched:
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/research-goal-check-product.md
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-product/state.yaml
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-product/digest.md
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status:
    - id: SC-01
      verdict: met
      method: automated
      evidence: "df23bdaa:.agents/skills/harness/bin/test-merge-gitignore.py:18-23,34-45; pinned run evidence at notes/review-harness-qa-c1.md:10-17"
    - id: SC-02
      verdict: met
      method: automated
      evidence: "df23bdaa:.agents/skills/harness/bin/test-merge-gitignore.py:48-72 checks both exit paths, every missing rule, and byte equality; pinned run evidence at notes/review-harness-qa-c1.md:10-17"
    - id: SC-03
      verdict: met
      method: automated
      evidence: "df23bdaa:.agents/skills/harness/bin/test-merge-gitignore.py:26-29,75-97 checks each canonical rule exactly once in absent and partial targets; pinned run evidence at notes/review-harness-qa-c1.md:10-17"
    - id: SC-04
      verdict: met
      method: automated
      evidence: "df23bdaa:.agents/skills/harness/bin/test-merge-gitignore.py:100-110 compares bytes after first and second merge; pinned run evidence at notes/review-harness-qa-c1.md:10-17"
    - id: SC-05
      verdict: not_met
      method: automated
      evidence: "df23bdaa:.agents/skills/harness/bin/test-merge-gitignore.py:113-123 proves the requested target exists and caller target is absent, but does not prove only the requested project's .gitignore changes; notes/review-harness-qa-c1.md:17,23 confirms only that narrower case ran"
    - id: SC-06
      verdict: met
      method: inspection
      evidence: "df23bdaa:.agents/skills/harness/bin/run-unit-tests.sh:17-18 and df23bdaa:.harness/harness.json:118-122 register the integration test; base and pin share merge-gitignore.sh blob 4610430764205c16a627edc9764a37dcb54af75c; notes/review-harness-code-reviewer-c1.md:19-25"
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-product/digest.md
```

The PM's pinned inspection is recorded at `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/research-goal-check-product.md`. The lead spot-check of the cited SC-05 case confirms its assertions are limited to the requested target's existence and the caller target's absence.