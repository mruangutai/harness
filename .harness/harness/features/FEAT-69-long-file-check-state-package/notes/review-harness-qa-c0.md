# QA gate — FEAT-69 c0

```yaml
VERDICT: FAIL
DIGEST:
  headline: Matrix is green and non-vacuous, but SC-02 byte identity and SC-03 fail-first evidence are unmet.
  reviewed_sha: db488aa7c78e392c788bd5839a43ebf4ba562ea1
  suite: pass
  failures: 2
  matrix_ok: true
  required_kinds: [unit, integration]
  kinds:
    - kind: unit
      state: satisfied
      cmd: python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit
      discovered: 43
      executed: 43
      exit_status: 0
      non_vacuous: true
    - kind: integration
      state: satisfied
      cmd: python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration
      discovered: 71
      executed: 71
      exit_status: 0
      non_vacuous: true
  sc_evidence:
    - id: SC-01
      test: notes/clean-pin-byte-receipts.generated.md:45-66
    - id: SC-02
      test: notes/clean-pin-byte-receipts.generated.md:14-43
    - id: SC-03
      test: tests/integration/test-check-plan-routes.py:2834-2949
    - id: SC-04
      test: notes/clean-pin-byte-receipts.md:5-31
  fail_first:
    - sc: SC-01
      evidence: notes/red-first-receipts.md:5-24 (baseline grade assertion exit 1; pin exit 0)
    - sc: SC-02
      evidence: notes/red-first-receipts.md:26-28; approved baseline-versus-pin comparison equivalent
    - sc: SC-03
      evidence: missing — committed notes/red-first-receipts.md:1-28 records SC-01 and SC-02 only; no retained pre-fix failing run for the structural package case
  coverage_gaps:
    - SC-03 has current mutation coverage but no committed accepted fail-first receipt.
  findings:
    - id: QA-01
      kind: substance
      severity: high
      reader: harness-qa
      owner: T-04
      path: notes/clean-pin-byte-receipts.generated.md:18,34-43
      summary: SC-02 normalized byte identity fails for full_table.
      scenario: Clean detached baseline and pin measurements both exit 1, but pin stdout adds five non-root lines after the sole permitted root replacement; the contract requires exact normalized exit/stdout/stderr identity for every measurement.
      expected: "All identical (normalised): yes (13/13)" with no exact-difference block.
      observed: "All identical (normalised): NO (12/13)" and five pin-only lines at lines 38-42.
    - id: QA-02
      kind: substance
      severity: high
      reader: harness-qa
      owner: T-04
      path: notes/red-first-receipts.md:1-28
      summary: SC-03 has no committed fail-first evidence.
      scenario: A later regression could leave the current mutation suite green or change its mutant assertions without any retained pre-fix failing run proving the SC-03 structural cases discriminated before implementation.
      expected: A committed receipt naming SC-03, its structural test, and that test's pre-fix nonzero failing result.
      observed: The only committed red-first receipt is explicitly scoped to "SC-01, SC-02 fail-first" and contains no SC-03 run.
  severity_max: high
  must_fix: [QA-01, QA-02]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-69-long-file-check-state-package/.harness/harness/features/FEAT-69-long-file-check-state-package/notes/review-harness-qa-c0.md
```

## Principles applied
- Build the Lever: used the configured per-kind runners and committed receipt scripts rather than hand-counting test coverage.
