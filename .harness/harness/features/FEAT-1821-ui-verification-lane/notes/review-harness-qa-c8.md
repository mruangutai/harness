# QA revalidation — T-01 c8

**BLUF: FAIL at `0163657540ab3ad3be4ff5aa34f838dc4f1e17d8`.** V7-01 closes: c8 removes the false title refusal without weakening no-bundle failure. V7-02 remains open because the receipt assigns SC-02/03/04 elsewhere but supplies no pinned SC-04 failing test or executable pre-fix failure.

## Scope and matrix

Phase 1 (BRIEF/plan only): T-01 is `logic`, so the matrix requires `unit`; its SC-05/06/10/11 contract needs parser, identity/accounting/evidence, runner/no-bundle, and complete-client-title refusal coverage. It does not own the browser-runner outcomes SC-02/03/04. The c8 delta from `b8f96ab8e9c8168ed8389ccf4732a958e84828fd` changes only `ui_contract.py` and its focused unit test, plus excluded governance records. `unit` is satisfied. The global automated-SC fail-first floor remains unmet for SC-04.

## V7-01 real regression

Command (at the review pin):

```sh
python3 .claude/skills/harness/bin/ui_contract.py gate --design .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --results .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/results.json --feature FEAT-53-metrics-dashboard --run-id FEAT-1821-initial-red --served-bundle-commit 153909c71e8ca3f02be6fcbcfe48781718953b1d --repo-root . --client-package .claude/skills/harness/bin/dashboard/client --changed .claude/skills/harness/bin/dashboard/client/src/tiles.tsx
```

Exit `1` is the intended FEAT-53 RED, not a T-01 failure: 18 product predicate failures and four inspection-setup refusals. Manifest-title absences: **0**. Non-RED structural/contract reasons: **0**. The four preserved setup outcomes are `VIS-DENSITY` and `VIS-PROTOTYPE` at both desktop projects; all remain explicitly refused as non-evidence. The 18 product failures remain honest committed-bundle outcomes.

## V7-02 static and complexity checks

- `python3 tests/unit/test-ui-verification-contract.py` → exit `0`; **24/24** passed.
- Deliberately unavailable results bundle with the same client change → exit `1`, `no results.json ...`; the gate fails closed before any success path.
- `python3 .claude/skills/harness/bin/code-grade.py --base b8f96ab8e9c8168ed8389ccf4732a958e84828fd --head 0163657540ab3ad3be4ff5aa34f838dc4f1e17d8 --json` → 3 changed records, 3 passing; the in-scope production function `_executed_titles` is grade 5 (bar 4).
- Full in-scope module check: `python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/ui_contract.py --json` → 38/38 passing, no ungraded; all grades are 4 or 5. This includes changed caller `_client_change_reasons` (grade 4) and `gate` (grade 4).

## Fail-first receipt audit

The receipt is honest for T-01's own SC-05/06/10/11 claims. Direct historical-tree cross-check found both module and test absent at `624eb59a^`; the current suite therefore imports no `ui_contract`. At pre-c7 `9adb6c58`, the source lacks predicate/inspection preflight and treats only literal titles as present, so current cases `test_gate_enforces_predicates_and_inspection_evidence`, `test_inspection_record_with_failed_setup_is_not_evidence`, and `test_client_package_change_requires_every_spec_title` are red. At pre-c8 `0af450c5`, literal-only `spec_titles()` still makes the dynamic-title case red. The receipt's listed c7 and c8 failures agree with those trees.

Criterion mapping: SC-05 → `CheckContract.*` and `test_gate_enforces_predicates_and_inspection_evidence`; SC-06 → `test_identity_and_pin`, `test_results_cannot_bring_their_own_check_list`, `test_screenshot_evidence_must_be_real_webp`, `test_accounting_and_status_consistency`, `test_inspection_manifest_entries_need_their_screenshot`, `test_inspection_record_with_failed_setup_is_not_evidence`; SC-10 → `test_missing_runner_or_contract_blocks` and T-07 `test-suite-layout.py` case 12; SC-11 → `test_client_package_change_requires_every_spec_title`. SC-02/03/04 are correctly not claimed as T-01-owned. T-03 supplies only a pre-lane missing-script command (`receipt-harness-frontend-dev-T-03-c0.md:5`), T-06 supplies the committed 22-RED run, and T-13's seven named probes cover reporter failures. None is a named pre-fix assertion of SC-04's pixel-baseline-default rule. Therefore the receipt's allocation is scoped honestly, but it is not a complete criterion-mapped fail-first record required to close V7-02.
**Finding (substance/high, T-01, pin `0163657540ab3ad3be4ff5aa34f838dc4f1e17d8`):** a default pixel-baseline gate could regress without any cited fail-first assertion reddening. The cited T-03/T-06/T-13 evidence does not cover that rule.


```yaml
VERDICT: FAIL
DIGEST:
  headline: "V7-01 closes at 0163657540ab3ad3be4ff5aa34f838dc4f1e17d8, but V7-02 cannot close: SC-04 has no pinned, criterion-mapped fail-first failure."
  suite: pass
  failures: 1
  matrix_ok: false
  kinds:
    - kind: unit
      state: satisfied
      cmd: "python3 tests/unit/test-ui-verification-contract.py"
      named_tests: 24
  coverage_gaps:
    - "SC-04: no pinned failing test or executable pre-fix result proves pixel baselines do not gate by default."
  sc_evidence:
    - { id: SC-05, test: "tests/unit/test-ui-verification-contract.py:123-191,287-294" }
    - { id: SC-06, test: "tests/unit/test-ui-verification-contract.py:210-300" }
    - { id: SC-10, test: "tests/unit/test-ui-verification-contract.py:323-333" }
    - { id: SC-11, test: "tests/unit/test-ui-verification-contract.py:302-321" }
  fail_first:
    - { sc: SC-05, evidence: "pre-T-01 module absence; pre-c7 test_gate_enforces_predicates_and_inspection_evidence red, receipt-main-direct-T-01-c8.md:14-16" }
    - { sc: SC-06, evidence: "pre-T-01 module absence; pre-c7 test_inspection_record_with_failed_setup_is_not_evidence red, receipt-main-direct-T-01-c8.md:14-16" }
    - { sc: SC-10, evidence: "pre-T-01 module absence; pre-c7 contract/runner mutants red, receipt-main-direct-T-01-c8.md:14-16" }
    - { sc: SC-11, evidence: "pre-c7 and pre-c8 test_client_package_change_requires_every_spec_title red, receipt-main-direct-T-01-c8.md:15-16" }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c8.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c8.md
```
