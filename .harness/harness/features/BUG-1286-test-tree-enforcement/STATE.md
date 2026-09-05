# STATE

## Current

- feature: BUG-1286-test-tree-enforcement
- run: 2026-09-05-09-validator (panel, PASS) and 2026-09-05-03-product (goal-check, PASS)
- squad: none
- status: awaiting_user

At the ship gate, every gate green. Not merged, no PR, the worktree stands. `review_sha` is pinned
at `bb3a31edc1971447b998fda1f9a736944bc8e612`; the plan's feature station is `review` and all five
task stations are `done`. `gates.merge` is `user_gated`, so the merge and the worktree removal are
the main session's acts, not the orchestrator's.

The operator authorised ONE additional rework cycle (`notes/answers-2026-09-05-budget-c11.md`,
mruangutai, 2026-09-05) to close B-1, B-2 and B-3, explicitly withholding risk acceptance, scope
change, merge and worktree removal. All three landed in `bb3a31ed` and the branch revalidated:

- Reviewer panel PASS, `must_fix` empty, `severity_max: med`, all four lenses ran.
- pm goal-check **19 of 19 SC MET**, every cycle-1 MET re-derived from scratch at the new pin.
- `code-grade.py` exit 0, zero high-severity records; two grade-2 med records remain
  (`tracked_paths`, `_literal_key_present`), both backlogged and non-gating.
- unit 342 PASS / 0 FAIL / 27 files; integration 14/0; `--check-layout` exit 0; tree-audit
  `TOTAL 85 OUTSIDE 9 VIOLATIONS 0` with the note round-trip at exit 0; anchors 30/0;
  `check-state.sh` exit 0 with nothing for this feature.

All figures re-measured by the orchestrator at the pinned revision rather than relayed. B-1's
decomposition was confirmed byte- and order-identical in output, and the panel drove D-03's
ordering constraint live against a real nested-checkout fixture for the first time in this
feature's history, confirming it fails CLOSED — the one way the refactor could have fail-opened.

`cycles_used` is 11 of 11 — exactly the authorised cycle, no more. `runs` is 41 against an
informational `max_total_runs: 20`; INV-22 notes it and never gates. Zero send-backs were reported
across the eight runs of the fix and revalidation.

The briefing is `notes/ship-review-2026-09-05-ship-final.md`, rendered to `.html`, carrying twelve
backlog rows B-4 through B-15. The earlier blocked briefing survives at
`notes/ship-review-2026-09-05-ship.md` as the record that justified the cycle.

## Open Questions

- For the operator: merge or not. That is the only decision left; every gate is green.
- Record hygiene, non-blocking: `runs/2026-09-05-02-validator/digest.md` fails the lead digest
  contract (no `artifact:`). Gitignored, absent from the reviewed tree, covered by no SC, and
  superseded by the `-03` record. pm also reported `check-state.sh` exiting 1 where the
  orchestrator measured 0 twice, before and after; the disagreement is reported rather than
  resolved. Backlog B-11.
- Harness defect found independently by two readers, backlog B-13: the integration suite is not
  hermetic against `HARNESS_AGENT_TYPE` — 15 FAIL lines under an agent's own env, green for a
  human, reproduced unchanged at the merge-base. Agents have been grading a red suite as evidence.
- Carried harness defects: `validate-digest.py`'s `code_grade` deadlock for plan-phase readers
  (B-9); members editing the MAIN checkout through bare relative paths under a worktree dispatch,
  twice, both reverted (B-10); `max_total_cycles` having no mechanical check and no definition of
  "exhausts" (B-12).
