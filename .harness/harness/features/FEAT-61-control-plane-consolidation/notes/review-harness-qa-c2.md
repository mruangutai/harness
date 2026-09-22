```yaml
VERDICT: FAIL
DIGEST:
  headline: All five signed clauses pass at f3825ca1, but T-01/T-02/T-03 use an unmapped `code` change_type, so the required-kind matrix cannot gate them and gh-sync would refuse them.
  suite: pass
  failures: 1
  matrix_ok: false
  kinds:
    - { kind: unit, state: satisfied, cmd: "T-01/T-02/T-04 signed clauses", named_tests: 6 }
    - { kind: integration, state: satisfied, cmd: "T-02/T-03/T-04/T-05 signed clauses", named_tests: 13 }
  coverage_gaps:
    - "QA-C2-01 (high/form, T-01/T-02/T-03): `code` is absent from test_matrix and gh_issue_types; `gh-sync open` would raise UnknownWorkNature. Evidence: plan.yaml:157,184,214; .harness/harness.json:157-240; .claude/skills/harness/bin/gh_issue_types.py:13-26,49-53. Use a signed supported type or add signed mappings."
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-check-plan-routes.py:2403-2421" }
    - { id: SC-02, test: "tests/unit/test-factory-config.py:547-608" }
    - { id: SC-03, test: "tests/integration/test-plan-merge.py:3342-3389" }
    - { id: SC-04, test: "tests/unit/test-gate-policy.py:62-92" }
    - { id: SC-05, test: "tests/integration/test-check-domain-worktree.py:754-802; tests/integration/test-bash-write-guard.py:1039-1096" }
    - { id: SC-06, test: "tests/unit/test-artifact-accessors.py:158-210; tests/integration/test-check-state-feat59.py:540-544" }
    - { id: SC-07, test: "tests/integration/test-check-plan-routes.py:2477-2510" }
  fail_first:
    - { sc: SC-01, evidence: "notes/fail-first-receipts.md:120-141" }
    - { sc: SC-02, evidence: "notes/fail-first-receipts.md:5-20" }
    - { sc: SC-03, evidence: "notes/fail-first-receipts.md:61-78" }
    - { sc: SC-04, evidence: "notes/fail-first-receipts.md:80-97" }
    - { sc: SC-05, evidence: "notes/fail-first-receipts.md:99-118" }
    - { sc: SC-06, evidence: "notes/fail-first-receipts.md:22-60" }
    - { sc: SC-07, evidence: "notes/fail-first-receipts.md:120-141" }
  open_questions: []
  files_touched: [".harness/harness/features/FEAT-61-control-plane-consolidation/notes/review-harness-qa-c2.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-61-control-plane-consolidation/.harness/harness/features/FEAT-61-control-plane-consolidation/notes/review-harness-qa-c2.md
```