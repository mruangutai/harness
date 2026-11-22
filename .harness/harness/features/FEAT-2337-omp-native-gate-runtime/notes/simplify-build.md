# SIMPLIFY — build seam, FEAT-2337

**Route.** build-phase step 3 hands SIMPLIFY to `harness-eng-lead`, which DEC-174 bars in a
main-session-direct feature. Instead, the main session ran the four angles as four parallel,
read-only, ungoverned `scout` readers (FEAT-2225 / FEAT-2274 precedent), one angle file each, and
applied the findings itself.

**Scope.** `git diff 0d7326e4 HEAD -- . ':!.harness/harness/features'` at `27f8d569`. `0d7326e4` is
origin/main and the merge base, so the diff holds exactly this feature's changes. Settled and not
flaggable: the signed plan and BRIEF, the grilling intent, and the delegated rulings in
`notes/answers-2026-11-22-*.md` (grading base, fix-run receipts, clean-tree reading, merge-gate
as a narrow gate). Also settled: parallel spawn with no TS skipping or dispatcher, the single 30 s
constant, the receipt-only trust model, the deliberate dual classifiers, DEC-205, and no weakening
of assertions.

| Angle | Reader | Findings |
|---|---|---|
| REUSE | `B_SimplifyReuse` | 2, both applied |
| SIMPLIFICATION | `B_SimplifySimplification` | none |
| EFFICIENCY | `B_SimplifyEfficiency` | none. Not elevated: two `discover_expected` tree listings per two-kind return, no measured cost |
| ALTITUDE | `B_SimplifyAltitude` | none |

**Applied.**
1. `validate-digest.py`: `_claimed_receipt_kinds` repeated `_satisfied_kinds`' normalization of
   a satisfied kind. Both now read through one ordered iterator, `_satisfied_kind_names`, so the
   matrix floor and the receipt check cannot drift apart. Claim order and deduplication are
   preserved.
2. `test-omp-native-gate-runtime.py`: the hand-written benchmark `median` is replaced by
   `statistics.median`, the convention `test-run-unit-tests-shards.py` already uses. The
   benchmark input validation (non-empty samples) is unchanged.

No assertion was touched.
