# STATE

## Current

- feature: FEAT-41-one-station-vocabulary
- run: 2026-08-29-01-product. Replan against the rebased tree. product-lead PASS, ONE send-back
  (its own digest.md was missing six required contract fields; check-state.sh caught it, the lead
  repaired it, `validate-digest.py lead` now exits 0 — I ran it, the lead holds no Bash).
- squad: none
- status: Plan. Nothing signed.
- WHY THIS RUN EXISTED: the branch was rebased onto a main carrying FEAT-42-one-root-resolver,
  FEAT-40 and PR #922 (OMP supervision). Every line anchor, count and quoted snippet in the plan
  was a claim about a file that had moved underneath it.
- COLLISION SURFACE, measured by me: 187 files changed between the old pin e5afc19 and 0d4845b.
  The plan names 57 distinct files; 28 changed. 13 of 14 tasks touch at least one.
- NO PATH RENAME. `.agents/skills` is a tracked SYMLINK to `../.claude/skills` (mode 120000), so
  every `.claude/skills/harness/bin/...` path in the plan is still canonical and was left alone.
  Trap for the next reader: a plan path spelled `.agents/...` can never appear in `git diff
  --name-only`, being beyond a symlink. All four such paths re-mapped and verified unchanged.
- OUTCOME: T-03 CARRY (its two files untouched since e5afc19). 13 RE-DERIVED against current
  source, each surviving anchor re-verified rather than carried. Audit:
  notes/research-FEAT-41-replan-collision-audit.md.
- ONE CLAUSE DEAD. T-10's "close the live INV-26 violation" has no subject: FEAT-40 shipped,
  its feature.json reads Done, check-plan-routes.py skips its plan as shipped, and a full
  check-state.sh run emits ZERO INV-26 lines — I ran it. The violation closed itself by merging.
  T-10's two ship defects survive; the FEAT-40 plan.yaml file, its verify line and its paragraph
  are dropped, and SC-09 is re-based onto the clause that still fails.
- T-14 IS NOT THE CASUALTY it was framed as. Verified BY ME at HEAD: its insertion point in
  check-state.sh is intact (per-feature loop :202, `val()` :227, runs :237-244, INV-6 block
  :246-253) and INV-32 is still free (INV-31 is the highest at BOTH pins). The migration falsified
  its stated REASON, not its instruction — the root now resolves through
  `harness_boundary.resolve_root` with refuse-don't-guess semantics, not CLAUDE_PROJECT_DIR.
  The reason is corrected; the instruction stands.
- THREE VERIFY BLOCKS COULD NEVER HAVE PASSED as written, and are repaired. Two absence-greps were
  satisfied by gitignored `__pycache__/*.pyc` holding the searched string as a compiled constant;
  one globbed over feature dirs and could never return grep's exit 1 (see Q11 — the cause is a real
  shell defect, measured). These were latent before the rebase, not caused by it.
- CLAIM SCHEMA: no task names inflight_registry.py, dispatch-guard.sh or validate-digest.py, and
  none assumed the old claim schema, so nothing was added for PR #922's registry rewrite.
- PIN RE-PINNED, and it now resolves: review_sha is cc009835da1fd6f33a99127bc80d7a1a6075db3d, the
  commit carrying the replanned plan.yaml and BRIEF.md. e5afc19, c056f49 and f3482a0 survive in the
  object db but are NOT in branch history — the rebase rewrote them. `lanes.resolved_at: 0d4845b`
  is deliberately left: lanes were resolved against that tree, and the replan changed no source
  file, so it remains truthful.
- Dangling commit ids quoted inside intent PROSE as historical measurements are deliberately left
  alone. They record what was true when written; rewriting them would falsify the record.
- gates, both run BY ME at this tree: check-plan-routes.py exit 0, "0 violation(s) across 1
  plan(s)", 40 dirs examined and 39 skipped as shipped. check-state.sh exit 1 with exactly ONE
  violation — FEAT-41's unapproved BRIEF — which is correct during a plan phase and closes at
  signature. Its output is BYTE-IDENTICAL to the pre-replan baseline.
- approval: pending in BOTH plan.yaml:7 and BRIEF.md. Not mine to move (DEC-120).
- source_issues: [845, 867], both still open.
- commit: cc00983. Tree clean.
- cycles: 8 of 10 — one send-back this run. runs: 14 of 20.
- briefing: notes/ship-review-2026-08-29-01.md
- next: the operator's signature decision. Q1, Q4 and Q6 below are the blocking conditions.

## Open Questions

- Q1: BLOCKING THE SIGNATURE, carried unchanged. T-12 has an external dependency: the
  decisions-authority triage must land a recording form — in-place clause strike under DEC-188, or
  the correction subsumed into the entry in one voice — before T-12 can be fully executed. It STOPs
  and returns the question rather than guessing. Signing the plan accepts that dependency. This
  audit did not touch it.
- Q2: input for that triage, not grounds to pick here. DEC-188's own text bears on it:
  struck decisions are not deleted from the file, and a partly-overtaken decision routes to
  amended. T-12's three cases are clause-level, so the subsume form is arguably closer to DEC-188's
  own path.
- Q4: RESOLVED by events, 2026-08-29. The INV-26 FEAT-40 violation is gone — FEAT-40 shipped. See
  ## Current; T-10 shrank accordingly.
- Q6: BLOCKING THE SIGNATURE, premise RE-MEASURED BY ME at the new tree and still true. INV-32 as
  T-14 writes it fires on TWO features, not one: FEAT-41 (intended) and
  FEAT-27-expertise-repository-tier, which is Done with PR 574 merged. FEAT-27's pin 9b929de
  resolves and its plan.yaml bytes have moved since; its BRIEF.md has not. Its whole post-pin diff
  is an approval-amendment record plus one task flipping pending->done — legitimate record-keeping
  after a review, not a false review claim. So the moment T-14 executes, check-state.sh goes RED on
  a shipped feature and stays red. T-14 is deliberately silent on four states but NOT on terminal
  stations. Two one-line fixes: scope INV-32 to non-terminal stations — check-plan-routes.py
  already uses exactly that idiom, now reading "examined 40 feature dir(s); 39 skipped as shipped"
  — or repair FEAT-27's pin. The dir count moved 38 -> 40 since this was first measured; the
  finding did not.
- Q7: the precondition "records a validator run" is a LAGGING indicator and inverts the guard. It
  means INV-32 can only fire AFTER a panel has already read the wrong text — which is how FEAT-41's
  own divergence survived. Recommend it become "a real pin exists AND the station is non-terminal".
- Q8: HARNESS DEFECT, unchanged. Nothing allocates run-dir slugs. An earlier run was dispatched
  into a slug the same day's earlier run already held and silently overwrote its digest.md and
  state.yaml; runs/ is gitignored, so the loss is unrecoverable. Recorded in
  runs/2026-08-26-01-product/OVERWRITTEN.md rather than reconstructed (PRINCIPLES rule 15).
- Q9: T-14 traces REQ-07 and pm calls the stretch knowingly. DEC-89 already decides T-14's
  invariant — "a hand edit must never be ignored; it does not inherit a passing review" — and says
  the state check re-pins review_sha. Nothing implements that re-pin; the clause lives only in
  agent prose. So #867 is the unbuilt detection half of an already-decided invariant.
- Q10: NEW, non-blocking, harness defect. Gitignored `__pycache__/*.pyc` defeat every absence-grep
  over the bin directory, because a compiled constant still carries the searched string. Should
  `--exclude-dir=__pycache__` become a standing convention for absence verifies, or should
  run-unit-tests.sh clear the cache first?
- Q11: NEW, non-blocking, HARNESS DEFECT — CONFIRMED BY MEASUREMENT, and I was wrong first.
  pm blamed three unpassable verifies on non-POSIX glob expansion; its lead reserved, and I shared
  the reservation, because the mundane reading (an unmatched glob stays literal) seemed sufficient.
  It is not. Minimal probe in a clean mktemp dir holding only `a/f.txt`, with subdirs `a` and `b`:
  `echo */f.txt` prints `a/f.txt b/f.txt`, and `echo */nomatch.txt` prints both members rather than
  the literal pattern. The shell substitutes PHANTOM pathnames that do not exist, which POSIX
  forbids. Consequence: `grep -rn PAT dir/*/f.yaml` errors ENOENT on every phantom and exits 2 even
  when it finds matches, so `grep ... ; test $? -eq 1` is unusable harness-wide. Confirmed on the
  real tree too: 31 of 40 dirs hold plan.yaml, grep found 56 matches and still exited 2 with 9
  ENOENT lines. I could not file this via xd://report_issue — check-domain denies the orchestrator
  that path — so it travels up in my return instead.
