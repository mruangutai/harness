# QA gate — BUG-285 canonical reader

```yaml
reviewed:
  base_sha: 8e3bda037bf62e89966d898ccfdf8c9cabcdcdea
  review_sha: da8932a065137bcfbdb85fc2489b5bdd01936a6f
  basis: plan.yaml:39 authoritative planning base
VERDICT: FAIL
DIGEST:
  headline: Final targeted gates are green and the permanent audit reports zero unresolved readers, but required fail-first evidence is missing and SC-07 omits its required comment-bearing issue-285 fixture.
  suite: pass
  failures: 3
  matrix_ok: false
  change_types:
    - { tasks: [T-02, T-03, T-04], type: cross_module, required: [unit, integration] }
    - { tasks: [T-01, T-05, T-06, T-07, T-09], type: bugfix, required: [unit] }
    - { tasks: [T-08], type: docs, required: [] }
  detected_changed_units: { paths: 142, test_paths: 47, source_and_enforcement: artifact_accessors-and-reader-callers }
  kinds:
    - { kind: unit, state: satisfied, cmd: "targeted T-02/T-03/T-04/T-07 verify commands", named_tests: 19 }
    - { kind: integration, state: satisfied, cmd: "targeted T-01/T-02/T-03/T-04/T-07 verify commands", named_tests: 27 }
  exact_targeted_gates:
    - { task: T-01, cmd: "python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test", outcome: pass }
    - { task: T-02, cmd: "plan.yaml T-02 verify", outcome: pass }
    - { task: T-03, cmd: "plan.yaml T-03 verify", outcome: pass }
    - { task: T-04, cmd: "plan.yaml T-04 verify", outcome: pass }
    - { task: T-07, cmd: "plan.yaml T-07 verify", outcome: pass }
    - { task: T-08, cmd: "python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md", outcome: pass }
    - { task: T-09, cmd: "test ! -e .claude/skills/harness/bin/sh-to-py-differential.py", outcome: pass }
    - { task: [T-05, T-06], cmd: "historical --verify-enforcement-bytes commands", outcome: not-rerunnable-after-required-T-07-retirement }
  discovery:
    permanent_ast_audit: { outcome: pass, unresolved: 0, scanned_python_files: 69 }
    enforcement_baseline: { outcome: retired, baseline_file_absent: true, temporary_mode_absent: true }
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-check-plan-routes.py:1928-2325" }
    - { id: SC-02, test: "tests/unit/test-artifact-accessors.py:29-153" }
    - { id: SC-03, test: "tests/unit/test-feature-json-reader.py:97-184; tests/integration/test-gh-sync-open.py (BUG-285 consumer assertions)" }
    - { id: SC-04, test: "tests/integration/test-check-plan-routes.py:2082-2117,2272-2289" }
    - { id: SC-05, test: "tests/integration/test-check-plan-routes.py:2082-2117" }
    - { id: SC-07, test: "tests/unit/test-feature-json-reader.py:125-132,153-184; tests/integration/test-gh-sync-open.py and test-factory-decompose.py BUG-285 consumer assertions" }
  fail_first:
    - { sc: SC-01, evidence: "MISSING: no receipt/path records this SC's assertion failing before the audit implementation." }
    - { sc: SC-02, evidence: "notes/receipt-harness-backend-dev-T-02-c0.md:8" }
    - { sc: SC-03, evidence: "notes/receipt-harness-backend-dev-T-02-c0.md:9-11" }
    - { sc: SC-04, evidence: "MISSING: no receipt/path records the canonical-cutover assertion failing before implementation." }
    - { sc: SC-05, evidence: "MISSING: no receipt/path records the enforcement-equivalence assertion failing before implementation." }
    - { sc: SC-07, evidence: "notes/receipt-harness-backend-dev-T-02-c0.md:9-11" }
  coverage_gaps:
    - "SC-07's required comment-bearing JSON/YAML divergence fixture is absent; the only YAML-only fixture has no comment."
    - "SC-01, SC-04, and SC-05 have no genuine fail-first receipt despite final green tests."
  findings:
    - { id: QA-01, kind: substance, severity: high, task: T-02, owner: harness-backend-dev/team, path: "tests/unit/test-feature-json-reader.py:125-132", scenario: "A permissive-YAML-only document without a comment is refused, but removing the issue-285 comment-bearing fixture lets the literal SC-07 requirement ship untested.", remedy: "Restore/extend central coverage with the comment-bearing document that permissive YAML accepts and strict JSON rejects; capture its red run before implementation." }
    - { id: QA-02, kind: substance, severity: high, task: T-01, owner: main-session-direct, path: "tests/integration/test-check-plan-routes.py:1928-2325", scenario: "The final audit is green, but no durable red run shows its live-inventory assertion detected the pre-cutover unresolved reader inventory.", remedy: "Record a genuine pre-fix or isolated historical red run for SC-01's named assertion." }
    - { id: QA-03, kind: substance, severity: high, task: T-05/T-06, owner: main-session-direct, path: "tests/integration/test-check-plan-routes.py; notes/", scenario: "Final retirement proves the temporary baseline/mode are absent, but no durable red run binds the pre/post enforcement-equivalence assertion required by SC-05; SC-04 likewise lacks a recorded red cutover proof.", remedy: "Add durable fail-first receipts for SC-04 and SC-05's consumer-observable assertions without restoring the retired baseline interface." }
  open_questions: []
  files_touched: [".harness/harness/features/BUG-285-canonical-reader/notes/review-harness-qa-c0.md"]
  expertise_update: []
```

Final T-07 command passed all named scoped scripts. Its permanent audit printed `0 unresolved reader site(s) across 69 Python file(s)`; the command also confirmed the temporary baseline file and `--verify-enforcement-bytes` mode are absent. T-05/T-06 historical exact commands are intentionally no longer runnable because that required final cutover removed their temporary file/mode.
