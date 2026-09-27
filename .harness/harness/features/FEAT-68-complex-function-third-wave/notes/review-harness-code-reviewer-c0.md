# Code review — FEAT-68 T-01

**BLUF:** FAIL at Stage 1. The pinned change uses two output normalizations that the approved SC-02/constraint explicitly excludes, so the evidence cannot establish the specified byte-preservation contract. Per the review protocol, Stage 2 quality review did not run. The mechanical changed-Python grade check independently passed all 34 selected records.

## Stage 1 — specification compliance: FAIL

### CR-01 — unapproved normalizations weaken the behavioral-equivalence proof

- **Kind / reader / severity:** substance / code-reviewer / high
- **Binding:** T-01, SC-02 and the BRIEF constraint “normalize only raw checkout-root output lines”.
- **Evidence:** `notes/clean-pin-byte-receipts.md` normalizes fresh `mkdtemp()` paths and unittest wall-clock text in addition to checkout roots; `notes/build-divergences.md` records the same departure. Raw hashes are retained, but the pass/fail comparison is made after all three transformations.
- **Concrete failure scenario:** if pin behavior changes a diagnostic’s temporary-directory value or changes the emitted unittest timing footer while the baseline does not, these added substitutions erase the changed bytes and report the suite identical, although SC-02 requires every non-root byte difference to enter the old/new/ruling ledger. The retained raw hashes show that bytes differ but do not classify or rule those differences.
- **Required outcome:** either collect/ledger comparisons under the signed root-only normalization or obtain an approved specification change before treating these extra normalizations as proof.

The renderer/test/classification/reference removal, `.omp/commands/harness.md` cleanup, 102 HTML deletions, D-01 `112 → 111` discovery change, five production decompositions, and both source-anchor repoints otherwise serve SC-01/SC-03/SC-05. D-01 is the direct observable consequence of deleting the prescribed test and is explicitly ledgered, so it is not an additional defect. Inspection of `_VERDICT_HANDLERS` found the unknown-outcome default is `_deny_verdict`, which exits 2; it is fail-closed rather than fail-open.

### CR-02 — red-first receipt identifies a superseded implementation pin

- **Kind / reader / severity:** form / code-reviewer / med
- **Binding:** T-01, SC-04.
- **Evidence:** `notes/red-first-receipts.md:3` calls `0c15bad6` the implementation pin, while `notes/clean-pin-byte-receipts.md:5` identifies the final immutable implementation pin as `9ab1813e86067ca4a21a84f49364cf4f453055b4`; the latter contains the required stale grade-exemption removal. `notes/handoff-build.md` then says the red-first evidence was committed after `9ab1813e`, contradicting the receipt’s own chronology.
- **Concrete failure scenario:** a later auditor following SC-04 cannot determine from the committed record whether red-first evidence was finalized only after the actual immutable implementation pin existed, because the authoritative receipt and handoff name different pins.

The absent pre-fan-in ship-review markdown is sequencing and was not treated as a defect.

## Stage 2 — code quality: NOT RUN

Stage 1 failed, so the protocol forbids proceeding to qualitative Stage 2. The required mechanical grade run over `e655f14a56a14bf1777cae55a19195c9af10505d..009b249b` reported **PASSING: 34**, with every selected production function at grade 4 or 5 and no grade-2 reason required. This mechanical result is reported as `code_grade: pass`, not as a Stage-2 quality verdict.

## Scope and pin

Reviewed the complete 132-path canonical range `e655f14a56a14bf1777cae55a19195c9af10505d..009b249b`, including all amended T-01/digest paths and deletions. No `[harness:human]` commits occur in the range. Worktree modifications are confined to feature metadata plus the supplied untracked handoff and do not alter pinned source bytes.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Stage 1 fails because two extra normalizations weaken SC-02's signed root-only byte comparison; Stage 2 was therefore not run."
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      summary: "T-01/SC-02: mkdtemp-path and unittest-time substitutions can erase non-root output changes and falsely report byte identity."
      why: "A pin-only change to either substituted value becomes identical after normalization instead of being entered in the required old/new/ruling ledger."
    - kind: form
      scope: task
      severity: med
      reader: code-reviewer
      summary: "T-01/SC-04: red-first-receipts names superseded pin 0c15bad6 while the immutable implementation pin is 9ab1813e."
      why: "The receipt and handoff give contradictory chronology, so an auditor cannot establish that the record was finalized after the actual immutable pin."
  must_fix:
    - "Bind SC-02 proof to the approved checkout-root-only normalization, or secure an approved spec change for the two additional substitutions before claiming equivalence."
  spec_violations:
    - kind: mismatch
      path: ".harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md"
      ref: SC-02
    - kind: mismatch
      path: ".harness/harness/features/FEAT-68-complex-function-third-wave/notes/red-first-receipts.md"
      ref: SC-04
  code_grade: pass
  reviewed: "e655f14a56a14bf1777cae55a19195c9af10505d..009b249b"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-68-complex-function-third-wave/.harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-code-reviewer-c0.md
```
