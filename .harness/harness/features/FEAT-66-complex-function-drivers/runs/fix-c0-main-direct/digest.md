# FEAT-66 fix c0 — main-session-direct (DEC-174)

```yaml
VERDICT: PASS
DIGEST:
  headline: "Validate c0's six must_fix items are closed at f882dc3e: no production byte changed since e2b580a6; the second grade lock is gone (the plan's inline assertion is the SC-01 evidence, green at the pin and red at the baseline in clean checkouts), the stale validate exemption is removed so the unit matrix is green, change_type is cross_module, D-02 is amended to the built form, SC-02's fail-first equivalence and the D-09 path-line ruling are recorded."
  tests_added: 0
  suite: pass
  task: T-01
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - tests/unit/test-driver-grades.py
    - tests/unit/test-code-grade.py
    - .harness/harness/features/FEAT-66-complex-function-drivers/plan.yaml
    - .harness/harness/features/FEAT-66-complex-function-drivers/BRIEF.md
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/answers-validate-validator.md
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/build-divergences.md
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/red-first-receipts.md
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/clean-pin-byte-receipts.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-66-complex-function-drivers/notes/clean-pin-byte-receipts.md
```

Per must_fix (operator rulings in notes/answers-validate-validator.md):
- MF-01 → D-09: the three `ok` lines naming the running checkout's path, exact old/new bytes in the receipt; ruled not a divergence; normalised comparison stands.
- MF-02 → D-02 amended (choice and because) to the built form via `plan-merge.py amend`.
- MF-03 → `tests/unit/test-driver-grades.py` deleted; SC-01's evidence is T-01 verify's inline assertion, run in clean checkouts of the pin (exit 0) and the baseline (exit 1, three drivers grade 1).
- MF-04 → the `("validate-digest.py", "validate"): 1` exemption removed from `tests/unit/test-code-grade.py`; `--kind unit` green (42 files).
- MF-05 → BRIEF SC-02 carries the fail-first-equivalence sentence with the ruling.
- MF-06 → T-01 change_type `cross_module`.
Implementation pin `f882dc3e` (production bytes identical to `e2b580a6`); receipts committed after it.
