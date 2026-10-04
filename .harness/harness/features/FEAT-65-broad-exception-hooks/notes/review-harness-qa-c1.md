VERDICT: FAIL
DIGEST:
  headline: Matrix is green at 7596434, but SC-01 lacks retained fail-first evidence using the review-pin test files.
  suite: pass
  failures: 0
  matrix_ok: false
  kinds:
    - kind: unit
      state: satisfied
      cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit"
      named_tests: 42
      discovered_files: 42
      exit: 0
    - kind: integration
      state: satisfied
      cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration"
      named_tests: 69
      discovered_files: 69
      exit: 0
  coverage_gaps:
    - "SC-01: notes/byte-evidence-vs-baseline.md retains comparisons made with older heads, not the test files committed at review SHA 7596434."
  sc_evidence:
    - { id: SC-01, test: "notes/byte-evidence-vs-baseline.md:5" }
    - { id: SC-02, test: "tests/integration/test-check-domain.py:50" }
    - { id: SC-03, test: "tests/unit/test-harness-boundary.py:1017" }
    - { id: SC-04, test: "tests/unit/test-broad-catch-census.py:127" }
    - { id: SC-05, test: "tests/unit/test-broad-catch-census.py:161" }
    - { id: SC-09, test: "tests/unit/test-feature-record.py:938" }
    - { id: SC-10, test: "tests/integration/test-inflight-registry.py:1262" }
  fail_first:
    - { sc: SC-01, evidence: "FAIL: notes/byte-evidence-vs-baseline.md:5,91,129 name dd1203a35/e10c56de/ec0996cb rather than 7596434; its check-domain/worktree/post test files differ at the review pin." }
    - { sc: SC-02, evidence: "PASS: notes/red-first-receipts.md:11-25,37-50,52-84; baseline exit 1, pin exit 0, verbatim discriminating failures; all indexed receipt test files are byte-identical from a17269db to 7596434." }
    - { sc: SC-03, evidence: "PASS: notes/red-first-receipts.md:11-25,137-145,186-203; baseline exit 1, pin exit 0; indexed receipt test files match 7596434." }
    - { sc: SC-04, evidence: "PASS: notes/red-first-receipts.md:148-184,196-203; test-broad-catch-census.py byte-identical from a17269db to 7596434." }
    - { sc: SC-05, evidence: "PASS: notes/red-first-receipts.md:86-96,148-184; test-branch-create-gate.py and test-broad-catch-census.py byte-identical from a17269db to 7596434." }
    - { sc: SC-09, evidence: "PASS: notes/red-first-receipts.md:128-135; tests/unit/test-feature-record.py byte-identical from a17269db to 7596434." }
    - { sc: SC-10, evidence: "PASS: notes/red-first-receipts.md:137-145; tests/integration/test-inflight-registry.py byte-identical from a17269db to 7596434." }
  c0_dispositions:
    - id: QA-65-01
      disposition: fail
      detail: "Closed for SC-02/03/04/05/09/10 only; SC-01 still does not bind RED and GREEN to the review-pin test files."
    - id: CR-01
      disposition: pass
      detail: "branch-create-gate.py:85-91 catches only (OSError, ValueError, AttributeError); test-branch-create-gate.py:245-274 proves expected recovery and AttributeError loudness; test-broad-catch-census.py:53-66 and check-plan-routes.py:2216-2235 bind executable string programs into the census. Independent AST probe measured baseline=5, pin=0; integration matrix ran this case green (14/14)."
  findings:
    - id: QA-65-01
      reader: qa
      sc: SC-01
      location: "notes/byte-evidence-vs-baseline.md:5,91,129"
      scenario: "A regression or assertion change in the review-pin check-domain/worktree/post suites can ship while this receipt remains green, because its retained baseline comparison used older test-file versions rather than the tests committed at 7596434."
      satisfies: "Copy each 7596434 test file into the baseline production tree, run it there and at 7596434 with the recorded command, and retain verbatim RED plus GREEN output/digests."
      kind: substance
      severity: high
      owned_plan_tasks: [T-01, T-02, T-03, T-04]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-65-broad-exception-hooks/.harness/harness/features/FEAT-65-broad-exception-hooks/notes/review-harness-qa-c1.md
