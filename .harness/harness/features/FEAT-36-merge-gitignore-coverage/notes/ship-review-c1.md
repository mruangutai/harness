# Ship review — FEAT-36 merge-gitignore behavioral coverage

## Decision

**Ready for operator PR acceptance.** All six success criteria pass at `be27d99454352e581fdf7cbace20fb52d0f45133`, and the independent c3 panel passed with no must-fix. The operator-requested B-1 diagnostic-set weakness is closed with discriminating mutant evidence. Ship-refresh was inapplicable; close-out distillation remains complete.

No PR was created or merged, no issue was closed, and the feature remains at `status: Review`. The operator may create the stacked PR, fix the unrelated renderer follow-up, or stop.

## Success criteria

| Criterion | Result | Declared verify | Evidence |
|---|---|---|---|
| SC-01 | PASS | automated / integration | `runs/goal-check-c2-product/digest.md` SC-01; c3 QA direct and registered PASS |
| SC-02 | PASS | automated / integration | `runs/goal-check-c2-product/digest.md` SC-02; exact emitted bullet-set equality rejects missing and unexpected values, including the controlled fabricated-superset mutant |
| SC-03 | PASS | automated / integration | `runs/goal-check-c2-product/digest.md` SC-03; absent and partial targets contain every rule exactly once |
| SC-04 | PASS | automated / integration | `runs/goal-check-c2-product/digest.md` SC-04; second merge is byte-identical |
| SC-05 | PASS | automated / integration | `runs/goal-check-c2-product/digest.md` SC-05; explicit project root changes only the requested target |
| SC-06 | PASS | inspection | `runs/goal-check-c2-product/digest.md` SC-06; integration registration is correct and `merge-gitignore.sh` remains byte-identical |

No criterion declares UAT, and no waiver was used.

## Validation

- Reviewed pin: `be27d99454352e581fdf7cbace20fb52d0f45133`.
- `runs/review-c3-validator/digest.md`: PASS from code, QA, security, and UI; no must-fix.
- Matrix: 23 unit + 23 integration registrations, all 46 passing; changed behavioral program 7/7 directly and through registration; no `MISCONFIGURED` or kind drift.
- B-1/F-02 is closed by exact-set comparison and a controlled mutant that reports `.claude/worktrees/NOT-THE-RULE` as unexpected.
- The generated ship-review HTML contrast finding was ruled unrelated to FEAT-36 and did not waive or substitute for any approved success criterion (`notes/operator-ruling-rendered-review-scope.md`).

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

The feature records 24 completed runs against the informational 20-run threshold and 7 rework cycles against the hard 10-cycle cap. The informational run tripwire was crossed. The extra runs closed a mandatory matrix failure, the SC-05 evidence gap, B-1's exact-diagnostic weakness, and the scope dispute without crossing the hard cycle cap.

## Proposed backlog

| ID | Nature | Finding | Evidence | Proposed action |
|---|---|---|---|---|
| B-2 | chore | The shared briefing renderer's pre-existing light-theme quiet-text token is below the normal-text contrast floor in generated ship-review HTML | `notes/operator-ruling-rendered-review-scope.md`; `runs/review-b1-validator/digest.md` UI-A11Y-01 | Address separately from FEAT-36; do not couple renderer changes to shell-utility coverage |

This row is proposed only. B-1 was fixed in this cycle; no backlog issue has been filed.

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
19. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/fix-b1-eng/digest.md`
20. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/fix-b1-qa-validator/digest.md`
21. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/fix-b1-simplify-eng/digest.md`
22. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-b1-validator/digest.md`
23. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/review-c3-validator/digest.md`
24. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/goal-check-c2-product/digest.md`
