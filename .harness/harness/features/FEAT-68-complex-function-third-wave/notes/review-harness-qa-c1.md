# QA gate — FEAT-68 complex function third wave, c1

**FAIL:** the required matrix and all five T-01 verification assertions pass at review SHA `66b9c914`, but the repaired SC-02 receipt still contains an incompatible normalization claim. This leaves the signed byte-comparison record internally contradictory.

## Phase 1 expectation

From `BRIEF.md` and `plan.yaml`, before code inspection: `cross_module` requires active unit and integration coverage. SC-01 requires the five-target grade lock and baseline red; SC-02 requires the clean detached baseline/pin byte experiment using only checkout-root normalization with all other deltas ledgered; SC-05 requires renderer/residue removal, both kinds green, and its baseline-presence red. SC-03/04 are inspection criteria.

## Matrix and T-01 verification

| Kind | Command | Result | Discovery |
|---|---|---:|---:|
| unit | `python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` | pass | 41 files |
| integration | `python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration` | pass; `0 failure(s)` | 70 files |

The exact chained T-01 `verify:` block passed: both runners, the five-target grade assertion, baseline-102/remaining-HTML assertion, and prohibited-reference assertion.

## SC evidence

- **SC-01 — met:** the grade assertion passed at the review pin. `notes/red-first-receipts.md:19-31` records a clean detached baseline red with exactly the five targets, all grade 1.
- **SC-02 — not met:** `notes/clean-pin-byte-receipts.md:11-15` says the comparison also normalized fresh `mkdtemp()` paths and the unittest wall-clock, while its table and `notes/build-divergences.md:11-45` say those are retained as D-02..D-05 real divergences under checkout-root-only normalization. The two accounts cannot both describe the signed experiment.
- **SC-03 — met:** T-01's HTML and reference-removal assertions passed; the complete baseline 102-file census is exercised by the verify block.
- **SC-04 — not met:** the post-pin chronology correctly identifies `9ab1813e` and `0c15bad6` only as superseded (`notes/red-first-receipts.md:3-5`), but the conflicting SC-02 normalization wording means this receipt set is not a single unambiguous record.
- **SC-05 — partial:** the pin-side removal assertions and both test kinds pass; the baseline red is at `notes/red-first-receipts.md:33-40`. The orchestrator-owned final markdown/no-HTML-sibling validation is correctly absent before clean panel fan-in. Its source/matrix preconditions are clean, but the final action remains sequenced after this panel.

## Finding

- **VF-03 — form, med, must fix; T-01.** An auditor using `notes/clean-pin-byte-receipts.md:13-15` is told `mkdtemp()` and wall-clock bytes were normalized, while the same record exposes them as unnormalized `NO` comparisons and the ledger explicitly calls them D-02..D-05. Thus a future output change limited to those lines can be incorrectly treated as excluded from the signed byte experiment rather than as a ledgered divergence. Remedy: replace the stale normalization description with checkout-root-only wording consistent with the table, D-02..D-05, and A-1; retain the exact raw-byte lines and rulings.

## Principles applied

- **Build the Lever:** relied on the committed, rerunnable T-01 verification chain rather than hand-counting removals or grades.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "T-01 matrix and verify block pass at 66b9c914, but the SC-02 receipt contradicts its checkout-root-only normalization record."
  suite: pass
  failures: 0
  matrix_ok: true
  reviewed_sha: "66b9c914"
  kinds:
    - kind: unit
      state: satisfied
      cmd: "python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit"
      named_tests: 41
    - kind: integration
      state: satisfied
      cmd: "python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration"
      named_tests: 70
  coverage_gaps:
    - "SC-02: the signed byte-comparison receipt is internally contradictory about whether D-02..D-05 were normalized or ledgered."
  sc_evidence:
    - { id: SC-01, test: "T-01 inline code-grade assertion; notes/red-first-receipts.md:19-31" }
    - { id: SC-02, test: "notes/clean-pin-byte-receipts.md:11-149; notes/build-divergences.md:3-45" }
    - { id: SC-05, test: "T-01 HTML/residue assertions; notes/red-first-receipts.md:33-40" }
  fail_first:
    - { sc: SC-01, evidence: "notes/red-first-receipts.md:19-31: clean detached baseline assertion exits 1 for exactly five grade-1 targets" }
    - { sc: SC-02, evidence: "notes/red-first-receipts.md:42-45: approved baseline-versus-pin byte-comparison equivalent; clean-pin receipt records 53/57 and D-01..D-05" }
    - { sc: SC-05, evidence: "notes/red-first-receipts.md:33-40: baseline has renderer/residue and 102 HTML derivatives" }
  findings:
    - id: VF-03
      kind: form
      severity: med
      task_binding: T-01
      scenario: "Receipt lines 13-15 say mkdtemp and timing were normalized, while its table and D-02..D-05 retain them as differences; an auditor can falsely exclude a changed byte from the signed comparison."
      remedy: "Correct the receipt to say checkout-root normalization only and retain D-02..D-05 as ledgered raw differences."
      artifact: ".harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-qa-c1.md"
  must_fix: [VF-03]
  severity_max: med
  sc_status:
    - { id: SC-01, verdict: met }
    - { id: SC-02, verdict: not_met }
    - { id: SC-03, verdict: met }
    - { id: SC-04, verdict: not_met }
    - { id: SC-05, verdict: partial, final_ship_review_preconditions: clean_and_sequenced }
  open_questions: []
  files_touched: [".harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-qa-c1.md"]
  expertise_update: []
artifact: "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-68-complex-function-third-wave/.harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-qa-c1.md"
```