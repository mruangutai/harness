# Observations — harness-pm — FEAT-13-single-issue-board-lookup

- 2026-08-10: check-plan-routes.py's module docstring and TASK_RE still describe the PLAN.md
  markdown path only, which reads as if the checker no-ops on plan.yaml. It does not: both the
  working-tree copy and origin/main carry process_plan_yaml (main-cpr.py:299/375), and running it
  on FEAT-12's plan.yaml reported 14 tasks. Do not spend a second pass re-deriving this — the
  stale docstring is the only misleading part.
- 2026-08-10: run-unit-tests.sh --kind integration takes 63s wall on this machine, over the 60s
  verify bar; test-factory-integration.py alone takes 6.2s and runs correctly from the repo root
  (Python puts the script's dir on sys.path). Name the single file in a verify, not the kind.
- 2026-08-10: the dispatch named c633bbd as the checkout; HEAD had already moved to bbfc9bb (a
  grilling commit touching only .harness/logs and .harness/notes). Ran git rev-parse rather than
  trusting the dispatch, and recorded lanes.resolved_at as the tree actually resolved against.
- 2026-08-10: the grilling note and issue #217's body record DIFFERENT board item ids for issue
  #216 (PVTI_lAHOAAases4Bf5NHzg15... elided, vs PVTI_lAHOAAases4BfZ9Zzg2AMPA), both claiming to be
  what project item-add returned. Prose anchors from two artifacts agreeing on the CLAIM is not
  the same as agreeing on the VALUE; derive the comparison target live instead.
- 2026-08-10: the eng review's own deletion anchor was wrong in the same way my plan's was. The
  _item_repo comment block runs 271-279 with rule lines at both ends; my plan said delete 277-280
  and eng said the block is 271-279. Both were line numbers into a file the same task edits twice.
  Rewrote step 2 entirely as quoted sentence fragments with keep/rewrite/delete verdicts. When two
  steps of one task edit the same file, line anchors are unusable by construction, not merely
  fragile — the second editor works against a file the first already moved.
- 2026-08-10: a raise clause added to a plan without a matching test bullet reproduces the exact
  defect the review found (F1: an enumerated rule nothing asserts). Accepting F7 meant adding both
  halves; I nearly added only the clause. Rule: a raise condition and its assertion are one edit.
- 2026-08-10: pinning a call's argument tuple is worthless if the fixture uses the same value in
  both slots. land's mis-wire is board-owner vs "owner/name" repo string, and the integration
  fixture uses owner "acme" with a repo string that shares no prefix — but a unit fixture could
  easily use the same login for both and the assertion would pass under the mis-wire. Wrote the
  discriminating-fixture requirement into the task rather than trusting the builder to notice.
- 2026-08-10: an eng review can leave the blast radius of its own finding under-stated. F3 was
  filed as "one sentence in plan.yaml" but the sentence it falsifies lives in BRIEF.md's Goal.
  A behaviour delta recorded only in the plan leaves the brief asserting the opposite, and the
  brief is what the operator reads at signature. Check every accepted delta against the Goal text.
- 2026-08-10 (goal-check): the `argv[:2]` slice I wrote at plan.yaml:368 can never match, because
  run_gh (factory_gh.py:88) builds [gh] + list(args). The adjacent line :367 already used the
  right `argv[1:3]` form, so one plan step carried both. Two lines of the same prose block
  disagreeing is invisible on reading — it shows only when someone runs the clause. Check every
  argv-slice literal in a plan against the actual arg-builder before shipping the step.
- 2026-08-10 (goal-check): SC-05 named a state ("an issue whose state is closed") that neither
  test double can represent — decompose's Recorder returns item_by_issue.get(number)
  unconditionally (test-factory-decompose.py:123-125), and the integration stub keys on a
  query-text token then answers from its own state dict. Both are state-blind by construction, so
  making either state-aware would test the fake. When an SC's distinguishing condition lives in a
  string the code SENDS rather than in an argument the fake SEES, the only non-vacuous evidence is
  an assertion on that string. At plan time ask where the condition is observable, not merely
  whether a test kind exists.
