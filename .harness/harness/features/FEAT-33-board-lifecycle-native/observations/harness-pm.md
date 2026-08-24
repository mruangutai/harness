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
- 2026-08-23: FEAT-33 - plan-merge.py cannot record a strike on an EXISTING task or decision: an id whose value differs from the base raises exit 7 CONFLICT (plan-merge.py:262-275), so an in-place amendment of a signed task is Edit-tool work by construction. Convention found for a struck record: FEAT-18 plan.yaml D-08 (a struck: sibling key, original choice: kept), and inside FEAT-33 itself T-18 verify (an in-field CORRECTED comment). No precedent existed for striking a clause of a task intent; I used a struck: list of clause/in_force/replaced_by/falsified_by/evidence entries plus [STRUCK ...] markers left beside the original wording.
- 2026-08-23 (FEAT-33): DEC-188's discriminator is STATEMENT-vs-TREE, not location. The same sentence lived in a decision's choice: and in a task's intent step; labelling one struck and the other struck_in_part made the record contradict itself about which rule applied. Reading a narrowed absolute as "flatly contradicted" because it fails on the carved-out instances would collapse DEC-188's amendment category entirely - that is true of every narrowing. Test that discriminates: does any population remain over which the clause holds unweakened? Established boards remained, so amendment; step 2's "STOP before the field work" had none, so strike.
- 2026-08-23 (FEAT-33): BRIEF.md had no precedent for amending a signed criterion, so I matched SC-10's and SC-16's own shape - keep the signed sentence quoted verbatim inside the same bullet, then a bolded correction naming the ruling, the measurement and the pointer, with verify: left as the bullet's last line. Reuse over invention: the file already answers "how do we record a superseded claim here".
- 2026-08-23 (FEAT-33): both correction passes I wrote into notes/research-FEAT-33-goal-check.md cited board_lifecycle.py by LINE; both sets were stale within hours because a fix cycle was editing the file concurrently. Cite by function name in any record about a file with a live writer.
- 2026-08-23 (FEAT-33): correcting one falsified sentence in a scope-call section exposed a second one TWO LINES up in the same numbered item - the item enumerated two routes to a provisioned field where the code has three. A falsified claim clusters with its own justification, so when correcting one, re-read the whole enclosing item rather than the sentence.
- 2026-08-23 (FEAT-33): a signed criterion whose OUTCOME is proven but whose MECHANISM verb is wrong takes a note, not an amendment. SC-01 grades an end state proven live; rewording it would spend a signature and change no grade. The note's job is to stop the next reader writing code that matches the verb - which was the actual bug.
- 2026-08-23 (FEAT-33): a Verification-gaps bullet saying "what is NOT proven" goes stale the moment someone captures the live run it was hedging against, and nothing flags it - the bullet still reads as an honest open gap while understating the evidence held. Re-read every NOT-proven claim after any live/manual capture lands.
- 2026-08-23 (FEAT-33): the sixth falsified statement in this BRIEF was invisible to every grep I ran (never / no code path / zero / non-destructive) and only fell out of reading all 642 lines by eye. It was a PROBLEM statement made false by the feature's own fix - the healthiest falsification and the one no keyword search can shape a pattern for. Read the file when the count of found defects is still climbing.
- 2026-08-23 (FEAT-33): the same baseline appeared twice - once sha-anchored inside SC-15 (at 46ee87c, grep -c returns 1) and once bare in a prose paragraph. The anchored copy survived its own fix and stayed true; the bare copy became false. That is the concrete payoff of B-12, observed on one claim in one file.
- 2026-08-23 (FEAT-33): a coordinator handed me 'board 3 reached 0 findings' as settled fact; the capture reads 2 finding(s). Re-derive a figure a dispatch supplies even when it is offered as already-verified evidence, and especially when it is the premise for deciding a clause is falsified.
- 2026-08-23 (FEAT-33): I corrected a false sentence by inserting two false ones. Cause 1: two capture files whose names differed by one word (migration-harness-audit-after.txt vs -after-2-accepted.txt) and I picked by which name sounded more specific, never checking which was current. When two artifacts could answer one question, check git log on both and read the one the later commit wrote - do not read the name.
- 2026-08-23 (FEAT-33): cause 2 of the same failure - I generalised 'board 3's reconcile moved no cards' into 'reconcile does not move cards'. My own cited evidence (zero STATION findings on that board) was the disproof: absence of a class on one input says nothing about the tool. Before writing a claim about a TOOL, read the tool's own dispatch table; _ALWAYS_FIXABLE_KINDS settled it in one grep.
- 2026-08-23 (FEAT-33): an equality assertion on a transient defect count reddens when the defect is FIXED. T-11's verify pins check-state.sh's VIOLATION count to = 1, justified by another feature's unsigned BRIEF; that BRIEF landed and the count is now 0, so a done task's verify fails because things improved. Assert absence of the specific violation, never equality on a total.
- 2026-08-23 (FEAT-33): the seventh falsified statement was a verify: block, not prose - found only by reading plan.yaml end to end after grep coverage had been declared insufficient. A stale verify on a status: done task is worse than stale prose: it reddens a gate and nothing attributes it to the ruling that superseded it.
- 2026-08-23 (FEAT-33): repointing a verify from a LIVE mutable board to a COMMITTED capture is what made it stable, and reading the capture through 'git show HEAD:' rather than the working tree is what kept it honest - an uncommitted or deleted capture now reddens instead of passing. Two clauses: the immutable archived capture proves the detection capability, the live capture proves the delivered outcome.
- 2026-08-23 (FEAT-33): after fixing a verify, prove it can redden before claiming it is fixed. Three mutants, each exit 1: swap the two capture paths in each direction, and swap the absence-grep pattern for one that IS present. The third is the load-bearing one - it proves the pipeline runs at all, so 'test -z' is not passing vacuously on an empty capture.
- 2026-08-23 (FEAT-33): the worst falsified record on this feature was a report whose HEADER contradicted its own final section - migration-harness.md still opens '13 findings to 2 findings' and 'an audit that exits 0 is impossible on this board' while its last section records 0 findings and the reversal. An appended correction does not fix a document whose summary a reader stops at. When appending a reversal, amend the summary in the same act.
- 2026-08-23 (FEAT-33): a criterion pinned to a MEASURED POPULATION rather than an outcome drifts by construction - SC-19 pinned 188 task tickets measured a day before the run and 218 were renamed. The outcome clauses were all stronger than asked. Pin what the work controls; a population count is not that.
- 2026-08-23 (FEAT-33): the tenth falsified statement was in MY OWN artifact - the goal-check note's title read '17 MET, 3 NOT MET' through SIX appended corrections that changed three of those verdicts. I had spent the day cataloguing this exact defect in other people's files. Appending a correction never repairs a summary; when you append a reversal, edit the summary in the SAME act or the document contradicts itself with the false half on top.
- 2026-08-23 (FEAT-33): the capture-confusion had a mechanical origin worth knowing - migration-harness-audit-after.txt was OVERWRITTEN in place at ace0b06 and its old content preserved under a near-identical name. The citation to it did not rot; the file changed underneath it. A capture path is a stable anchor only if the capture is immutable, so read captures at a ref (git show HEAD:) and name which sibling is archived.
- 2026-08-23 (FEAT-33): before grading a criterion in a note, grep the note for its OWN verdict vocabulary. This one's tally admitted met/not_met/unverifiable; 'partial' appeared twice but only as prose recommendations, never as an assigned verdict. Adding partial would have introduced a fourth bucket into a three-bucket tally, so not_met was the honest grade.
- 2026-08-23 (FEAT-33): when a reversal supersedes a document's reasoning, separate the part still TRUE from the part now false rather than striking the section. migration-harness.md argued an audit exiting 0 was impossible; reconcile genuinely will not write a Done column (still binding), but a HUMAN adding the cards was never ruled out. A tool's limit had been mistaken for the board's limit.
