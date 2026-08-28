# Handoff — FEAT-43 build complete; validation next

## Next

Continue with the **validation phase** for `FEAT-43-code-risk-grading`; do not resume build tasks.
Every signed task T-01 through T-10 is `done` in `plan.yaml`. The immutable review target is
`1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`, recorded in `feature.json.review_sha`.

Before dispatching the review panel, the validation orchestrator must:
1. Re-read `STATE.md`, `feature.json`, the validation-relevant BRIEF success criteria, and the
   pinned plan decisions.
2. Confirm the pin remains `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`; if any source commit is
   added, re-pin before review rather than reviewing the inherited SHA.
3. Read `.agents/skills/harness/references/github-mirror.md` and run the orchestrator-owned
   `gh-sync.py status <feature-dir> Review` sync point. Build intentionally did not perform it.
4. Dispatch the validator review panel against the pinned SHA and complete validator fix loops in
   the validation mission. Do not run goal-check, UAT, ship, merge, or deploy from this handoff.

The complete feature implementation, T-08 cutover, and eligible SIMPLIFY apply are contained in the
pin. Build metadata (`STATE.md`, `feature.json`, and this superseding handoff) is intentionally the
only working-tree delta after the pin; it records the boundary rather than changing reviewed code.

## Trust

- All signed plan tasks T-01 through T-10 are done — `plan.yaml:112-620` — verified-at `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`.
- T-08 teaches grade-1/high and grade-2/med findings, requires `code_grade`, and delegates policy to `gate_policy` — `.claude/skills/harness-code-review/SKILL.md`, `.claude/skills/harness/bin/validate-digest.py`, and `.claude/skills/harness/bin/test-validate-digest.py` — verified-at `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`.
- T-08's previous-revision and policy-discrimination cases passed in the reported all-suite verifier — main-session T-08 evidence in the assignment plus the committed tests — verified-at `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`.
- QA coverage inspection found direct tests for grading, CLI, gate policy, digest policy, and owner-route resolution — `notes/qa-build-qa.md` — verified-at `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`.
- QA's first runner BLOCKED result is preserved rather than rewritten — `runs/build-qa-validator/digest.md` — verified-at working tree after `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`.
- The measured blocker was interpreter selection: `/usr/bin/python3` 3.9.6 rejected `-P`; Homebrew Python 3.14.5 accepted it — `notes/qa-build-qa-rerun.md` — verified-at `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`.
- Configured QA passed unit 29/29 and integration 28/28 with nonzero named discovery — `runs/build-qa-validator-rerun/digest.md` — verified-at working tree after `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`.
- SIMPLIFY ran REUSE, SIMPLIFICATION, EFFICIENCY, and ALTITUDE as four independent readers — `runs/build-simplify-eng/digest.md` — verified-at working tree before `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`.
- SIMPLIFY applied only the eligible removal of a second head-file fetch/AST grading traversal and weakened no assertion — `notes/receipt-harness-backend-dev-simplify-apply.md` — verified-at `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`.
- Post-apply gates passed unit 29/29 and integration 28/28 with zero corrective fixes — `runs/build-simplify-eng/digest.md` — verified-at working tree before `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`.
- `review_sha` contains all reviewed feature source and generated adapter changes — commit `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c` — verified-at `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`.

## Dead ends

- Do not restore direct reads of the retired project-root environment variable; T-08 deliberately uses `harness_boundary.resolve_root`.
- Do not treat the first QA BLOCKED run as a source defect; the rerun measured and corrected interpreter selection without changing the configured commands.
- Do not rerun build QA or SIMPLIFY merely to reconfirm their evidence; rerun only if validation lands a new source commit and then re-pin.
- Do not weaken grade findings, the reviewer `code_grade` contract, gate-policy enforcement, previous-revision discrimination, or the no-distribution invariant.
- Do not review the dirty working tree; review the pinned commit.
- Do not move HEAD, merge, deploy, perform goal-check, run UAT, or ship from the build handoff.

## Working set

- `.harness/harness/features/FEAT-43-code-risk-grading/feature.json`
- `.harness/harness/features/FEAT-43-code-risk-grading/STATE.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/plan.yaml`
- `.harness/harness/features/FEAT-43-code-risk-grading/runs/build-qa-validator-rerun/digest.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/runs/build-simplify-eng/digest.md`
