# STATE

## Current

- feature: FEAT-41-one-station-vocabulary
- run: 2026-08-26-02-product. ONE pm cycle spent adding T-14, closing issue #867 on the operator's
  ruling that the fix folds into this feature. product-lead PASS, 0 send-backs.
- squad: none
- status: Plan
- T-14 (plan.yaml:1253-1354), verified BY ME on disk, not taken from the digest: "Detect a stale
  review_sha, not only an absent one, as INV-32". traces REQ-07, change_type bugfix,
  execution_mode main-session-direct with a DEC-174 reason, depends_on [T-07, T-11], status
  pending, files check-state.sh + test-check-state.py. The verify runs test-check-state.py and
  greps for two named cases - (inv32.a) a stale pin is reported, (inv32.b) a current pin is
  silent - so it can fail in both directions. The silence fixture is built as a REVERT (X, Y, X
  again, pin the first commit), which kills a commit-equality implementation. Stronger than the
  dispatch asked for.
- placement: after T-07 (last task to open check-state.sh) and T-11 (last to open its test), so it
  collides with neither. Appended at the end of tasks:.
- gate: check-plan-routes.py exit 0, 0 violations across 2 plans - I ran it. check-state.sh run
  BEFORE the commit, per AGENTS.md, and BYTE-IDENTICAL to the pre-run baseline: the same two known
  violations (unapproved BRIEF, expected in plan; INV-26 FEAT-40, which T-10 closes). No new
  violation introduced.
- approval: pending in BOTH plan.yaml:7 and BRIEF.md:190. BRIEF.md untouched this run - no REQ-08,
  no SC-14. Nothing signed.
- source_issues: [845, 867].
- PIN STILL STALE, deliberately: review_sha reads e5afc19, plan.yaml now committed at f3482a0. Not
  mine to move this run - the main session re-pins after this lands.
- commit: f3482a0. Tree clean.
- cycles: 7 of 10 - UNCHANGED, 0 send-backs. runs: 13 of 20.
- next: the operator's signature decision on Q6 and Q7 below, then the re-pin.

## Open Questions

- Q1: SIGNATURE CONDITION, non-blocking to the plan. T-12 now carries an external dependency: the
  decisions-authority triage must land a recording form — in-place clause strike under DEC-188, or
  the correction subsumed into the entry in one voice — before T-12 can be fully executed. It STOPs
  and returns the question rather than guessing. Signing the plan accepts that dependency.
- Q2: pm reports DEC-188's own text bears on that triage: DECISIONS.md:5942-5944 says struck
  decisions are not deleted from the file, and :5938-5940 routes a partly-overtaken decision to
  amended. T-12's three cases are clause-level, so form (b) is arguably closer to DEC-188's own
  path. Input for the triage, not grounds to pick here.
- Q3: RESOLVED 2026-08-26. The GAP-7 violation is closed. The operator ruled the review be re-run
  against the committed plan; the panel read plan.yaml and BRIEF.md only via `git show e5afc19:...`
  with no working-tree copy opened and no concurrent pm edit, so review_sha is now pinned to
  e5afc19 truthfully rather than after the fact. check-state.sh no longer emits the GAP-7 line for
  FEAT-41.

- Q4: the second live VIOLATION is INV-26 FEAT-40 parent (issue #842) — plan derives Review, board
  reads Done. This is the exact defect T-10 exists to close, so it is expected and closes on build.
- Q5: does check-state.sh INV-26 flag issue 223 once T-06 routes the compare through project()?
  223 is a parent card, not a task sub-issue. Not run. T-10 now STOPs and reports rather than adding
  the card, so it fails safe either way. Tracked as PB-03.

- Q6: BLOCKING THE SIGNATURE, measured by me by simulating T-14's own stated rule over all 38
  feature dirs. INV-32 as written fires on TWO features, not one: FEAT-41 (the intended catch) and
  FEAT-27-expertise-repository-tier, which is Done, PR 574 merged. FEAT-27's entire post-pin diff
  is an approval-amendment record plus one task flipping pending->done — legitimate record-keeping
  after a review, not a false review claim. So the moment T-14 executes, check-state.sh goes RED on
  a shipped feature and stays red. T-14 is deliberately silent on four states (no git work tree,
  unresolvable sha, no plan file, no validator run) but NOT on terminal stations. Two fixes, both
  one line: scope INV-32 to non-terminal stations — check-plan-routes.py already uses exactly this
  idiom, "examined 38 feature dir(s); 36 skipped as shipped" — or repair FEAT-27's pin. Scoping
  leaves exactly 2 features in scope tree-wide today (FEAT-40 at Review, FEAT-41 at Plan), which is
  the small surface where a pin's claim is actually load-bearing.
- Q7: the precondition "records a validator run" is a LAGGING indicator and inverts the guard.
  FEAT-40 sits at Review with a resolving, byte-current pin and NO validator run recorded, so
  INV-32 skips it. That is the exact window the check should protect: pin taken, pm still writing,
  panel not yet run. Gating on a recorded validator run means INV-32 can only fire AFTER the panel
  has already read the wrong text — which is how FEAT-41's own divergence survived. Recommend the
  precondition become "a real pin exists AND the station is non-terminal".
- Q8: HARNESS DEFECT, not a plan question. Nothing allocates run-dir slugs. This run was dispatched
  into runs/2026-08-26-01-product/, the slug the EARLIER product run of the same day already held,
  and silently overwrote its digest.md and state.yaml. The lost digest is unrecoverable — runs/ is
  gitignored. I moved this run's files to runs/2026-08-26-02-product/ so feature.json's ids resolve
  to the right digests, and recorded the loss in runs/2026-08-26-01-product/OVERWRITTEN.md rather
  than reconstructing it (PRINCIPLES rule 15). The substance of the lost digest survives in this
  file's previous ## Current and in commit c056f49.
- Q9: T-14 traces REQ-07 and pm calls the stretch knowingly; it recommends REQ-08/SC-14 text but
  deliberately did not write it to BRIEF.md. Separately, I found DEC-89 already decides T-14's
  invariant — "a hand edit must never be ignored; it does not inherit a passing review" — and says
  the state check re-pins review_sha. Nothing in .claude, .omp, .agents or .harness implements that
  re-pin; the clause lives only in agent prose. So #867 is the unbuilt detection half of an already
  decided invariant, which is a stronger grounding than the REQ-07 stretch.
