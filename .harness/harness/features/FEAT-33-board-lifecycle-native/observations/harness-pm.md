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
- 2026-08-22 (fix cycle): two readers reported the SAME T-02 fixture blast radius (arch M1, simplify
  L1) with PARTLY DIFFERENT file lists — arch missed `test-factory-land.py` and
  `test-factory-decompose.py`, simplify missed `test-factory-integration.py`. Either list alone leaves
  T-02 red on files it does not name. Take the union whenever two readers report one defect.
- 2026-08-22: the finding said three `feature` tasks under-cover `integration`. The discriminating
  check neither reader ran was in the gate's own rule — `harness-qa-gate/SKILL.md:60`, *"Presence is
  not satisfied by an unrelated existing test"* — which turns under-coverage into a hard FAIL. Reading
  it reframed the remedy away from retyping `change_type` and toward the one file already in both
  `integration.detect` and `INTEGRATION_SCRIPTS` (`test-factory-integration.py`, whose docstring says
  it is the only file that forks a real process).
- 2026-08-22: the same defect existed in T-03 (`change_type: api`, whose `when` fires `integration` on
  `touches_db_or_external`) and NEITHER digest flagged it. Applying a finding's remedy to only the
  tasks the finding names leaves the rest standing.
- 2026-08-22: FEAT-29 T-03 shipped `change_type: feature` with a unit-only verify and the identical
  coverage hole. Precedent said fine; the gate's text said FAIL. Precedent is not bedrock.
- 2026-08-22: the sha pin looked stale (`d065b3b` vs HEAD `e3c9187`) but
  `git diff --name-only d065b3b..HEAD` returned only this feature's own artifacts, so every code
  anchor was still valid. Re-pin AND state the equivalence; a bare re-pin loses the finding that
  nothing drifted.
- 2026-08-22: added a decision whose plain-scalar `because:` contained `": "` and broke `safe_load`.
  Validate after every `decisions:` edit, not once at the end.
