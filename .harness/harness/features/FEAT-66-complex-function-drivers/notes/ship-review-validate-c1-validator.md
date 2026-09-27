# Ship review — FEAT-66 complex function drivers

FEAT-66 is ready for the operator's ship decision. Validation passed at review pin `b635ec5f61ee29bf280c99f5b6182520c99a0487`: the required unit and integration matrix is green, both signed perspectives are met, SC-01 through SC-04 are met, and all six validate-c0 findings are closed.

## Definition of done

| Perspective | Signed outcome | Verdict | Discharged by | Evidence |
|---|---|---|---|---|
| operator | I can rely on all existing enforcement outcomes and output bytes from the three evaluators remaining unchanged, with any divergence explicitly enumerated and ruled, and on reproducible evidence from the exact implementation pin rather than the working tree. | met | SC-02, SC-04 | `notes/research-FEAT-66-complex-function-drivers-goalcheck-validate-c1.md`; `notes/review-harness-qa-c1.md`; `notes/clean-pin-byte-receipts.md`; `notes/build-divergences.md` D-09 |
| code maintainer | I can change or review one rule without traversing a grade-1 monolith: each of the three named functions is a small driver over ordered per-rule functions, and every function produced or retained by this refactor meets the production code-grade bar except the grader's grade-2 exception. The comments that explain each rule remain byte-for-byte with that rule. | met | SC-01, SC-03 | `notes/research-FEAT-66-complex-function-drivers-goalcheck-validate-c1.md`; `notes/review-harness-code-reviewer-c1.md`; `notes/red-first-receipts.md` |

## Run record

No report round was spawned. This briefing was assembled from the durable run digests:

- `runs/patch-product/digest.md`
- `runs/build-main-direct/digest.md`
- `runs/validate-validator/digest.md`
- `runs/fix-c0-main-direct/digest.md`
- `runs/validate-c1-validator/digest.md`

The patch run produced the approved one-task direct-execution plan. The build run decomposed `shape_problems`, `validate`, and `apply_merge` into graded drivers and per-rule helpers while preserving the owning suites' outcomes. Validate c0 found six defects in evidence, plan conformance, and matrix configuration. The operator ruled the three scope/acceptance questions in `notes/answers-validate-validator.md`; fix c0 closed MF-01 through MF-06 without changing production bytes. Validate c1 independently re-graded those repairs with QA, code, security, UI, and PM readers and returned PASS with no finding.

## Verification and risk

- Review pin: `b635ec5f61ee29bf280c99f5b6182520c99a0487`.
- QA: `cross_module` requires unit and integration; 42 unit files and 70 integration files passed in an exact-pin detached checkout.
- Fail-first: SC-01's plan-inline assertion fails at baseline `35c39f02` with all three drivers at grade 1 and passes at implementation pin `f882dc3e`; SC-02 uses the operator-approved baseline-comparison equivalent.
- Code review: 91 changed or new function records pass the production grade bar; the exact three-file production boundary, rule/output order, and load-bearing comments are preserved.
- Security: enforcement boundaries were inspected and no security finding survived.
- UI: correctly scoped out; the pinned diff has no rendered surface.
- UAT: not required; all success criteria are automated or inspection-based and the change has no user-facing surface.

## Resolved escalations and open questions

All validate-c0 escalations are resolved: D-09 records and rules the three checkout-root-only output lines; D-02 is amended to the built fold shape; the second permanent grade lock and stale exemption are removed; BRIEF records SC-02's approved fail-first equivalent; and T-01 uses `change_type: cross_module`. There are no open questions.

## Spend and ledger

The feature used 5 recorded runs, 1 of 10 allowed rework cycles, 110 wall-clock minutes, and 287,658 measured agent tokens. Rework used 39 of the operator-approved 90 minutes and 1 of 2 rounds. The ledger contains 8 judgements. The informational run budget is 20, so it was not crossed.

## Amendments to signed task text

| At | Decision | Reason | Overruled |
|---|---|---|---|
| `2026-09-26T15:09:41.830185+00:00` | `T-01.files` | The shadows suite existed only untracked in the operator's main checkout and was on neither origin/main nor this branch. | no |
| `2026-09-26T15:09:41.830349+00:00` | `T-01.verify` | The shadows suite existed only untracked in the operator's main checkout and was on neither origin/main nor this branch. | no |

Overrule rate: 0/2.

## Proposed backlog

| ID | Nature | Residual |
|---|---|---|
| B-1 | chore | Derive the pre-existing `SHAPE_PATTERNS` constant from `SHAPE_RULES`; this is outside SC-03 and was intentionally not included in FEAT-66. |
| B-2 | chore | Replace `check-state._inv15_digest_verdict`'s hand-rolled `_return_tail` behavior and moved validate-digest line citations in a separately scoped change. |

These rows do not gate FEAT-66. Unstruck rows become backlog issues only if the operator accepts ship.