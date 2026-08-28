# STATE

## Current

- feature: FEAT-43-code-risk-grading
- run: .harness/harness/features/FEAT-43-code-risk-grading/runs/plan-product/digest.md
- squad: product
- status: awaiting-user

BRIEF.md and plan.yaml are written and both read `pending`. The plan phase ends here, at the
signature gate. 10 tasks (T-01..T-10), 20 success criteria, 1 rework cycle spent. Four tasks are
main-session-direct (T-04, T-05, T-08, T-09) because their paths resolve to NOBODY or sit in the
DEC-174 enforcement layer. Nothing is built.

## Open Questions

- Q1 (blocking): the operator must approve BRIEF.md and plan.yaml. One signature, both artifacts.
- Q2 (non-blocking): the product-lead's digest reports a `high` finding that `.agents/**` does not
  exist and both active test-kind `cmd` paths in harness.json are dead. I measured the opposite and
  the finding is FALSE — `.agents/skills` is a symlink to `../.claude/skills`, and the exact cmd
  string runs from the repo root with the unit suite passing 18/18, exit 0. No fix is needed and
  T-03 must NOT absorb one. Root cause is a symlink-blind search tool, which is a harness defect.
- Q3 (non-blocking): the SubagentStop hook named `harness-validator-lead` as my child in flight. I
  never dispatched one. Cause unknown; two candidates, evidence for neither.
