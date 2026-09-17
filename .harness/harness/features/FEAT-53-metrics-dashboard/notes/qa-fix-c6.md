# QA gate — FEAT-53 fix c6 final

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: "Scoped c6 proofs pass, but the QA digest gate independently requires a broad runner that the dispatch expressly forbids."
  suite: n/a
  failures: 0
  matrix_ok: n/a
  kinds:
    - kind: integration
      state: satisfied
      cmd: "python3 .claude/skills/harness/bin/run-unit-tests.py --check-layout && python3 tests/integration/test-metrics-trend.py; npm test -- src/kpi-content.test.tsx"
      named_tests: 18
  coverage_gaps: []
  sc_evidence:
    - id: SC-19
      test: "tests/integration/test-metrics-trend.py:103-132"
    - id: SC-20
      test: ".claude/skills/harness/bin/dashboard/client/src/kpi-content.test.tsx:15-26"
  fail_first:
    - sc: SC-19
      evidence: "notes/qa-fix-c6.md (pre-overwrite artifact, lines 18): removal of weekly.sourcing_rule from all three payload states produced KeyError at test-metrics-trend.py:130; trend.py is byte-identical from e40dfd38 to 93785232 (SHA-256 58a7e1f3e7c4085f44bbdca4ce33f29fcefda4763a8c38cc74bc7c629008d265)."
    - sc: SC-20
      evidence: "notes/receipt-harness-backend-dev-fix-c6.md:8-24: replacing weekly.sourcing_rule with a hard-coded fallback made the sentinel assertion fail; restored tiles.tsx SHA-256 is a54245e3c1a71d64f881c38fa2ef8b2cc7de87e5496e1b382be6e778af7c8663."
  open_questions:
    - id: Q1
      question: "The digest validator independently runs broad run-unit-tests.py and refuses PASS when it exits 1, while this dispatch prohibits broad suites and excludes the ambient T-12 failure. Resolve this gate conflict before a PASS can be accepted."
      blocking: true
  files_touched:
    - ".harness/harness/features/FEAT-53-metrics-dashboard/notes/qa-fix-c6.md"
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/qa-fix-c6.md
```

## Phase 1 coverage expectation

The scoped repair requires an exact weekly sourcing-rule field for populated, no-record, and missing-log weekly payloads; counts must still include a nullable `pr`; and KPI 7 must disclose the supplied (not hard-coded) payload rule after its accessible control opens. All are covered. No unrelated T-12 performance check was run.

## Final evidence

- T-10 exact verification passed: layout check plus `tests/integration/test-metrics-trend.py` (17 tests).
- The sole client command passed: `npm test -- src/kpi-content.test.tsx` (1 test).
- The backend field-removal mutant had already reddened the dedicated assertion; the proof subject is unchanged at the final tip.
- The client hard-coded-fallback mutant reddened the sentinel assertion; the restored production source hash matches the recorded proof hash.
