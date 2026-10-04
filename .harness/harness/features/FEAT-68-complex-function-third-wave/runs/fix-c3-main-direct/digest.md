# FEAT-68 fix c3 — main-session-direct (DEC-174; operator-authorised fourth round, A-5)

```yaml
VERDICT: PASS
DIGEST:
  headline: "VF-04-C3 and VF-05-C3 repaired: the comparison generator executes every suite once and derives the table, the hashes and the raw-difference lines from that one execution, writing a separate generated file committed exactly as produced; the hand-written receipt states the reproduction from the feature worktree root where it was run and cites the generated file; D-02..D-05 carry that execution's bytes."
  tests_added: 0
  suite: pass
  task: T-01
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.generated.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/build-divergences.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/answers-validate-validator.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts/feat68-cleanpin.py
    - .harness/harness/features/FEAT-68-complex-function-third-wave/feature.json
  expertise_update: []
artifact: .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md
```

Form/provenance only; production untouched at pin `9ab1813e86067ca4a21a84f49364cf4f453055b4`. The
rework ruling was raised to 4 rounds / 150 min on the operator's "yes" (A-5). `feat68-cleanpin.py`
has one `subprocess.run` per suite; `outputs[s]` from that call feeds both the hashed table row and
the raw-difference lines. The generated file is the command's output, untouched; the hand-written
receipt is separate so a regeneration can never overwrite the record.
