# FEAT-68 fix c2 — main-session-direct (DEC-174; operator-authorised third round, A-4)

```yaml
VERDICT: PASS
DIGEST:
  headline: "VF-04-C2 repaired: the reproduction section names the scripts' real feature-tree path, the preserved feat68-cleanpin.py loads its grade-assertion sibling by its own directory, and the recorded step-3 invocation was then run verbatim from the repository root to regenerate the receipt it describes (53/57 identical again; D-02..D-05 new-bytes synced to that run)."
  tests_added: 0
  suite: pass
  task: T-01
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/build-divergences.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/answers-validate-validator.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts/feat68-cleanpin.py
    - .harness/harness/features/FEAT-68-complex-function-third-wave/feature.json
  expertise_update: []
artifact: .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md
```

Form-only; production untouched at pin `9ab1813e86067ca4a21a84f49364cf4f453055b4`. The rework
ruling was raised to 3 rounds / 120 min on the operator's "yes" (A-4). The receipt is now the
output of the command it records: `python3 $SCRIPTS/feat68-cleanpin.py 9ab1813e e655f14a` with
`SCRIPTS=.harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts`,
run from the repository root against the existing detached checkouts; the per-run lines
D-02..D-05 carry this run's bytes.
