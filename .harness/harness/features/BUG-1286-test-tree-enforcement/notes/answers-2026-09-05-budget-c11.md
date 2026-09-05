# Operator answer — rework budget

- feature: BUG-1286-test-tree-enforcement
- date: 2026-09-05
- question: Validation reached the 10/10 rework budget with B-1, B-2, and B-3 outstanding.
- answer: Raise `max_total_cycles` from 10 to 11 and use the additional cycle to fix all three required remedies, then revalidate.
- authority: mruangutai, selected “Raise budget by one cycle” in the main session.
- limits: This authorizes one additional rework cycle only. It does not authorize risk acceptance, scope changes, merge, or worktree removal.
