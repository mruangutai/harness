# Observations - harness-dev-ops

- 2026-08-23: FEAT-33 c2 dispatch quoted the suite baseline as "46 script-level PASS lines, 812 assertion PASS lines"; measured on HEAD, 812 is the TOTAL ^PASS count and INCLUDES the 46 script-level lines. The number was right, its label was wrong — re-measuring the baseline after reverting my own files was the only way to report a truthful delta (+10 = 11 added, 1 inverted).
- 2026-08-23: FEAT-33 c2: writing the new tests FIRST against a clean working tree made the RED proof free — no cp/git-show pinning needed for it, since the working tree WAS HEAD. The pinned-restore dance was still needed, but only to measure the full-suite baseline counts.
- 2026-08-23 (c3): a brand-new GitHub Projects v2 project is NOT empty — it ships a `Status`
  single-select with Todo / In Progress / Done plus ~12 plain ProjectV2Fields (measured live on
  project 7, mruangutai). c2's "empty by construction" comment was written from inference and a
  live run falsified it on first contact; only the live run could tell, because every fake in
  test-board-lifecycle.py answers the probe from a fixture the test author chose.
- 2026-08-23 (c3): the working-tree fleet.yaml carries two repos, so
  test-no-distribution.py's case3_presence_fleet_has_exactly_one_repo fails at HEAD+c2 — the
  fleet's size is hard-coded in that test, so adding the harness-factory-smoke fixture repo
  reddens it. Raised as an open question rather than fixed (fleet.yaml is dispatch-forbidden).
- 2026-08-23 (c4): a review-supplied mutant can be uncompilable rather than silent -- `created["number"]` -> `number` inside `_fresh_board_station_field` is a NameError (no `number` param), so it reddened 18 checks, not 0. Had to construct a third mutant (thread the declared number in as a new param, mutate the READ sites only, leave every message on `created["number"]`) to get a genuinely silent one. Its pass count landing on exactly the pre-fix baseline (138) is what proved the old suite was fully green under it.
- 2026-08-23 (c4): `except BaseException` added around a block whose own helper calls `sys.exit()` needs `except SystemExit: raise` FIRST -- otherwise the intended exit gets re-wrapped as an unexpected failure and the precise refusal message is lost.
- 2026-08-23 (c4): a fake CLI's argv log can already contain the evidence an assertion needs -- checked before adding a recording mechanism the reviewer asked for, and it was there. Also: a nonzero-exit lever (FAIL_MATCH) cannot produce a non-GhError; only exit-0-with-unparseable-body reaches the json.loads ValueError, so a new lever was genuinely required.
- 2026-08-23 (c4): the GhError-only catch defect existed in TWO post-create blocks; fixing only the dispatched one would have left the docstring claim false at a different line. Checked the sibling block before believing the corrected prose.
