# STATE

## Current

- feature: BUG-1286-test-tree-enforcement
- run: eng segment T-01/T-02/T-03 in flight
- squad: eng
- status: building

Build phase entered 2026-09-05 at 5eebad66. BRIEF `## Approval` and plan.yaml `approval.status`
both read `approved` (mruangutai, 2026-09-05), verified by reading both files. `gh-sync.py open`
created milestone #44, parent #1295 and sub-issues #1296..#1300 (T-01..T-05); plan.yaml feature
station and T-01/T-02/T-03 task stations are `building`, and `start-task` moved those three cards.

Baseline captured before any edit, at 5eebad66 with a clean worktree: `run-unit-tests.sh --kind unit`
exits 0 with 316 PASS lines, 0 FAIL, 27 files. `check-state.sh` reports no violation and no note for
this feature.

Cycle budget is the binding constraint: `cycles_used: 9` of `max_total_cycles: 10`. Exactly ONE
rework cycle remains for the whole rest of the feature, so every segment is dispatched to land
first-pass. `len(runs)` is 29 against an informational `max_total_runs: 20` — INV-22 notes it and
never stops a branch.

## Open Questions

- Five cycle-10 panel findings ride into build, all `disposition: open`, none gating. The med one,
  PF-7f5eff475a69a7db20cc8293d4b6e9f7, says condition (b)'s NON-DEGENERATE conjunct requires a
  wildcard in the core and so trips fail-closed on a fully literal core such as `**/test_foo.py`.
  The operator signed the plan with these carried; they are not a build-phase fix mandate.
- The honest limit T-01 must close: every green/red result on record is a hand-simulation of the
  SPECIFICATION against reader-written reimplementations. T-01 case 11's four red cases must be
  re-proved against the BUILT artifact.
- Harness defect surfaced at plan time: `validate-digest.py` requires `code_grade` on a code-reviewer
  digest and rejects every value while `feature.json` reads `review_sha: none`, so a plan-phase panel
  reader that did its job settles as `failed`. Not this feature's scope; carried to the briefing.
