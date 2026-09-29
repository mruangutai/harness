# FEAT-70 pinned code review — cycle 0

## BLUF

FAIL on Stage 2 code quality. Stage 1 passes: the pinned implementation and reproducible receipts satisfy SC-01..SC-03, the T-01 and T-02 signed verification commands pass, and the seven recorded differences are exactly the two traceback-coordinate stderr records plus five shipped-plan anchor records covered by the delegated rulings. The canonical pinned-range grader then finds one grade-3 production function and one grade-2 test function, so the review cannot report a passing code grade.

## Stage 1 — spec compliance: PASS

- SC-01: the unchanged hyphenated interface is the 300-line entry with one `VERBS` table, four registrars, `main`, and the INV-40 `signed_task_hash` re-export (`.claude/skills/harness/bin/plan-merge.py:120-300`). The package has exactly `__init__.py` plus the ten specified owner modules. The T-01 signed verification passed, including all entry/package functions at grade 4 or better and all three named integration suites.
- SC-02: the committed clean-checkout receipt records the same 107 pre-existing cases passing at baseline and pin, 293 aligned behavioral invocations, and 6,518 aligned scratch commands (`notes/clean-pin-byte-receipts.generated.md:1-31`). Its only differences are the two traceback frame-path/coordinate stderr records and five `check` records in four shipped plans. Those exact seven records—and no broader class—are listed in `notes/divergence-rulings.json:1-51` and reproduced with their scoped rulings in `notes/build-divergences.md:1-70`. The T-02 signed verification passed against the committed receipt and immutable implementation pin.
- SC-03: `_render_field` now returns one list element per physical line (`.claude/skills/harness/bin/plan_merge/text.py:402-434`), and `_splice_amendments` re-locates each later target after every splice (`.claude/skills/harness/bin/plan_merge/amendments.py:99-121`). The retained integration case observes both fields, literal-block form, ordered ledger entries, valid ledger, exit zero, and no traceback (`tests/integration/test-plan-merge.py:4414-4450`); the red-first receipt records baseline `IndexError` with unchanged plan/ledger bytes and pin success with both changed atomically (`notes/red-first-receipts.md:3-24`).
- D-01/D-02: the reset/resume family is owned by `stations.py`; `_task_status_line` delegates to `_task_search` and `_status_in_task` with the specified task-range and first-match semantics (`.claude/skills/harness/bin/plan_merge/stations.py:193-254`). `_verify_spliced` delegates in refusal order to reload, schema, union-id, and replacement checks (`.claude/skills/harness/bin/plan_merge/union.py:41-132`).
- Clean cutover: canonical-reader rows and `scanned_files` name the package owners (`tests/integration/canonical-reader-classification.json:1695-1895,2162-2239`); test tree copying has one implementation in `copy_executable_package`, with both entry-specific helpers delegating (`tests/integration/check_state_support.py:71-86`; `tests/integration/test-plan-merge.py:2033-2035`). No legacy private-helper import from the entry remains.

## Stage 2 — code quality: FAIL

1. **High, substance, T-02 — canonical production grade failure.** `.harness/harness/features/FEAT-70-long-file-plan-merge-package/notes/receipt-scripts/feat70-grade-assert.py:43-52` (`bodies`) grades 3 (cognitive 15) against the required production bar of 4. Concrete failure scenario: running the mandatory canonical range grade over `9e531b34..138d11a4` exits 1 with `SEVERITY: high`, so a reviewed merge containing the reproducibility tooling cannot satisfy the repository's code-quality gate even though the narrower SC-01 surface assertion passes. Expected wording/result: every changed production Python function reports `GRADE: 4` or better and `RESULT: PASS`; `bodies` currently reports `GRADE: 3`, `RESULT: FAIL`, `SEVERITY: high`.
2. **Medium, substance, T-01 — grade-2 regression test requires decomposition.** `tests/integration/test-plan-merge.py:4414-4450` (`case_feat70_record_amendments_after_a_block_scalar_splice`) grades 2 (ABC 30.1) against the test bar of 3. Concrete failure scenario: a maintainer changing one of the six independently checked postconditions must reason through setup, subprocess execution, two parsed outputs, and all assertions in one function; the canonical grader flags the case `REASON REQUIRED`, and a further assertion increases the already below-bar reader load. Expected result: changed tests grade 3 or better; this function reports `GRADE: 2`. This is non-blocking by grade policy but must be recorded.

## Review record

```yaml
VERDICT: FAIL
DIGEST:
  headline: "SC-01..SC-03 and the exact delegated divergence rulings pass, but the canonical pinned-range grade fails on a grade-3 receipt function; the SC-03 test is also grade 2."
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      summary: "T-02: feat70-grade-assert.py:43 bodies grades 3, so canonical grading of 9e531b34..138d11a4 exits 1 instead of reporting every production function grade >=4."
      why: "A realistic merge/review gate over the required pinned range rejects the change with SEVERITY: high even though the narrower implementation-surface assertion passes."
    - kind: substance
      scope: task
      severity: med
      reader: code-reviewer
      summary: "T-01: test-plan-merge.py:4414 case_feat70_record_amendments_after_a_block_scalar_splice grades 2 (ABC 30.1), below the test bar of 3."
      why: "The six-postcondition regression mixes fixture setup, execution, plan parsing, ledger parsing, and assertions in one below-bar function, increasing reader load for any future amendment-contract change."
  must_fix:
    - "T-02: restructure `.harness/harness/features/FEAT-70-long-file-plan-merge-package/notes/receipt-scripts/feat70-grade-assert.py:43-52` so `bodies` grades >=4, then rerun the canonical code-grade command over `9e531b34fc04f752cedf51586dc13c460580901a..138d11a4ac2b762a57bf0800bea2db95fc5d878a`."
  spec_violations: []
  code_grade: fail
  reviewed: "9e531b34fc04f752cedf51586dc13c460580901a..138d11a4ac2b762a57bf0800bea2db95fc5d878a"
  human_commits_in_scope:
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-70-long-file-plan-merge-package/.harness/harness/features/FEAT-70-long-file-plan-merge-package/notes/review-harness-code-reviewer-c0.md
```
