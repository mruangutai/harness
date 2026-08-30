# Observations - harness-pm

- 2026-08-29: plan-merge.py REFUSES (exit 8) a proposal carrying an `approval:` mapping when the base
  plan.yaml does not exist — it treats an absent base as an empty mapping with no approval key, so
  any approval value "differs". Creating a brand-new plan.yaml must therefore use a direct write;
  the merge tool is for the second and later pm spawns. Skill text says "write it through the merge
  tool, never whole" without carving out creation.
- 2026-08-29: the dispatch told me to "confirm and plan for" test-gen-decisions-index.py using
  DEC-104's body as a fixture. It does not. The cited line is a COMMENT recording that the fixture
  was already removed when DEC-104 was struck, and the live assertion is a relationship not a frozen
  total. Reading the 20 lines around a cited line, rather than the line, cost 30 seconds and deleted
  a task from the plan.
- 2026-08-29: check-docs.sh does not exist in this tree, yet issue #78 rests two load-bearing claims
  on it (its stale-marker registry, and it exiting 0 as a verification). An old ticket's named script
  is worth an `ls` before any requirement is written against it.
- 2026-08-29: run-unit-tests.sh cross-checks every INTEGRATION_SCRIPTS name against harness.json's
  integration detect and exits 2 with KIND-DRIFT if absent. The two files are in DIFFERENT lanes
  (backend-dev, dev-ops), so registering a new test script is necessarily two tasks, and the config
  side must land first or the whole suite exits 2. The runner-side task's verify must assert the
  absence of the KIND-DRIFT string separately, because exit 2 is not a test failure.
- 2026-08-29: `check-domain.sh --resolve` run per path across 26 candidate paths took 2.3s and
  overturned the grilling's "entirely squad work" claim on 13 of them. Resolving every path the plan
  names, not a representative sample, is what produced the task split.
- 2026-08-29: FEAT-38 cycle 1. Every one of the 23 verify blocks passed the pre-change discrimination test (all exit non-zero), and that green is exactly what hid nine defects: an earlier conjunct exits first, so the generator and suite invocations at the END of nine blocks never ran. Discrimination proves the block reddens; it does NOT prove any conjunct past the first failing one was ever executed. To prove a trailing conjunct, build a tree where every earlier conjunct passes and run only the tail.
- 2026-08-29: FEAT-38. gen-decisions-index.py orphan detection (:302-316) makes 'generator --stdout || exit 1' UNSATISFIABLE for any task that deletes a DECISIONS.md entry before DECISIONS-INDEX.md is regenerated. Since the regenerating task transitively depends on the deleting tasks, no depends_on edge can fix it - the assertion itself has to be reshaped to expect the failure shape. Adding an edge was not an available remedy and I nearly reached for it first.
- 2026-08-29: FEAT-38. compute_tags scores tags from the RAW entry body, so an HTML comment inserted into a body re-scores its row tags, and any line-count change shifts every later row's @<line> anchor. Measured: two claim markers in DEC-181 changed 24 index rows. Any plan that regenerates a derived index mid-DAG must make the regenerating task depend on every task that writes the source file.
- 2026-08-29: FEAT-38 S7. Three signed verify blocks unsatisfiable while the WORK was correct. Two shapes: (a) a helper invoked with no argument exiting on its usage guard (check-expertise.sh, exit 2); (b) an absence-grep whose token appears in the PASSING labels of the test suite FOR that detector (6 bare 'KIND-DRIFT' hits, 0 anchored '^KIND-DRIFT:'). Third was window-dependent: the block REQUIRED a case to be RED that a later task in the same segment turns GREEN, so no exclusion-list fix alone could pass in both windows. Lesson: a verify that asserts a by-construction red is a time bomb; exclude, never require.
- 2026-08-29 (FEAT-38, SC-13 UAT): a receipt saying an amendment was "folded into DEC-137" did not mean the content survives — DEC-137 was itself deleted as a struck entry in an earlier task, so `grep '^## DEC-137 '` returns nothing. Verified the destination entry still EXISTS before writing that a folded claim is findable there; the fold receipt and the deletion receipt were two different tasks and neither cross-referenced the other.
- 2026-08-29 (FEAT-38): dispatch gloss ("one renumbered after a collision and two partly struck") was unsupported by any receipt; only the span collision was. Stated what the record supports and dropped the rest.
- 2026-08-29 (FEAT-38 goal-check at 48bbe7e): check-domain denied an Edit whose hash-line section header was a BARE filename — it resolved against cwd, not the file just read. Re-issuing with the absolute path in the header passed. Also: the prior goal-check's "Ten of the fifteen" over a twelve-id list was a word error, list right; 15-3=12.
- 2026-08-29: FEAT-38 S2 replan. check-plan-routes.py takes a FILE, not a feature dir: passed the dir it dies with IsADirectoryError at line 397 and exits 1, which reads as a gate failure rather than a bad argument. Pass plan.yaml.
- 2026-08-29: run-unit-tests.sh KIND-DRIFT is one-directional per kind (lines 121-130): an INTEGRATION_SCRIPTS name absent from detect is flagged, a detect entry with no array entry is not. That asymmetry decides deregistration ORDER (runner side first) and it is NOT the mirror-image of the registration reason.
- 2026-08-29: a done task whose product is being deleted has no legal status to say so (only pending/building/done). Turning its verify into a two-sided reversal check - product existed at the landed sha, absent at final state - makes it mechanically legible and keeps the record honest.
- 2026-08-29: FEAT-38 replan. A removal sequence's ordering rationale is only as good as its
  enumeration of the gates the INTERMEDIATE state trips. Two drafts of T-24/T-25 reasoned carefully
  about run-unit-tests.sh's KIND-DRIFT cross-check and never named the MISCONFIGURED file-presence
  detector 30 lines above it, which fires on any on-disk test-*.py in neither script array - so the
  three-step order took the whole suite to exit 2 for the interval. When I write an ordering
  argument, list every gate that reads the surfaces being changed, then say what each does in each
  intermediate state; a single-gate argument reads as rigorous and is not.
- 2026-08-29: FEAT-38. Merging two tasks is a plan-level remedy I own, and the cheapest form is to
  KEEP the id that other tasks already depend on (T-24) and retire the other (T-26), which made two
  of the three dependency edits no-ops. Check the id-reuse ledger first: renumbering was free here
  only because feature.json's github.attached stopped at T-23.
- 2026-08-29: FEAT-38. A generated file can be half hand-written. gen-decisions-index.py regenerates
  every field of a row EXCEPT the ruling right of " :: ", which it copies from the existing row. A
  task that says "do not hand-edit, it is generated" therefore forbids the only repair that works,
  and a diff-clean regeneration check passes over a false ruling. Ask which half of a generated
  artifact is derived before writing either the instruction or the gate.
