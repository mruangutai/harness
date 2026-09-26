# FEAT-66 build — main-session-direct (DEC-174)

```yaml
VERDICT: PASS
DIGEST:
  headline: "check-domain.shape_problems, validate-digest.validate and plan-merge.apply_merge are drivers over per-rule functions at bar 4 (from grade 1: cyc 135/124/59), every extracted helper is at bar 4, and all eleven owning suites are byte-identical to the baseline at a clean checkout of the implementation pin e2b580a6."
  tests_added: 1
  suite: pass
  task: T-01
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .claude/skills/harness/bin/check-domain.py
    - .claude/skills/harness/bin/validate-digest.py
    - .claude/skills/harness/bin/plan-merge.py
    - tests/integration/test-check-domain-artifact.py
    - tests/unit/test-driver-grades.py
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/build-divergences.md
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/red-first-receipts.md
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/clean-pin-byte-receipts.md
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/amendments-build-main-direct.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-66-complex-function-drivers/notes/clean-pin-byte-receipts.md
```

One run covers T-01: `abe0d43a` (red lock), `c0099fc1` (shape_problems → SHAPE_RULES, 36 helpers),
`285e6ab4` (validate → common rules then persona groups, 34 helpers), `8c3e0015` (apply_merge → phases,
20 helpers), `e2b580a6` (the four-angle simplify pass applied: eight fold-ins) — the implementation pin —
then `25259fe0` for the receipts and this digest's commit for the amendment and close. Full runners at the
pin: 113 unit / 70 integration green. Evidence: `notes/clean-pin-byte-receipts.md` (11/11 owning suites
identical at a clean detached checkout of the pin, after normalising each checkout's own absolute path;
the lock green at the pin and red verbatim against the baseline tree; every extracted function graded),
`notes/red-first-receipts.md`, and `notes/build-divergences.md` (no output divergence; D-01..D-08 ruled;
the simplify pass's applied/skipped record).

Three things the panel should weigh:
1. **pm's intent vs the bar (D-06).** The intent asked that `apply_merge` alone extend the six accumulator
   lists and construct `MergeResult` on each return path; both forms graded 2–3 on the ABC axis, so the
   key walk is `_merge_keys` (`_fold_merge_rows` extends the same six named lists in key order) and
   `MergeResult` is built once on the union path. Order semantics are unchanged.
2. **Two source-anchor mutants repointed (D-01/D-02)** in `test-check-domain-artifact.py`: the red proofs
   now mute the rule *function* rather than slice an inline branch. Same proof, same non-traceback
   requirement.
3. **Plan amendment (D-04)**: `tests/integration/test-validate-digest-shadows.py` exists only as an
   untracked file in the operator's main checkout; dropped from T-01's `files`/`verify` via
   `record-amendments` (`notes/amendments-build-main-direct.md`).

Residual (briefing rows, not applied): derive `SHAPE_PATTERNS` from `SHAPE_RULES` (pre-existing
constant, outside SC-03); `check-state._inv15_digest_verdict` hand-rolls `_return_tail` and cites
validate-digest line numbers that moved.
