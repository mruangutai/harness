# FEAT-68 validate-c1 — corrected code review

## Disposition

**FAIL. Stage 1 fails; Stage 2 was not reached.** This correction withdraws and supersedes the PASS in `notes/review-harness-code-reviewer-c1.md`. The implementation's mechanically checked grade remains `pass` (39 selected records, all grade 4 or 5), but it cannot cure the SC-02 evidence contradiction or SC-04 provenance omissions.

## Stage 1 — specification compliance: FAIL

- **SC-02 mismatch:** `notes/clean-pin-byte-receipts.md` says under “Owning suites at the pin vs baseline” that three fresh `mkdtemp()` paths and the unittest wall-clock were normalized. Its table and exact-byte section instead mark the affected suites `NO`, while `notes/build-divergences.md` D-02..D-05 says those bytes were retained as divergences under checkout-root-only normalization. An auditor can therefore exclude a changed byte which the signed experiment requires to remain visible and ledgered.
- **SC-04 omission:** the receipts point to ephemeral `/tmp/feat68-baseline.py` and JSON outputs rather than preserving the exact 57-suite capture/comparison invocation. `notes/build-divergences.md` names full base `e655f14a56a14bf1777cae55a19195c9af10505d` but calls `9ab1813e86067ca4a21a84f49364cf4f453055b4` only “the pin.” The applicable receipts consequently do not each name the exact commands and full base/pin identities required by SC-04. A later auditor cannot distinguish the signed experiment from a capture made with a different invocation or revision.
- SC-01 and SC-03 remain met. SC-05's automated portions are green; its final markdown/no-HTML-sibling validate action remains correctly sequenced after a clean panel. The pinned range contains no `[harness:human]` commit. Working-tree changes are confined to Harness feature records and do not invalidate the pinned source review.

## Stage 2 — NOT REACHED

The two-stage protocol stops after Stage 1 fails. The earlier mechanical result is retained only as evidence: `code_grade: pass`, 39 selected functions at grade 4 or 5. It is not a Stage 2 PASS and does not mask specification failure.

## Findings

1. **CR-C1-01 — form, med, T-01 / main-session-direct; existing class (QA VF-03 / PM GC-C1-01).** Readers: code-reviewer, QA, PM, validator-lead. Scenario: an auditor follows the receipt's opening paragraph and normalizes a fresh `mkdtemp()` or unittest-time byte, producing “identical” where D-02..D-05 and the signed checkout-root-only rule require a divergence. Remedy: correct only the stale paragraph; preserve the table, raw lines, hashes and rulings. Artifact: this correction.
2. **CR-C1-02 — form, med, T-01 / main-session-direct; new class in validate-c1 (PM GC-C1-02).** Readers: code-reviewer, PM, validator-lead. Scenario: because the temporary scripts are absent and the ledger omits the full pin SHA, a later auditor can attribute the 57-suite hashes and 53/57 result to a different invocation or revision. Remedy: record the complete reproducible capture/comparison invocation and full base/pin SHAs in every applicable receipt without changing measurements or chronology. Artifact: this correction.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Stage 1 FAIL at 66b9c914daa3b8b5a4bd35570768027515ed3d7b: SC-02 contradicts its normalization rule and SC-04 lacks exact-command/full-pin provenance; Stage 2 NOT REACHED."
  severity_max: med
  findings:
    - { id: CR-C1-01, kind: form, scope: task, severity: med, reader: code-reviewer, task_binding: T-01, owner: main-session-direct, new_class: false, readers: [code-reviewer, harness-qa, harness-pm, harness-validator-lead], summary: "The clean-pin receipt says mkdtemp/time were normalized although D-02..D-05 retain them as divergences.", scenario: "An auditor can exclude a changed nondeterministic byte and report identity contrary to the signed checkout-root-only comparison.", remedy: "Replace the stale normalization wording while preserving measurements and D-02..D-05.", artifact: ".harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-code-reviewer-c1-correction.md" }
    - { id: CR-C1-02, kind: form, scope: task, severity: med, reader: code-reviewer, task_binding: T-01, owner: main-session-direct, new_class: true, readers: [code-reviewer, harness-pm, harness-validator-lead], summary: "The receipts omit the exact 57-suite capture/comparison invocation and the divergence ledger omits the full pin SHA.", scenario: "A later auditor can mistake output from a different command or revision for the signed experiment.", remedy: "Record the complete reproducible invocation and full base/pin SHAs in each applicable receipt.", artifact: ".harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-code-reviewer-c1-correction.md" }
  must_fix: [CR-C1-01, CR-C1-02]
  spec_violations:
    - { kind: mismatch, path: ".harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md", ref: SC-02 }
    - { kind: omission, path: ".harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md", ref: SC-04 }
    - { kind: omission, path: ".harness/harness/features/FEAT-68-complex-function-third-wave/notes/build-divergences.md", ref: SC-04 }
  code_grade: pass
  reviewed: "e655f14a56a14bf1777cae55a19195c9af10505d..66b9c914daa3b8b5a4bd35570768027515ed3d7b"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-68-complex-function-third-wave/.harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-code-reviewer-c1-correction.md
```
