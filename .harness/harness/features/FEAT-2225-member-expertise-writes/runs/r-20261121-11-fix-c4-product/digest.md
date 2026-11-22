# C4-F1 fixed; literal diff-stat acceptance fails

Fix commit **8257a2e02d84a1fb32f91b24d645cd9404bf092e** regenerates only DEC-253's tags. Final receipt-only commit: **1abacbffa07493b53a1aa879101c5e97c25251d0**.

Documentor PASS: T-02 comparison and named integration command each exited **1 before / 0 after**. Receipt preserves `236c236` and the actual one-line index diff. Lead read both and the resulting index row 236, which now carries `[expertise,dispatch,state,worktree]`. No lead checks rerun.

Lead FAIL: receipt reports `git diff --stat` additionally names pre-existing feature.json and plan.yaml modifications. These were not made or committed by documentor, but the assignment explicitly makes any other changed path a run failure. No unrelated bookkeeping was reverted. Orchestrator must reconcile its bookkeeping/scope gate; no further index edit is needed.

Member artifact: ../../notes/receipt-harness-documentor-fix-c4.md. Deliverables: `.harness/harness/docs/DECISIONS-INDEX.md` and that receipt only. No push, gh, additional tests, or review pin change. Open questions: none.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "8257a2e02d84a1fb32f91b24d645cd9404bf092e fixes C4-F1; both gates 1\u2192\
    0, but literal diff-stat scope gate fails on pre-existing bookkeeping."
  open_questions: []
  files_touched:
  - .harness/harness/docs/DECISIONS-INDEX.md
  - .harness/harness/features/FEAT-2225-member-expertise-writes/notes/receipt-harness-documentor-fix-c4.md
  expertise_update: []
  team: fix
  steps_run: 1
  cycles_used: 0
  members:
  - step: T-02
    persona: harness-documentor
    verdict: PASS
    headline: Regenerated DEC-253 index tags; comparison and integration exits before
      1/1, after 0/0; fix 8257a2e02d84a1fb32f91b24d645cd9404bf092e.
    files_touched:
    - .harness/harness/docs/DECISIONS-INDEX.md
  must_fix:
  - 'Reconcile literal diff-stat scope acceptance: receipt reports pre-existing feature.json
    and plan.yaml changes, untouched and unstaged by documentor.'
  branch: feat/FEAT-2225-member-expertise-writes
  escalations: []
  adequacy_notes:
  - Lead read receipt, actual index diff, and corrected row 236; C4-F1 repair is complete.
  - 'T-02 verify: before exit 1, after exit 0. Named integration command: before exit
    1, after exit 0 (12 cases pass). No additional tests run.'
  - 'Final receipt-only commit: 1abacbffa07493b53a1aa879101c5e97c25251d0. Both commits
    confined to index and receipt.'
  - Scope failure concerns pre-existing orchestrator bookkeeping, not unauthorized
    documentor changes; unrelated changes were preserved.
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-11-fix-c4-product/digest.md
```
