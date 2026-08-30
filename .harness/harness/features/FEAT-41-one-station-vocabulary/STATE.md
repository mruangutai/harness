# STATE

## Current

- feature: FEAT-41-one-station-vocabulary
- run: 2026-08-29-02-product. The operator's answers applied as ONE consolidated revision.
  product-lead PASS, ZERO send-backs.
- squad: none
- status: Ready. SIGNED — `plan.yaml` `approval.status: approved` and `BRIEF.md:255`, both
  Mike Ruangutai, 2026-08-29, re-confirmed by the operator on 2026-08-30. The earlier
  "NOTHING IS SIGNED" reading was written before the signature landed and is corrected here.
  `review_sha` is pinned past the signature commit at `49638bf` (DEC-89; #965).
- WHY THIS RUN EXISTED: the operator read notes/ship-review-2026-08-29-01.md and returned a
  complete, decided answer set in notes/answers-2026-08-29-01.md. This run executed those
  decisions; it did not re-open them and did not re-audit the 13 tasks the replan re-derived.
- Q1 APPLIED — THE DECISION-RECORD TASK IS REMOVED, not deferred in place. The operator declined
  its external dependency on the decisions-authority triage. The plan is now THIRTEEN tasks and
  carries NO team-lane task at all: every surviving task is main-session-direct. Its dependency
  edge is dropped from the rename task, the one prose reference in the schema-migration task is
  re-worded, and D-09 is KEPT to preserve what the deferred recording must say, so the triage
  inherits the content rather than re-deriving it.
- IDS ARE GAP-NOTED, NOT RENUMBERED: the two ids after the gap are cited in this file, in the run
  digests, in the ship-review briefing the operator has read, and in the answers file itself.
  Renumbering would falsify every one of those references (PRINCIPLES rule 15).
- Q6+Q7 APPLIED, folded into one edit site as instructed. INV-32 is scoped to NON-TERMINAL
  stations, reusing check-plan-routes.py's own `_is_shipped`/`FINISHED_STATUSES` idiom rather than
  a second one, and its precondition is now "a real pin exists AND the station is non-terminal" —
  the lagging validator-run condition is dropped, so the guard can fire BEFORE a panel reads the
  wrong text instead of only after. The task now carries the execution-order fact that makes it
  implementable: the terminal read is plan.yaml's top-level station against the LOWERCASE terminal
  set, never feature.json, because the schema-migration task it depends on deletes that key first.
- THE SCOPE IS LOAD-BEARING FOR FOUR SHIPPED FEATURES, NOT ONE — measured BY ME at the cc00983
  tree, walking all 40 feature dirs and comparing `git show <review_sha>:<plan path relative to the
  git top level>` against the working copy byte for byte, which is the comparison the check itself
  makes. Under the REVISED precondition the reported set is EMPTY: no live feature goes red when
  INV-32 lands. FOUR carry a real pin whose plan bytes have moved and are silenced ONLY by the
  terminal scope — FEAT-26 (bad32441), FEAT-27 (9b929de), FEAT-32 (5107efb9), FEAT-33 (337bbc21),
  all at station done. Q6 named only FEAT-27; the other three were HIDDEN by the very validator-run
  precondition Q7 removes. Had the two answers been applied separately, the second would have
  reddened three shipped features the first never measured.
- A THIRD FIXTURE, case (inv32.c), proves the terminal silence on the FEAT-27 shape — stale pin,
  moved post-pin bytes, terminal station — alongside the existing red/silent pair, and the verify
  asserts its label. The task also states what that case CANNOT prove: against an unmodified
  check-state.sh it passes vacuously, so its discriminating run is against an implementation that
  already reports (inv32.a) but carries no terminal scope, and that red is what the receipt records.
- THE SCOPE LOSS IS DISCLOSED WHERE THE OPERATOR SIGNS. BRIEF.md's Constraints now state plainly
  that this feature lands changes contradicting one clause each of DEC-203 section 6, DEC-191 and
  DEC-182 WITHOUT recording the contradiction in DECISIONS.md, that all three entries read as
  though the contradicted clause still holds until the triage lands, and that no success criterion
  rests on it — which is exactly why it needed saying. Carried as PB-04.
- EVERY REQ AND SC STILL HAS A TASK BEHIND IT. pm re-checked all thirteen criteria one at a time
  rather than by a file-global grep; the four requirements the removed task traced are all
  discharged elsewhere. Nothing was orphaned and nothing was quietly dropped.
- commit: 0dbd284, "Apply the operator's answers". Tree clean.
- PIN RE-PINNED to 0dbd2845074c97401e38dbf50e2d19e5587258b2, the commit carrying the revised
  plan.yaml and BRIEF.md. Without this the feature would have become the ONE feature INV-32
  reports — pin and plan bytes diverge at every plan commit, which is the invariant's own subject.
  `lanes.resolved_at: 0d4845b` is deliberately left: the revision changed no source file.
- gates, both run BY ME at this commit. check-plan-routes.py: exit 0, "0 violation(s) across 1
  plan(s)", 40 dirs examined and 39 skipped as shipped — the known-good shape, unchanged.
  check-state.sh: exit 1 with exactly ONE violation, this feature's unapproved BRIEF, correct
  during a plan phase and closing at signature. The pre-revision baseline shape.
- A SECOND VIOLATION APPEARED AND WAS CLOSED, recorded because it is the gate working: INV-5
  forbids this file from naming a task its plan.yaml does not contain, so the first draft of this
  entry — which narrated the removal by id — turned check-state.sh red. The id is carried by the
  artifacts built to hold it (the commit message, D-09, PB-04, the answers file, all tracked) and
  this file describes the task rather than naming it. Nothing is lost and nothing is softened.
- next: the operator's signature. Every condition the answers file set for it has landed.
- cycles: 8 of 10 — ZERO send-backs this run, so the count does not move (DEC-157: only rework
  counts). runs: 15 of 20.
- briefing: none written. The operator has read notes/ship-review-2026-08-29-01.md and decided;
  this run returns a delta, not a second briefing.

## Open Questions

- Q1: RESOLVED 2026-08-29 by the operator. The external dependency is declined and the
  decision-record task is removed; its subject re-files with the decisions-authority triage,
  outside this feature. See BRIEF.md PB-04 and plan.yaml D-09.
- Q2: MOVES WITH THE RE-FILED WORK. It was input to the recording-form choice — DEC-188's own text
  bearing on strike-in-place versus subsuming rewrite. Preserved in D-09 for the triage.
- Q4: RESOLVED by events, 2026-08-29. The INV-26 FEAT-40 violation is gone — FEAT-40 shipped.
- Q6: RESOLVED and APPLIED. INV-32 is scoped to non-terminal stations. FEAT-27's pin is NOT
  repaired: shipped history stays untouched, per the operator.
- Q7: RESOLVED and APPLIED, folded into the same edit site as Q6.
- Q8: HARNESS DEFECT, AND IT FIRED AGAIN THIS RUN. Nothing allocates run-dir slugs. This run's
  product squad wrote into runs/2026-08-29-01-product — the slug the SAME DAY's replan run already
  held — and overwrote its digest.md and state.yaml. runs/ is gitignored, so the replan digest is
  unrecoverable; what survives of it is this file, feature.json and the tracked ship-review
  briefing assembled from it. Recorded in runs/2026-08-29-01-product/OVERWRITTEN.md rather than
  reconstructed (rule 15). The two runs are registered in feature.json under distinct ids; the
  digest physically at the -01 path is the -02 run's. THE CAUSE IS MINE AS MUCH AS THE HARNESS'S:
  I dispatched without naming a slug, having seen this exact failure recorded three days earlier.
- Q9: unchanged. The stale-pin task traces REQ-07 and pm calls the stretch knowingly. DEC-89
  already decides its invariant and says the state check re-pins review_sha; nothing implements
  that re-pin, so #867 is the unbuilt detection half of an already-decided invariant.
- Q10: non-blocking harness defect. Gitignored `__pycache__/*.pyc` defeat every absence-grep over
  the bin directory, a compiled constant still carrying the searched string. Should
  `--exclude-dir=__pycache__` be a standing convention, or should run-unit-tests.sh clear it?
- Q11: non-blocking HARNESS DEFECT, confirmed by measurement. The shell substitutes PHANTOM
  pathnames for an unmatched glob member, so `grep -rn PAT dir/*/f.yaml` exits 2 on ENOENT even
  when it matches, making `grep ... ; test $? -eq 1` unusable harness-wide. Measured: 31 of 40
  dirs hold plan.yaml, grep found 56 matches and still exited 2 with 9 ENOENT lines. I could not
  file it via xd://report_issue — check-domain denies the orchestrator that path.
- Q12: NEW, non-blocking, and the operator may want it settled before signing. plan.yaml's lanes
  block keeps a row resolving `.harness/harness/docs/**` to the team lane with harness-documentor,
  and no surviving task touches that surface. check-plan-routes.py does not object — it resolves
  per task, not per lanes row — so the row is vestigial rather than false. Left standing because
  the rows are a dated resolution record (DEC-179) and I told pm to leave the DEC-174 rows alone;
  flagged because BRIEF.md now says the plan has no team-lane task and a reader could take the row
  for one.
- Q13: NEW, non-blocking, pre-existing and untouched by this revision. SC-02's own quoted-literal
  grep — the one the criterion writes out in full — appears in no task's `verify:` block, so the
  criterion is graded against a command nothing runs. Worth one line in a task's verify before the
  build starts; recorded rather than absorbed.
