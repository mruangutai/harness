# Observations — harness-pm — FEAT-28

- 2026-08-19: TWO pm runs wrote this feature's BRIEF.md and plan.yaml concurrently. I wrote a
  Route A design (dedicated bin/test-ci-wiring.py) at ~06:2x; a second run overwrote both files
  with a Route B design (case_26 family inside test-check-plan-routes.py) at 06:29-06:31. My
  follow-up in-place patch then spliced my SC block into their BRIEF, leaving it internally
  contradictory for a few minutes. Nothing in the feature dir detects a concurrent author; the
  Write tool has no compare-and-swap. Resolved by adopting the surviving plan.yaml and rewriting
  the SC block to match it.
- 2026-08-19: the surviving plan's REQ-02 named FIVE failure-forcing behaviours but its case list
  enumerated only four mutants; the missing-examined branch had no case. Caught by grading the
  REQ against the case list rather than the case list against itself.

- 2026-08-19 (stray spawn S-99, prompt was the literal string `placeholder`): I oriented from
  `runs/*/state.yaml` and the orchestrator's notes rather than from a dispatch, found the sibling
  pm's artifacts already on disk, and chose to audit instead of write. The step status in
  `runs/2026-08-19-01-product/state.yaml` (`S-01-pm-plan: in_flight`) is what settled it —
  file mtimes cannot tell "mid-write" from "just finished", a step status can.
- 2026-08-19: I recorded T-01's verify as red-by-construction, then ran the phantom resolver's own
  logic and found it green: `case_25b9` truncates to `case_25`, which has a real `def`, so the
  resolver resolves the phantom it exists to catch. My finding was wrong AND the plan's assertion
  is unmeetable — running the specified logic, not reasoning about it, produced both facts at once.

- 2026-08-19 (fix cycle 2, S-02): `test-check-plan-routes.py` defines ONE function per case family
  (`def case_25()`) and calls `check("<full_label>", ...)` once per sub-case. Sub-case ids such as
  `case_19a3b` therefore exist ONLY as `check(` string labels — there is no `def case_19a3b` and
  never will be. An id-resolution rule written against `def` names alone reports every real
  sub-case citation as a phantom. Measured at `061acbb`: `tests.yml` cites exactly two ids,
  `case_25b9` (line 44, unresolvable) and `case_19a3b` (line 177, resolves at
  `test-check-plan-routes.py:366`).
- 2026-08-19: a mutation-proof case must INJECT an id absent from the real text, never replace one
  the text already carries — otherwise the scan reports it whether or not the mutation did
  anything, and the case also breaks the moment a downstream task removes that id. Chose
  `case_25zz9`: absent from the tree, but its base `case_25` resolves, so it is red only under the
  fixed full-identifier rule.
- 2026-08-19: `git diff --exit-code` inverts meaning between a task that must NOT touch a file (a
  real assertion) and one that MUST (always fails on a correct task). For a generated file the
  criterion is idempotence: copy aside, regenerate, `diff -q`.
- 2026-08-19: an SC can silently encode the implementation it is meant to grade. SC-05 said
  "resolves to no `def case_NN`" — the exact truncating, def-only rule the fix removes — so the
  broken implementation satisfied its own criterion. Grade every SC's text against the change
  before assuming only the plan needs editing.
