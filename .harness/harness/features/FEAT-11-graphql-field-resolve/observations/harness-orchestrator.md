# Observations — harness-orchestrator — FEAT-11-graphql-field-resolve

- 2026-08-10: The repo moved under me mid-run. My dispatch brief said `main` at 45af5aa clean; by the
  time the plan run returned, HEAD was 835b297 — eight commits, one of which DELETED
  `.claude/skills/harness/bin/check-docs.sh` (issue #202). I had told two leads to respect that gate
  and its `<!-- ok-stale -->` escape. Harmless here, but the lesson is that a long-running
  orchestrator's environment facts expire: re-read HEAD before pinning `review_sha` or asserting a
  gate exists, never trust the spawn brief's sha at the end of a run.

- 2026-08-10: Dispatched a validator plan-contract segment on a plan that had already passed
  eng-lead + visual-designer + ui-reviewer inside the product run. It returned FAIL with three
  must_fix, one of which (`git diff --quiet HEAD` in T-01's verify) was vacuous by construction —
  it passes trivially once the build agent commits before running verify. The intra-squad reviewers
  had all read that same clause. The independent segment earned its spawn; predicting it would not
  have been wrong in a way nothing would have surfaced until build.

- 2026-08-10: I told a lead to run two steps "in parallel, disjoint files" — pm on BRIEF.md, designer
  on a line-number pointer INTO BRIEF.md. The lead overrode me and sequenced them, and it was right:
  pm's edits moved the pointer target :132 → :137. Disjoint *files* is not disjoint *content* when
  one member's output is the other's input. My parallelism instruction would have cost a cycle.

- 2026-08-10: The validator escalated that the operator's own grilling artifact carried a false
  premise (`_validate_stations` and the `Redy` case "depend on" two error paths). Two file reads
  settled it — the function propagates without reading the text, the test runs against a Recorder
  and never enters the module. Measured rather than escalated. The right split turned out to be:
  the CONSTRAINT is the operator's and stands regardless; the REASON is a fact and is mine to check.

- 2026-08-10: The falsified claim lived in four sites; the validator's must_fix named one. Grepping
  the behaviour phrase myself across all three artifacts found the other three — including one
  inside a success CRITERION (SC-04), where the fix had to correct the justification without
  weakening the testable clause. DESIGN.md turned out to already carry the correct account, so the
  dispatch could point pm at a peer's file instead of asking it to invent wording.

- 2026-08-10: A lead's final digest write can BREAK a contract its earlier draft satisfied. The
  plan-product digest passed when member entries were collapsed per persona and failed after the
  lead expanded them per step, because three superseded FAIL rounds re-entered the roll-up input.
  I read the earlier version and validated the later one; only the second reading caught it.
  Validate the digest on disk at the END of the run, not when you first read it.
