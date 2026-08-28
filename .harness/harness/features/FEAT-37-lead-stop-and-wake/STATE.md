# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: runs/2026-08-27-01-t09-docs-product/digest.md
- squad: none — qa segment next
- status: building

**ALL SIX TASKS ARE DONE. T-09 LANDED.** Runs 16/20, four remain. Cycles 1/10 — the T-09 run had
ZERO send-backs, so nothing was added. Numbering is NOT compacted; the gaps are deliberate.

**T-09'S DELIVERABLE IS GOOD AND ITS SIGNED GATE IS BROKEN. Both halves are true and the record says
so rather than choosing one.** The task's `verify:` calls `gen-decisions-index.py --check`. That flag
has never existed — the script's own docstring says "There is no --check" and it exits 2 on any
argument but `--stdout`. So `index=2` is an unrecognized-argument refusal, NOT index drift, and
`T09_FAIL` grades the flag rather than the work. I re-ran both halves myself instead of taking the
lead's report: the drift check the docstring AND SC-06 both prescribe,
`gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md`, exits **0**, and the scope grep
already exited 0.

**Why T-09 is recorded done and not held.** The property the broken clause meant to gate is gated
anyway, by SC-06, which names the `--stdout | diff -` form in its own text and is graded at the
goal-check by its declared method. Nothing is waived: a defective clause is recorded as defective,
and the criterion that actually governs still runs. Amending the clause is pm's and the operator's,
and it is carried up rather than done here.

**I VERIFIED THE EDIT MYSELF against all four rejection conditions** — zero exclusion language (the
body states the eval kind "stays required wherever the scope above holds"), no level-3 heading and no
Amendment form, all three scope terms present, index row regenerated not hand-edited. The documentor
also widened DEC-70's HEADING, not only its body; accepted at this tier as serving D-09's
subsume-in-place intent, and citations resolve by number so nothing breaks.

**THE DOCS SWEEP FOUND A THIRD ONCE-ONLY SITE THAT SC-07 DOES NOT GRADE.** `SPEC.md` carried
"Enforcement is exactly one rejection deep", corrected in place to the measured
per-consecutive-stop-sequence bound. SC-07 covers only `DECISIONS.md` and `inflight_registry.py`, so
this site would have shipped falsified with every criterion green. The sweep's second fix narrowed
SPEC's `ai_behavior` matrix row to match DEC-70.

**Q5 IS AN INSTANCE OF Q7, MEASURED, NOT A NEW DEFECT.** The lead's stop was refused naming a
`harness-pm` it never spawned. The in-flight registry is a SINGLE file at the OUTER checkout root,
`/Users/molchairuangutai/GitHub/harness/.harness/.inflight-claims.json`, shared by every worktree and
every concurrent context — so an unrelated actor's live child is attributed to whoever tries to stop.
The lead holds no Bash and could not see this; I read the path and the file.

**STILL AHEAD, AND THE QA SEGMENT MUST ANSWER ONE THING EXPLICITLY.** `harness.json`
`test_matrix.ai_behavior.always` is `["eval"]` and T-02 is `change_type: ai_behavior`;
`test_kinds.eval` is `cmd: null` / `status: unresolved`. T-09 changed NO config — it rewrote DEC-70,
the decision that CREATED that row, and SPEC's copy of it. The row is applied by qa READING it, not
by any script, so the narrowing reaches the enforcement point. qa must say plainly whether the row
still blocks rather than inventing a pass.

**SIMPLIFY IS OMITTED DELIBERATELY.** The feature's whole non-documentation surface is 661
insertions, 641 of them the one new test file, whose structure is pinned by SC-03's six-fixture
discrimination requirement. The spare run is held for a FAIL. Disclosed to the operator, not dropped.

## Open Questions

- Q1 (was: the eval's author) — CLOSED by the strike. No eval, no author.
- Q2 (was: the grader firing one rule alongside others) — MOOT. The grader is unwound.
- Q3 (the route checker validating against the wrong config) — folded into issue #910 as scope, by
  operator ruling. Not this feature's work.
- Q4: `notes/root-cause-*.md` is in no member's domain, so debug reports fall back to receipt paths.
- Q5: engineer DIGESTs carry no `files_touched`, so a member that wrote a receipt reported no files.
- Q6 (the #866 deadlock) — half closed by FEAT-42. The dispatch end is fixed; the return end is what
  this feature corrected. This feature does not close #866 and never claimed to.
- Q7: single-flight is keyed per checkout, so several orchestrators' children can share one registry.
  CONFIRMED by measurement 2026-08-27, and Q5-of-the-t09-run is an instance of it: the registry is one
  file at the OUTER root, `.harness/.inflight-claims.json`, shared by every worktree.
- Q8: a lead holds no `SendMessage`, so a finding made after dispatch cannot reach a member in
  flight. That is D-03's deliberate consequence, not a defect to fix here. Backlog.
- Q9: the `gates` block in `harness.json` — `qa_gate`, `review`, `uat`, `merge` — is read by NO
  script. Agents honour it as prose. Folded into issue #910 by operator ruling.
