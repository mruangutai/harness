# QA matrix gate — BUG-1725 T-01

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The pinned gate cannot pass: unit failed, SC-02 lacks fail-first evidence, and the two required pinned inspection paths do not exist."
  suite: fail
  failures: 3
  matrix_ok: false
  review_range: "c280792f2719145a1a41fb3df12075fdb3eebd40..b317f9a54f7f5f6570e0d36b1a46601357a02ec9"
  discovery:
    changed_files: 2
    changed_paths:
      - .claude/skills/harness/bin/plan-merge.py
      - tests/integration/test-plan-merge.py
    changed_integration_test_lines: 56
  kinds:
    - kind: unit
      required_by: "bugfix + touches_runtime_code"
      state: failed
      cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit"
      named_tests: 0
      evidence: "artifact://372:201-206 — test-check-state-inv35.py has one named assertion failure"
    - kind: integration
      required_by: "SC-01/SC-02 require integration coverage; the changed test is under tests/integration/**"
      state: satisfied
      cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration"
      named_tests: 1
      evidence: "artifact://409:314-317,811-814 — test-plan-merge.py exit 0; pinned test is tests/integration/test-plan-merge.py:2954-3005"
  task_verify:
    state: satisfied
    cmd: "python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1725-task-file-overlap/.harness/harness/features/BUG-1725-task-file-overlap/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1725-task-file-overlap"
    evidence: "exit 0: OK T-01 4 anchor(s) resolved; 0 failure(s)"
  sc_evidence:
    - id: SC-01
      test: "tests/integration/test-plan-merge.py:2975-3005 (case at :2954)"
      result: "pinned green"
    - id: SC-02
      test: "tests/integration/test-plan-merge.py:2973-2974"
      result: "pinned green, but pre-fix assertion was already green"
  fail_first:
    - sc: SC-01
      evidence: "This artifact, Pre-fix replay below: checker from c280792f... with pinned test red on the three OVERLAP assertions; pinned runner green at artifact://409:314-317,811-814."
    - sc: SC-02
      evidence: "missing — pre-fix replay reports PASS 'an otherwise valid plan with shared files still exits 0 (SC-02)', so the exit-code assertion did not fail before the fix."
  coverage_gaps:
    - "SC-02 has no fail-first red: the asserted advisory exit code was already correct at c280792f."
    - "SC-03 inspection cannot be satisfied: git show b317f9a...:.agents/skills/harness-spec-driven/SKILL.md exits 128 because the path is absent."
    - "SC-04 inspection cannot be satisfied: git show b317f9a...:.agents/skills/harness/teams/plan.yaml exits 128 because the path is absent."
  findings:
    - id: F-01
      kind: substance
      severity: high
      summary: "SC-02's required fail-first proof is absent."
      evidence: "Pre-fix replay below shows its only exit-0 assertion passed before the overlap implementation existed."
    - id: F-02
      kind: substance
      severity: high
      summary: "Required unit matrix command fails on a named assertion."
      evidence: "artifact://372:201-206."
    - id: F-03
      kind: substance
      severity: high
      summary: "SC-03 and SC-04 cannot be inspected at the required immutable paths."
      evidence: "Exact git-show invocations below both exit 128: path exists on disk but not at b317f9a."
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1725-task-file-overlap/notes/review-harness-qa-c1.md
  expertise_update: []
```

## Pre-fix replay

Executed the pinned integration test against `.claude/skills/harness/bin/plan-merge.py` from isolated worktree `c280792f2719145a1a41fb3df12075fdb3eebd40`, via `PLAN_MERGE_BIN`. It exited 1. SC-01's three overlap-content assertions and the overlap-with-existing-failure assertion were red because the old checker emitted no `OVERLAP` lines. The same replay reports `PASS  check: an otherwise valid plan with shared files still exits 0 (SC-02)`: the SC-02 assertion does not discriminate the pre-fix state.

## Pinned inspection receipts

- `git diff --name-status c280792f2719145a1a41fb3df12075fdb3eebd40 b317f9a54f7f5f6570e0d36b1a46601357a02ec9` reports exactly two changed files, both listed above.
- `git show b317f9a54f7f5f6570e0d36b1a46601357a02ec9:.agents/skills/harness-spec-driven/SKILL.md` exits 128: path exists on disk but not at the pinned commit.
- `git show b317f9a54f7f5f6570e0d36b1a46601357a02ec9:.agents/skills/harness/teams/plan.yaml` exits 128: path exists on disk but not at the pinned commit.
