# FEAT-70 pinned code review — cycle 1

## BLUF

PASS with one non-blocking medium code-grade advisory. Stage 1 passes SC-01..SC-03 and D-01/D-02 at immutable implementation pin `73ba9dceee11253bbf57b7ca1b36323c81d83891`; cycle-0 VAL-01 and VAL-02 are closed. Stage 2 passes the canonical production bar; the retained SC-03 integration case remains grade 2, which is advisory under the grade policy.

## Stage 1 — spec compliance: PASS

- **SC-01 / ownership / pin:** the entry remains the sole 300-line hyphenated CLI with one `VERBS` table, four registrars, `main`, and INV-40 `signed_task_hash` import (`.claude/skills/harness/bin/plan-merge.py:146-300`). The pin contains exactly `__init__.py` plus the ten specified owner modules. Direct `feat70-grade-assert.py 73ba9dce... 9e531b34...` execution exited 0: 237 functions across 12 files all grade >=4, all twelve named functions have their required owners, and the public import works. Commits after the immutable pin alter feature state/receipts only, not implementation or integration-test source.
- **VAL-01:** `notes/receipt-scripts/feat70-grade-assert.py:43-57` separates nested-definition collection from `bodies`; canonical grading reports `bodies` grade 4 (cyclomatic 5, cognitive 1, ABC 10.2), `RESULT: PASS`.
- **VAL-02:** `tests/integration/test-hooks-install.py:63-71,130-141` copies every sibling Python package, including `check_state/` and `plan_merge/`; `tests/integration/test-post-merge-sweep.py:91-100,153-161` links the same set into its isolated fixture. Direct runs of both files exited 0, including real merge/ship paths importing those entries.
- **SC-02:** the committed receipt binds baseline `9e531b34fc04f752cedf51586dc13c460580901a` to pin `73ba9dceee11253bbf57b7ca1b36323c81d83891`, records 107/107 pre-existing cases green on both sides, 293 aligned behavioral invocations, 6,518 aligned scratch commands, and `overall: PASS` (`notes/clean-pin-byte-receipts.generated.md:1-31`). Differences remain exactly the accepted seven records: two traceback-coordinate stderr records and five shipped-plan anchor records. `notes/divergence-rulings.json` enumerates exactly those records; this review preserves rather than re-litigates the ruling.
- **SC-03:** `_render_field` returns one element per physical block-scalar line (`plan_merge/text.py:402-434`); `_splice_amendments` relocates each later field after every splice (`plan_merge/amendments.py:99-121`). The retained case asserts exit/output, both landed fields, literal-block form, ordered ledger, valid ledger, and no traceback (`tests/integration/test-plan-merge.py:4414-4450`); the red-first receipt records baseline `IndexError` with unchanged files and pin success.
- **D-01/D-02:** the reset/resume family remains in `stations.py`; `_task_status_line` delegates to `_task_search` and `_status_in_task` (`plan_merge/stations.py:193-254`). `_verify_spliced` retains its signature and ordered reload/schema/id/replacement checks (`plan_merge/union.py:41-142`). No scope creep, omission, mismatch, shim, second dispatcher, or legacy private entry re-export was found.

## Stage 2 — code quality: PASS with advisory

Canonical grading of `9e531b34fc04f752cedf51586dc13c460580901a..01af5a511f356d76ee91ced8922e2d53e71479e3` reports 250 passing changed functions, no high-severity record, and one grade-2 test record. Review of moved guard/write paths found no new fail-open or silent-failure branch: parse, schema, missing-item, approval-mutation, and post-splice identity failures remain loud refusals before atomic write.

1. **Medium · substance · T-01 · advisory/non-blocking.** `tests/integration/test-plan-merge.py:4414-4450`, `case_feat70_record_amendments_after_a_block_scalar_splice`, remains grade 2 (cyclomatic 7, cognitive 3, ABC 30.1). **Scenario:** when a maintainer changes one SC-03 postcondition, setup, command execution, two parsed outputs, and six independent assertions must all be held in one function; another assertion expands an already below-bar ABC surface. **Disposition:** required grade-2 advisory, non-blocking. Eventual expected result: behavior-preserving decomposition with changed test functions grade >=3.

## Review record

```yaml
VERDICT: PASS
DIGEST:
  headline: "SC-01..SC-03, both cycle-0 closures, immutable-pin identity, exact package ownership, and the accepted seven-record ruling pass; canonical grading has only one non-blocking grade-2 test advisory."
  severity_max: med
  findings:
    - kind: substance
      scope: task
      severity: med
      reader: code-reviewer
      summary: "T-01: tests/integration/test-plan-merge.py:4414-4450 case_feat70_record_amendments_after_a_block_scalar_splice remains grade 2 (ABC 30.1), below the test bar of 3."
      why: "A maintainer changing one SC-03 postcondition must reason through setup, execution, two parsed outputs, and six independent checks in one below-bar function; another assertion increases the already flagged reader load. Disposition: advisory, non-blocking."
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  grade_2_reasons:
    - "case_feat70_record_amendments_after_a_block_scalar_splice: the test coherently proves one atomic two-amendment transaction across exit/output, both plan mutations, literal-block preservation, ledger order, and ledger validity; splitting it would obscure that single observable contract, so retain the grade-2 case as a non-blocking advisory."
  reviewed: "9e531b34fc04f752cedf51586dc13c460580901a..01af5a511f356d76ee91ced8922e2d53e71479e3"
  human_commits_in_scope:
    - d6195d62056330d12ff3b8cf02d94f6110ccbe11
    - 5b020528c8f924b3b6c576f04e7a7057e07f90e7
    - c9452c40e5debe6ebcc58fdee9f84d15c84cc58c
    - 73ba9dceee11253bbf57b7ca1b36323c81d83891
    - 9cf33e6b4935e5b7686930b8fc3c27c91734949a
    - dd9ae2f6aac7f81120f404906e0b23bfdd037a25
    - 35b42d2ac73460255d1e6b78cac5d8101ad8ad28
    - dbba18f7b4f068d33c90b61d7f635f0ca3b08267
    - b900d207429cc91a390f12758bb8cc424c130b84
    - 937b1242bfb09b18c84d7e512070817080e1787f
    - 6ffc06a12fc4c13f92f78943d9599eb0e42a5e6b
    - 50996922d0c122d92498f093255ce507e39babed
    - c48c14bd9aa2994c0949da496462567989bdc5f7
    - ac9f33b236020d6ac72f9fbe76cd1c43a626b1fd
    - fc1dfb0664468c95ce0826fb70824b8c0a53a665
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-70-long-file-plan-merge-package/.harness/harness/features/FEAT-70-long-file-plan-merge-package/notes/review-harness-code-reviewer-c1.md
```
