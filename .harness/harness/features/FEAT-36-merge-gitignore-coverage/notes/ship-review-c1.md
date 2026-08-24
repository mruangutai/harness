# Ship review — FEAT-36 merge-gitignore behavioral coverage

## Decision

**Ready for operator ship acceptance.** All six success criteria pass at `f494553bd9fbb987b4a19f91dcf4c3f37253fe38`, and the independent c2 panel passed with no must-fix. Ship-refresh is validly inapplicable. Product, engineering, and validator distillation are complete: two additive Expertise entries landed and passed the corpus checker; six unexpressible replacement ops are closed as unapplied/not permitted under the operator's explicit permitted-results contract.

No PR was created or merged, no issue was closed, no backlog item was filed, and the feature remains at `status: Review` rather than Done. The operator's available decisions are ship, fix, re-scope, or stop.

## Success criteria

| Criterion | Result | Declared verify | Evidence |
|---|---|---|---|
| SC-01 | PASS | automated / integration | `runs/goal-check-c1-product/digest.md` SC-01; pinned test `f494553:.agents/skills/harness/bin/test-merge-gitignore.py:9-23,36-47`; c2 QA direct and registered PASS |
| SC-02 | PASS | automated / integration | `runs/goal-check-c1-product/digest.md` SC-02; pinned test lines 50-73 separately prove exits 0/1, every missing rule, and byte identity |
| SC-03 | PASS | automated / integration | `runs/goal-check-c1-product/digest.md` SC-03; pinned test lines 76-98 separately prove absent and partial targets contain every rule exactly once |
| SC-04 | PASS | automated / integration | `runs/goal-check-c1-product/digest.md` SC-04; pinned test lines 101-110 compare complete-target bytes across the second merge |
| SC-05 | PASS | automated / integration | `runs/goal-check-c1-product/digest.md` SC-05; pinned test lines 113-126 prove requested-target creation and byte-identical preservation of a pre-existing caller `.gitignore`; `runs/review-c2-validator/digest.md` |
| SC-06 | PASS | inspection | `runs/goal-check-c1-product/digest.md` SC-06; pinned runner lines 17-18 and `.harness/harness.json:118-122` register integration coverage; base/pin `merge-gitignore.sh` SHA-256 is unchanged |

No criterion declares UAT, and no waiver was used.

## Validation

- Reviewed pin: `f494553bd9fbb987b4a19f91dcf4c3f37253fe38` (current HEAD when ship review began).
- `runs/review-c2-validator/digest.md`: PASS from code, QA, security, and UI; no must-fix.
- Matrix: 23 unit + 23 integration registrations, all 46 passing; changed behavioral program 7/7 directly and through registration; no `MISCONFIGURED` or kind drift.
- Earlier F-01/MF-01 is closed after the bytecode-disabled mutation-child correction and pinned rerun (`runs/review-fix-eng/digest.md`, `runs/review-c1-validator/digest.md`).
- The initial SC-05 evidence gap was fixed and re-gated, not waived (`runs/goal-check-product/digest.md`, `runs/goal-check-fix-eng/digest.md`, `runs/goal-check-fix-qa-validator/digest.md`).

## Close-out

The ship-refresh and feature-close distillation jobs were issued concurrently. Distillation was split into product, engineering, and validator squad-owned segments so no lead crossed squad boundaries.

| Workstream | Disposition | Affected gate |
|---|---|---|
| Ship-refresh | PASS / skipped: `.harness/codebase/` does not exist, so there is no map-domain intersection, stale section, or HTML map to render | Map render/check not applicable; `runs/ship-refresh-product/digest.md` |
| Product distillation | PASS: PM, documentor, and product lead accepted no ops; all candidates were absent or already covered | No Expertise file changed; `runs/distill-product/digest.md` |
| Engineering distillation | PASS after one receipt correction: no accepted op; the apparent merge-tool issue was a heading-less empty proposal, not a tool defect | No Expertise file changed; `runs/distill-eng/digest.md` |
| Validator distillation | PASS on c1 reassessment: security O-09 and UI G-11 remain applied and checked; code-reviewer P-04/P-06/G-13 and QA P-13/P-03/G-06 are individually closed as unapplied/not permitted | `check-expertise.sh .harness/expertise/` PASS with existing advisories only; `runs/distill-c1-validator/digest.md` supersedes the original blocking disposition without rewriting it |

The six replacements are not permitted results because harness-distill requires: “Apply through the merge tool. Never write the file yourself,” while the available merge tool supports lock-safe additive union only. Direct or whole-file replacement was not attempted. The stale code-reviewer P-06 wording and replace/drop capability gap remain recorded as non-gating close-out dispositions; neither creates a second backlog row. Observation logs remain archived; none existed and none was created or deleted.

## Budget

The feature records 18 runs against the informational 20-run threshold and 6 rework cycles against the hard 10-cycle cap. The run-budget tripwire was not crossed. The runs remained productive: they closed one mandatory matrix failure, one SC-05 evidence gap, and the close-out disposition conflict.

## Proposed backlog

| ID | Nature | Finding | Evidence | Proposed action |
|---|---|---|---|---|
| B-1 | chore | F-02: substring membership can accept a fabricated diagnostic superset such as `.claude/worktrees/NOT-THE-RULE` as naming the missing canonical rule | `.agents/skills/harness/bin/test-merge-gitignore.py:67-72`; `runs/review-c2-validator/digest.md` F-02 | In a later approved change, compare the exact emitted bullet-rule set with the expected missing-rule set |

This row is proposed only. It has not been filed through `gh-sync.py backlog`.

## Open questions

None.

## Source disclosure

No report round was spawned. This briefing was assembled directly from every feature run digest:

1. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/plan-product/digest.md`
2. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/plan-simplify-eng/digest.md`
3. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/t01-eng/digest.md`
4. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/qa-validator/digest.md`
5. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/simplify-eng/digest.md`
6. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-validator/digest.md`
7. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-fix-eng/digest.md`
8. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-c1-validator/digest.md`
9. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-product/digest.md`
10. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-fix-eng/digest.md`
11. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-fix-qa-validator/digest.md`
12. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-c2-validator/digest.md`
13. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-c1-product/digest.md`
14. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/ship-refresh-product/digest.md`
15. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/distill-product/digest.md`
16. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/distill-eng/digest.md`
17. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/distill-validator/digest.md`
18. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/distill-c1-validator/digest.md`
