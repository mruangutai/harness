# Observations — harness-pm — FEAT-06

- 2026-08-04: send-back on T-02. I wrote `mutates_repo: true` for the new qa step in
  `review.yaml` reasoning "qa writes tests", but in that file the flag means serialize-the-dispatch,
  and all three existing review steps write `outputs:` notes at `mutates_repo: false`. The recorded
  run `.harness/features/FEAT-03-subissue-mirror/runs/2026-07-31-12-validator/state.yaml` shows
  code(:26)/security(:35)/qa(:43) all at `dispatched_at: seq-1` — parallel. Shipping `true` would
  have made `review.yaml` contradict `SPEC.md:1980`'s `{code ∥ qa ∥ security ∥ ui}` — the exact
  definition-vs-definition contradiction this feature exists to close. The recorded run outranked
  my inference about the persona's general behaviour.
- 2026-08-04: three anchors I carried from BRIEF into PLAN and SC cited `SPEC.md:1977`; actual row
  is `:1980` at 635ef14. I never re-derived the line after first capture.
- 2026-08-04 (replan): the tidier-looking reconciliation was the wrong one. Four sources disagreed
  on where the qa gate runs; the elegant reading (qa is only an orchestrator segment, panel stays
  3-wide) was supported by `harness-qa.md`'s "you are a doer, not a reviewer" and by review.yaml's
  header prose. It would have closed #24's hole in ship-feature and opened the identical hole in
  STANDALONE review (`SPEC.md:1980` names that path; `harness/SKILL.md:66` lets the orchestrator
  "insert a review"), where nothing else runs the matrix. The check that settled it — "does this
  path exist, and is it covered by anything else?" — I skipped on the first pass and ran only when
  pushed. Agent-file tool lists and header prose are weaker evidence than a live dispatch path.
- 2026-08-04 (replan): the user's re-scope added an issue and the reflex was to add a task. The
  acceptance test that mattered was different: does any SC go RED if the newly-named file is never
  touched? T-11 without SC-14 would have shipped the fix with nothing asserting it. A new issue in
  scope means new REQ coverage and a new SC, not just a new task.
