# FEAT-70 — clean-checkout implementation-pin receipts (reviewed record)

The generated receipt `clean-pin-byte-receipts.generated.md` is the evidence and is committed exactly
as `receipt-scripts/feat70-cleanpin.py` wrote it. This file is the human record beside it.

## Identity and chronology
- implementation pin: `73ba9dceee11253bbf57b7ca1b36323c81d83891` — the last production/test commit.
  Production: carve b900d207, twelve grade fixes dbba18f7, simplify pass 35b42d2a (the FIRST pin,
  superseded). Validate c0 found the sweep/hooks fixtures copy bin's files without its packages
  (VAL-02); that test-only fix, 73ba9dce, selected this pin and every measurement was re-run for
  it. Because the fix landed after the first pin's receipts were committed, the pin TREE contains
  the first pin's receipt files; nothing in them is claimed for this pin — the receipts for
  73ba9dce are the commit after it, derived from executions over 73ba9dce.
- baseline: `9e531b34fc04f752cedf51586dc13c460580901a`, the worktree's base (origin/main when cut).
- checkouts: `.claude/worktrees/harness/feat70-cleanpin-73ba9dce` and `feat70-base-9e531b34`, both
  detached, `git status --porcelain` empty, asserted by the script before any measurement.
- executions: `feat70-baseline.py` once per checkout (stamps printed in the generated receipt): the
  baseline's from the 13:50Z run (its tree did not change), the pin's fresh over 73ba9dce; the
  SC-03 cross-run and the two grade assertions once each at receipt time.

## Reproduction, exactly as run
From the FEAT-70 worktree root:
```
python3 .harness/harness/features/FEAT-70-long-file-plan-merge-package/notes/receipt-scripts/feat70-cleanpin.py 73ba9dceee11253bbf57b7ca1b36323c81d83891 9e531b34fc04f752cedf51586dc13c460580901a
```
(~65 min: two plain suite runs, two recorded suite runs of 293/295 CLI invocations, two scratch
corpora of 6,518 commands over 100 plans, grades.) Add `--reuse` to regenerate from the JSONs.

## What was measured (SC-02), and the result
1. The checkout's own `test-plan-merge.py`, plainly: exit 0 both sides; 107 pre-existing case
   identities identical; the pin adds `case_feat70_record_amendments_after_a_block_scalar_splice`.
2. Behavioural ledger: every CLI subprocess the 107 cases fork, through a recording shim (argv,
   exit, stdout, stderr, plan bytes before/after). 293 aligned invocations; 2 differing records,
   both ruled (below). Determinism applied identically on both sides by the driver, never to the
   tool: fixed fixture paths, frozen clock inside the shim, serialised `Popen` in the concurrency
   case. `behavioral_identity: PASS`.
3. Scratch corpus: 100 tracked `plan.yaml` (own record excluded), `check` + idempotent
   `set-feature-station` + per-task `set-task-station` + per-field `amend --show`, 6,518 commands per
   side, zero plan changes either side; 5 differing records in 4 plans, all ruled (below).
   `scratch_identity: PASS`.
4. Grades: 12 below bar 4 at baseline, 0 at pin; 198 moved functions with unchanged bodies keep
   their exact grade; 16 changed bodies and 23 new helpers all ≥4.

## Rulings (fable-advisor, blocking rulings delegated by the operator on 2026-09-28)
Recorded in `notes/divergence-rulings.json` and printed beside each record in the generated
receipt. Full text in `build-divergences.md`.
- Two stderr records in `case_feat61_approval_reset_refuses_an_unknown_task_station` (`delete-items`,
  an intended raise): traceback FRAME file/line coordinates changed because the code moved;
  function-name chain, final exception line, exit, stdout, plan bytes identical. Accepted; no
  traceback normalisation added.
- Five scratch records (`check` over the shipped plans BUG-1699, FEAT-1714, FEAT-61, FEAT-66): each
  carries a `plan-merge.py#<symbol>` anchor to a function now in the package, so the pin's `check`
  prints one more `FAIL … no definition or token` line (FEAT-66's exit 0→1). Identical tool logic
  on changed input; DEC-232 re-resolves at build entry and these shipped plans have none; re-pointing
  would reset four approvals. Accepted (option A); no anchor edited.

## SC-01
`feat70-grade-assert.py <pin> <baseline>` green at the pin (237 functions: 106 at 5, 131 at 4);
`--tree <baseline>` red (12 below 4; no package; the twelve not at their owners). Both outputs are
in the generated receipt.

## SC-03
`red-first-receipts.md`.
