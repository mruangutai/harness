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
