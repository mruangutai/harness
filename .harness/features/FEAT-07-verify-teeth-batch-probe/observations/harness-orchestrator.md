# Observations — harness-orchestrator — FEAT-07-verify-teeth-batch-probe

- 2026-08-04: NO plan team file exists in either directory. `ls .harness/teams/` → absent;
  `.claude/skills/harness/teams/` holds only `build.yaml` and `review.yaml`. FEAT-06's
  `plan-product/state.yaml` records `team: plan-feature-segment-1`, a name that resolves to no file
  — so that run was an improvised team name. Naming a team here would have bought a spawn that
  returns a directory listing and stops. The single-task-through-the-lead path is the working one,
  and it also dissolves the run-dir chicken-and-egg: `harness-team` demands the checkpoint be
  written BEFORE dispatch, but the run dir path needs pm's not-yet-coined feature id. On a
  single-task dispatch the lead only needs the dir at close.

- 2026-08-04: Plan phase cost $44.57 attributable vs FEAT-06's $170.17, for a comparable
  9-task/12-SC plan. The differences: no design pass (skipped, zero end-user surface), no
  pre-signature architecture review, zero send-backs, and a grilling artifact that pre-verified
  the anchors so pm did not re-derive them. Which of those four carried the saving is NOT
  separable from one data point — perf-doc row 10 (per-lever instrumentation) is exactly the thing
  that would have said, and it was ruled out of scope.

- 2026-08-04: The dispatch prompt named the mandate/ruling TENSION explicitly ("the settled field
  is self-reported; the mandate says mechanically ungameable — word the SC to what is enforced and
  raise the residue as an open_question") rather than letting pm reconcile it silently. pm came
  back with a scoped recommendation AND, while sizing it, found an unrelated live fail-open in the
  shipped validator (`suite: fail` + `PASS` accepted, GATE_FIELDS nested inside the
  PLACEHOLDER_UNSET branch at `validate-digest.py:477-484`). I re-verified it empirically at my own
  tier before relaying. Naming the tension is what sent pm to read the enforcement code at all.

- 2026-08-04: The handed propagation site list was short by three AGAIN — fourth consecutive
  feature. pm found `harness-dev-ops.md:69-75`, `SPEC.md:1062-1063` and
  `test-validate-digest.py:1043-1044`, and also recorded the sites it ruled OUT with the grep that
  ruled them out. The ruled-out list is the part that makes the re-derivation auditable; a bare
  found-three-more claim is not checkable.

- 2026-08-04: `validate-digest.py` takes a PERSONA as argv[1] — `validate-digest.py lead <file>`.
  Passing the file alone returns `BLOCKED (contract violation) — unknown persona '<path>'`, which
  reads like the file failed when the invocation was wrong. `--help` produces the same misleading
  line. Cost me one wasted call.

- 2026-08-04: THE ARCHITECTURE REVIEW'S BEST FINDING WAS PROVEN BY ITS OWN RETURN. The reviewer was
  a `harness-backend-dev` returning `VERDICT: PASS` on a dispatch carrying no PLAN task and no
  `verify:` command — which is exactly the case the planned gate makes illegal. It was accepted only
  because the change has not landed. A reviewer whose own return instantiates the defect is the
  cheapest possible evidence, and neither of the two planning passes before it had found the gap.

- 2026-08-04: A REVIEWER'S CORRECTION OF MY MEASUREMENT WAS ITSELF WRONG, and only re-measuring
  settled it. I reported the index drift as uniformly +6; the review said the deltas reverse
  direction and concluded "at least two independent edits". Printing the four values directly
  (committed DEC-118 @2376 / DEC-174 @4674; generated @2382 / @4680) showed the review had
  transposed one pair — 57 of 174 rows, all exactly +6, ONE edit. Two prose accounts of the same
  numbers cannot be adjudicated by reading them; a stronger reviewer's confidence is not evidence.
  I had also been wrong twice in the same exchange (the review discharged one of my three handed
  findings as already-in-the-artifact), so the lesson is symmetric.

- 2026-08-04: THE BATCHING RULE THIS FEATURE INSTALLS, USED ON ITSELF, IS WHY THE USER SAW TWO ROUND
  TRIPS INSTEAD OF SEVEN. Four user rulings went down as one dispatch; seven review findings went
  down as one dispatch, each carrying a LEAVE list naming what was already settled so no spawn
  re-judged it. FEAT-03's counter-example cost seven serialized runs and ~$95 for the same shape of
  work. The mechanism that makes the LEAVE list work is that it names findings the ORCHESTRATOR
  raised and lost — "I raised this, the review checked it, leave it" is what stops the next member
  re-litigating it.

- 2026-08-04: COST CROSSED AT THE STEP THE USER EXPLICITLY ORDERED. 44.57 for the first pass, then
  180.37 of 120 after the review and its fix. The review cost 30.49 and found a blocking gap in the
  one task no member reviews during the build. Reporting the overrun with what it bought, rather
  than the bare figure, is what makes it a decision the user can act on instead of an alarm.

- 2026-08-04: PRICING THE REJECTED OPTION WELL IS WHAT MADE THE REDIRECT COST ONE INSTRUCTION. pm
  recommended the cheap option but wrote the alternative's full price into PLAN against six
  enumerated in-file redirect markers, and pre-counted the trap — a bare marker grep returns
  eleven, five of which are not redirect sites. When the user reversed the recommendation, the
  whole change was mechanical: zero markers survived and no site was re-derived. A recommendation
  that does not price its own rejection forces a re-plan when it loses.

- 2026-08-04: THE ADVISOR CAUGHT ME UNDER-STATING A TRADE-OFF I HAD ALREADY MEASURED. My headline
  called the pending decision "a scope call, not a defect" while pm's own option text said the
  recommended value was CHEAPER TO ABUSE than the lie it replaced. Both facts were in my context;
  the framing buried one. The user then redirected on exactly that ground. Emphasis and ordering
  are not cosmetic when the reader's decision depends on which cost they see first.

- 2026-08-04: EVERY RELAYED "ALREADY VERIFIED" FACT THIS FEATURE PRODUCED WAS WRONG AT LEAST ONCE.
  The main session's "no pre-existing index drift" described a tree an undeclared agent had already
  fixed; the architecture review's correction of my anchor measurement transposed a pair; my own
  dev-ops residue finding was already in the artifact I had not read. Re-measuring at my own tier
  cost seconds each time and changed the plan twice. The relay is a pointer to a measurement, never
  the measurement.

- 2026-08-04: RAISING A BUDGET IS A MEASUREMENT PROBLEM, NOT A NEGOTIATION. The main session
  proposed 400; I set 550 with an arithmetic basis — plan phase closed at 242.48, FEAT-06's
  build+validate measured 252.63 with its own note recording that as an understatement because most
  build tasks ran at depth-0 and were not separable, and this feature has the same shape with a
  doubled T-01. A budget that gets crossed in week one produces alarms nobody reads, which is worse
  than no budget.

## Build, validate and close phases

- 2026-08-04: EIGHT OF TEN TASKS WERE LAYER-0 WORK AND I RETURNED THEM AS TWO SEGMENTS, NOT EIGHT
  ROUND TRIPS. Segment 1 was T-01 plus the three tasks independent of it, so a T-01 failure would
  have wasted none of them; segment 2 was the four whose deps it satisfied, in dependency order,
  each with its `verify:` verbatim. The squad run for the two `docs/**` tasks slotted between them.
  Two main-session round trips for eight tasks, against FEAT-03's seven serialized runs.

- 2026-08-04: THE FEATURE'S OWN THESIS FIRED INSIDE THE FEATURE, THREE TIMES. DEC-175's index ruling
  shipped at 32 words against a 30-word cap that lives only in `test-gen-decisions-index.py` — no
  task's `verify:` invoked it and `DECISIONS-INDEX.md`'s header does not state it, so the member
  could not have learned it from what it was given. T-03's scope guard fired on a first draft
  carrying the exact false sentence a superseded draft had instructed. And T-08's clause went red
  because `before any claim` was split across a line break with bolding inside it — the rule read
  correctly to a human and the literal string did not exist.

- 2026-08-04: A LINE-WISE GREP CANNOT SEE ACROSS A WRAP, AND IT NEARLY BOUGHT A WASTED CYCLE. Two
  SC-07 checks reported surfaces failing that were already correct, because the clause wrapped
  across comment lines; a directional regex also missed `Omit … when task: none` because the verb
  precedes the noun. Flattening whitespace in Python before matching settled it and found the one
  genuine gap. Every `grep -c` detector aimed at a hard-wrapped file carries the same trap, in both
  directions — it also false-NEGATIVES a prose-correct fix whose wrap splits the counted tokens.

- 2026-08-04: THE GOAL-CHECK'S FOUR UNMET CRITERIA WERE ALL UNDER-PROOF, NOT WRONG BEHAVIOUR. Every
  clause was run against the validator and it behaved correctly; what was missing was a fixture, or
  a clause of prose the approved task intent had already specified and that did not land. The shape
  is a criterion enumerating N clauses, shapes or personas with fewer than N fixtured — SC-03's
  dev-ops `fail` half, SC-05's documentor family, SC-18a's ALONGSIDE assertion, SC-07's binding rule
  on three of four surfaces.

- 2026-08-04: SC-12 NAMED A RECEIPT NO AGENT IN THE ORG COULD WRITE. `harness-documentor` executed
  T-09 and holds no `notes/receipt-*` grant — only the five dev specialists do. Carving that half
  out with the reason, and recording the substance that WAS captured (precondition exit 0, index
  clean, nothing absorbed), routed it to the user as a named residue instead of an unmet criterion
  with no lead to fix it. Three separate lead dispatches named `notes/**` for a documentor and the
  hook refused each time.

- 2026-08-04: THE RELAY-DICTATION QUESTION (OQ-01) IS ANSWERED, AND THE VARIABLE IS DISPATCH SHAPE.
  Three squads: product 2 of 4 novel relayed candidates accepted with one killed by the member
  reproducing the evidence; validation 4 of 5 accepted but ZERO entries from either member's own
  material; engineering 3 of 5 from the member's OWN material — the difference being that eng-lead
  handed its member the paths to its own prior artifacts and said self-derived candidates count.
  Neither validation member kept an observations log either, so the log is not the variable.

- 2026-08-04: I BROKE MY OWN STATE FILE WITH AN UNQUOTED SCALAR. `goal_check: FAIL — … 4 unmet:
  SC-03, …` put a colon-space inside a plain scalar and `safe_load` raised at that column; the file
  had been valid one write earlier. Quoting fixed it. Every summary line I write into `feature.yaml`
  risks this, because the natural way to write a verdict summary uses a colon.

- 2026-08-04: FINAL COST 702.82 AGAINST A 550 BUDGET I HAD MYSELF RAISED FROM 120. The raise was
  measured and still short by 28%. The two costs the arithmetic missed: a validation panel plus a
  goal-check that found real gaps and cost four fix runs, and the close phase's distillation at
  129.10 — which the user ruled KEPT on the ground that it buys the next feature's starting position.
