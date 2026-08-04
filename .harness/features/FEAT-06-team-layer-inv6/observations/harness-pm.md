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
- 2026-08-04 (goal-check): SC-03 read as VIOLATED on a literal before/after diff — two non-INV-6
  lines appeared vs `notes/before-check-state-635ef14.txt`. The diff could not separate a code
  effect from a tree effect. Running the PRE-change `check-state.sh` (from `git show 635ef14:`)
  over the CURRENT tree and diffing against the post-change run on the same tree came back
  byte-identical, which settles it: tree state, not code. One of the two new lines was the
  goal-check's own run dir. When a before/after capture spans time as well as a change, hold one
  variable and re-run the old code — a stale capture cannot do it.
- 2026-08-04 (goal-check): the multi-conjunct SC is where evidence quietly goes missing. Seven of
  FEAT-06's twelve automated SCs were conjunctions; eleven of twelve had per-conjunct assertions
  and one (SC-05) had an assertion for the first half only, with the number in the SECOND half
  appearing in the test's printed f-string label. A printed number reads exactly like an asserted
  one in runner output.
- 2026-08-04 (amend): amending PLAN/BRIEF to match shipped code while the main session was still
  editing that code. `build.yaml` had `filter: eng_squad_tasks` at spawn and not at minute 20
  (mtime 14:37); a verify command I had executed at exit 0 became exit 1 mid-run. Re-executing the
  anchor command at FINAL state — not trusting the earlier receipt — is what caught it. A plan
  amendment reads a moving target unless the code is committed first.
- 2026-08-04 (amend): `run-unit-tests.sh` 0, `check-state.sh` 0 and `check-docs.sh` 0 all ran green
  AFTER the `filter:` key was deleted from `build.yaml`. No gate reads team-file field content
  beyond what `test-team-catalog.py`'s ten checks name, so an approved EMF-2 fix was removed
  silently — the same unguarded-copy class this feature exists to close.
- 2026-08-04 (amend2): the escalation from the previous pass was ANSWERED, not reversed — the user
  ruled the key unneeded. Writing the amendment note in the house "previously read '<literal>'" form
  reintroduced the deleted token `eng_squad_tasks` three times and pushed the `filter` residual to
  11, blowing the mandated residual counts (0 and ≤1). Quoting a deleted string verbatim defeats a
  residual-count gate. Naming the key by ROLE ("the task-selection key") instead of by literal kept
  the amendment honest and the count clean. Measure residuals BEFORE writing the note, not after.
- 2026-08-04 (amend2): before deleting a config key's instruction from a PLAN task, check what the
  instruction has BUNDLED into it. T-04's `filter:` paragraph also carried the DEC-118 "a non-eng
  task is not dropped" requirement, echoed in T-09 and shipped at `build.yaml:5-6` and `:46-50`.
  Deleting the paragraph wholesale would have dropped a live requirement with the dead key.
