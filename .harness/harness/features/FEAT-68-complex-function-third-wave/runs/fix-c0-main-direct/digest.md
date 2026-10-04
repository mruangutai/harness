# FEAT-68 fix c0 — main-session-direct (DEC-174)

```yaml
VERDICT: PASS
DIGEST:
  headline: "VF-01 and VF-02 repaired without touching production: the SC-02 evidence is recollected between clean detached baseline and pin checkouts under the one signed checkout-root normalisation (53/57 identical; five ledgered lines D-01..D-05 with exact old/new bytes and rulings), and every receipt names the immutable pin 9ab1813e."
  tests_added: 0
  suite: pass
  task: T-01
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/red-first-receipts.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/build-divergences.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/answers-validate-validator.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/amendments-build-main-direct.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/handoff-build.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/runs/build-main-direct/digest.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md
```

Evidence-only fix; production bytes at `9ab1813e` are untouched, so the implementation pin
stands. VF-01: baseline recaptured in `feat68-base-e655f14a` (detached, clean); pin re-run in a
fresh `feat68-cleanpin-9ab1813e`; the mkdtemp and unittest-timing substitutions are removed and
the lines they masked are ledgered D-02..D-05 in built form (rulings in
`notes/answers-validate-validator.md` A-1/A-2). VF-02: `red-first-receipts.md` names `9ab1813e`
and records `0c15bad6` as a superseded candidate (A-3); the build digest carries an append-only
correction; the amendment note's ledger references follow the renumbering.
