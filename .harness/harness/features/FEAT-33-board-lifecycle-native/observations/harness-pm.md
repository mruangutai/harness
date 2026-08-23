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
- 2026-08-23: FEAT-33 rulings round. A binding operator ruling (stop closing sub-issues at commit)
  collided with an invariant the plan is forbidden to edit (INV-26 maps task status done to the done
  column, check-state.sh:1234). Neither the arch review nor the four-angle simplify pass saw it,
  because both graded the plan before the ruling. Lesson for me: when a ruling changes WHEN a
  ticket closes, grep the gates for what they assert about that ticket's state before applying it.
- 2026-08-23: two count claims in the plan were stale and nobody re-counted them — integration.detect
  said "six explicit filenames" against 22, INTEGRATION_SCRIPTS "14-name" against 22. A count in
  prose is the citation class least likely to be re-derived, because it does not look like a pointer.
- 2026-08-23: the scaffold template (.claude/skills/harness/templates/harness.json) carried the
  five-key station instruction. Grepping only bin/ and .harness/ for a widened constant misses the
  templates dir, which is the file a NEW repo is built from.
- 2026-08-22: FEAT-33 cycle 2 — a reviewer finding named ONE unordered writer pair (T-07/T-08 on gh-sync.py); computing the general property (for every file, are all its writers totally ordered in the transitive closure?) over plan.yaml found 20 unordered pairs across 8 files in 4 families. Four depends_on edges closed all of them. Twenty lines of python over the parsed plan is now my default check before returning any plan whose tasks share files.
- 2026-08-22: FEAT-33 cycle 2 — adding a serialising edge silently ages the successor task intent line anchors (all pinned at one sha). Each new edge got a one-paragraph ORDERING note telling the doer to re-derive by symbol.
- 2026-08-23: a plain YAML scalar cannot carry ": " — I broke plan.yaml's D-24 `because:` by writing
  "RULED: the operator..." inside a one-line plain scalar and safe_load failed at column 1135. Any
  prose I splice into a single-line `because:`/`choice:` value must use " - " where I want a colon.
  Parse the file right after every edit; check-plan-routes.py would have caught it, but only after
  I had already written more.
- 2026-08-23: plan-merge.py cannot EDIT an existing task or decision — it unions by id and exits 7
  when one id carries two different values. Amending an existing intent is a direct file edit, and
  the merge tool is for ADDING. Do not reach for it to reword.
- 2026-08-23: "feature X merged" is two different facts. FEAT-26's plan SIGNATURE merged to main
  while all eight of its tasks were still pending, and a prior round's BRIEF recorded that as the
  feature having merged. Check feature.json status AND the task statuses before writing "merged".
- 2026-08-23: FEAT-33 goal-check. Two SCs failed on their own SENTENCE, not on the work: SC-01 asserted a one-run conjunction the signed plan explicitly splits across two runs (provision exits 3 before the field branch), and SC-20 asserted a status-Done fixture that check-state.sh's terminal exemption makes unconstructible. Both were signed with the plan that contradicts them - the swap test does not catch this; only re-reading each SC against the task intent that implements it does.
- 2026-08-23: a before/after capture pair can be BOTH identical and cited as proof of 'differs by nothing except X' - check-state-before/after-T-22.txt are byte-identical with zero INV-26 lines, so the removal half was never demonstrated live. When an SC says 'differs by nothing except', require the capture to show the except-set non-empty.
- 2026-08-23: SC-15 graded on 'git show <review_sha>:path' passed only in the working tree - the fix landed uncommitted in fix cycle c1, so the criterion's own command fails against the pin. A content-at-sha criterion needs the sha re-pinned after every fix cycle, or it grades a tree nobody ships.
