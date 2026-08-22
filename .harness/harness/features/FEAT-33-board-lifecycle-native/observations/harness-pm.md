# Observations — harness-pm — FEAT-33

- 2026-08-22: the dispatch and the grilling artifact both asserted that `ProjectV2Workflow` state was
  effectively unreadable. One live query settled it the other way:
  `projectV2(number:$n){workflows(first:30){nodes{name enabled number}}}` returns both fields on
  boards 2 and 3. Only `trigger`/`action` are absent. Running the query cost one call and changed the
  feasibility verdict on #673 from "risky" to "one query". Lesson shape: an inherited "the API cannot
  do X" is a measurement, and inherited measurements about an external API are the cheapest to re-take.
- 2026-08-22: the load-bearing constraint on this whole plan was found in a validator nobody cited —
  `factory_config.validate_board` tests the station keys for EXACT set equality
  (`factory_config.py:134`), and `product_config` reads a served repo's config from the REMOTE at
  `default_branch`, never a checkout. Together those two make a one-key config change a cross-repo
  ordering problem. Neither the dispatch's decision floor nor the grilling artifact named either. I
  found them only because I traced what "declare `plan`" would actually execute against.
- 2026-08-22: `check-domain.sh --resolve` grants `check-state.sh` to `harness-dev-ops` while DEC-174
  forbids dispatching a change to it. The two answers disagree and only prose reconciles them. Raised
  as a non-blocking open_question rather than worked around.
- 2026-08-22: `--resolve` returned `harness-orchestrator` for a generic `features/<FEAT>/notes/*.md`
  path. The orchestrator is not a task executor, so a plan task writing there has no dispatchable
  owner and must be `main-session-direct`. `check-plan-routes.py` reports that as an advisory
  DEVIATION, not a violation — exit 0. Worth knowing that a DEVIATION line is the expected output for
  a correctly-declared orchestrator-owned path, not a defect to chase.
