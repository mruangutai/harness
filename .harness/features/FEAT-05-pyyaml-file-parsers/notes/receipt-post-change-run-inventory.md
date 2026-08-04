# Receipt — SC-13's POST-change run inventory — 2026-08-03

**The second of the two listings SC-13 requires.** The panel's Q1 found only the baseline existed
(`receipt-baseline-run-inventory.md`), so the criterion could not be evaluated at all — a comparison
needs both sides. This is the missing half, produced after F-02.

## Why SC-13 exists at all, restated because it is the subtle one

SC-02 asks that `check-state.sh` still exits 0 with zero violations. **That is exactly what a
silently dropped run also produces.** Issue #11's defect was invisible precisely because the gate
stayed green while INV-6/7/8 checked nothing. So only an inventory comparison distinguishes
"nothing fired" from "nothing was checked".

## Post-change inventory, parsed by the converted `check-state.sh` logic

| feature | runs parsed | runs declared | |
|---|---|---|---|
| FEAT-01 | 1 | 1 | OK |
| FEAT-02 | 4 | 4 | OK |
| FEAT-03-subissue-mirror | 19 | 19 | OK |
| FEAT-04-decisions-index | 15 | 15 | OK |
| FEAT-05-pyyaml-file-parsers | 4 | 4 | OK |
| **TOTAL** | **43** | **43** | **no run dropped** |

`parsed` counts entries `harness_yaml.load_file` yields and the invariants actually consume;
`declared` counts entries present in `runs:`. Equality per feature is the claim.

## Against the baseline

The baseline receipt recorded `parsed == declared` for all five features at 1/1, 4/4, 19/19, 15/15
and 3/3 — 42 runs. **The only difference is FEAT-05's own count, 3 → 4**, because the validator
panel run was recorded after the baseline was taken. Every pre-existing run is still parsed, and
no id changed.

**SC-13 is MET**: same features, same ids, and the one count that moved is a run this feature
itself added.

## SC-02, re-measured at the same state

`check-state.sh` — **exit 0, 0 violations, 40 notes**, all INV-8 "run dir absent (pruned)". Matches
the criterion's stated baseline shape. The note count differs from the baseline's 39 by exactly the
one new FEAT-05 run, consistent with the inventory above.

## Q1's second half, answered

The panel asked whether F-02's fix invalidates SC-02/SC-13, since those criteria compare against
pre-change output and the conversion turned out not to be faithful.

**It does not, and the reasoning is worth keeping:** F-02 changed which invariants FIRE (INV-11 and
INV-15 now catch a quoted `status:` that used to slip past), not which runs are SEEN. SC-13 is about
the run inventory, and that is unchanged — 43 parsed, 43 declared, ids identical. A criterion about
coverage is not disturbed by a fix that adds detection.

The one thing that WOULD have invalidated it is fixing issue #16 (`review_sha: none` is truthy)
inside this change, because that alters INV-6's output on the very features being compared. It was
deliberately deferred for exactly that reason (D-09), and this receipt is the evidence that the
deferral bought what it was meant to buy.
