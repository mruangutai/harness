# Observations — harness-pm — FEAT-19-central-product-config

- 2026-08-13: the dispatch's HEAD (63b83c7) and the session's git snapshot (89ecc11 on
  feat/FEAT-18-board-truth) disagreed. `git rev-parse HEAD` settled it: 63b83c7 on main. The
  snapshot in the system context is not a measurement; run the command.
- 2026-08-13: a plan-time `--resolve` sweep changed the shape of the plan, not just its routing.
  Four of five surfaces this feature touches return NOBODY, so two of five tasks are
  main-session-direct for the DEC-179 reason rather than the DEC-174 one. Doing the sweep before
  writing tasks meant the partition fell out of the data instead of being retrofitted.
- 2026-08-13: `check-plan-routes.py` enforces a 50-line budget on machine fields per task. A
  careful multi-assertion `verify:` heredoc blows it easily — T-03's first draft was 60 lines. The
  fix is compression, not a shorter check; every assertion survived.
- 2026-08-13: I wrote `gen-decisions-index.py --check` into a `verify:` from the shape of every
  other checker in this tree. The flag does not exist and the script's own `--help` says so
  explicitly. Running `--help` on a script I am about to cite cost one command.
- 2026-08-13: two contradictions survived YAML load, route check and a discriminating-verify
  sweep, because all three test form rather than agreement between artifacts. The BRIEF said a
  session outside both roots refuses loudly while T-01's dispatch prompt said it returns the
  harness config; and T-02 copied kaya's board into the product config, re-creating in this
  feature's own output the two-files-one-value redundancy the feature exists to remove. Neither is
  detectable by any gate. The check that would have caught both is reading the plan's intent prose
  against the BRIEF's requirement text, clause by clause.
