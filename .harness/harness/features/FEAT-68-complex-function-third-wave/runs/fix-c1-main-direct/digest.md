# FEAT-68 fix c1 — main-session-direct (DEC-174)

```yaml
VERDICT: PASS
DIGEST:
  headline: "VF-03 and VF-04 repaired in the receipts only: the clean-pin receipt's opening states the checkout-root normalisation alone (consistent with the table and D-01..D-05), and it now carries the exact reproduction — both full SHAs, the three capture/comparison scripts preserved verbatim under notes/receipt-scripts/, and the three invocations from the repository root."
  tests_added: 0
  suite: pass
  task: T-01
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/build-divergences.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/red-first-receipts.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts/feat68-baseline.py
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts/feat68-cleanpin.py
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts/feat68-grade-assert.py
  expertise_update: []
artifact: .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md
```

Form-only; no measurement, ruling, chronology or production byte changes. Pin `9ab1813e86067ca4a21a84f49364cf4f453055b4` unchanged. VF-03: the stale three-line opening (left from the pre-c0 version of the receipt) replaced by the root-only statement. VF-04: `## Reproduction` section added with both full SHAs, the preserved scripts and the exact invocations; the ledger and the red-first receipt name the full pin SHA.
