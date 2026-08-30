# Handoff — FEAT-43, ship → build

## Next

Run the **build phase**, beginning with T-01 in `plan.yaml`. T-07 may run independently alongside
T-01. T-09 is also dependency-free but is main-session-direct. Preserve the approved ordering:
T-04 precedes T-05, and T-08 follows T-03, T-05, T-06, and T-07.

Route T-04, T-05, T-08, and T-09 to the main session as recorded in `notes/handoff-plan.md`. Route
the remaining implementation work through the engineering lead. After all T-NN work passes, run
the QA matrix, SIMPLIFY, pin `review_sha`, and enter validate. Do not resume ship until validation,
the goal-check, and SC-11 UAT pass.

No operator question blocks this route: both approval gates are already signed.

## Trust

- The brief is approved — `.harness/harness/features/FEAT-43-code-risk-grading/BRIEF.md` — verified-at d169ad4
- The plan is approved — `.harness/harness/features/FEAT-43-code-risk-grading/plan.yaml` — verified-at d169ad4
- No build run is recorded; only `plan-product` exists and `review_sha` is `none` — `.harness/harness/features/FEAT-43-code-risk-grading/feature.json` — verified-at d169ad4
- The branch delta contains planning, research, state, observations, and logs but no implementation deliverable — `git diff --name-only origin/main...HEAD` — verified-at d169ad4
- The working tree was clean before the blocked ship artifacts were written — `git status --short` — verified-at d169ad4
- Planning passed after one rework cycle — `.harness/harness/features/FEAT-43-code-risk-grading/runs/plan-product/digest.md` — verified-at d169ad4
- The human-readable blocked ship assessment is complete — `.harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-ship-gate.md` — verified-at d169ad4

## Dead ends

- Do not request ship authorization now; build and validation have not run — `.harness/harness/features/FEAT-43-code-risk-grading/feature.json` — verified-at d169ad4
- Do not treat the approved draft skill in `notes/skill-draft-2026-08-27.md` as T-04 delivery — `.harness/harness/features/FEAT-43-code-risk-grading/notes/handoff-plan.md` — verified-at d169ad4
- Do not revive the planning digest's `.agents/**` missing-path finding; the operator handoff records the symlink-aware measurement that disproved it — `.harness/harness/features/FEAT-43-code-risk-grading/notes/handoff-plan.md` — verified-at d169ad4
- Do not create a PR, merge, deploy, move HEAD, or remove this worktree during build — `.harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-ship-gate.md` — verified-at d169ad4

## Working set

- `.harness/harness/features/FEAT-43-code-risk-grading/plan.yaml`
- `.harness/harness/features/FEAT-43-code-risk-grading/BRIEF.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/feature.json`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/handoff-plan.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-ship-gate.md`
