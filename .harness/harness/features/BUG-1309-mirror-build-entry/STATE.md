# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: c18 validate — `runs/c18-validator/` (validator lead, qa evidence + four-reviewer panel,
  **ESCALATE**; the panel gate itself is PASS) and `runs/c18gc-product/` (product lead, pm goal-check
  of SC-04 and SC-11, **ESCALATE**).
- squad: validator, then product. **No production source and no test file changed in this cycle by
  any agent.** The only change under grade is commit `9fe5cf31`, the operator's own additive test
  commit: `tests/integration/test-merge-gate.py`, +37/-1.
- authorization: the operator explicitly chose option 3 of the c17 ruling — ONE additive test-only
  cycle on `tests/integration/test-merge-gate.py` to close SC-04's three evidence gaps. That is what
  this cycle is, and it is the last one the budget allows.
- station: **review** (`plan.yaml` `status:`, unchanged this cycle), T-05 `done`. `plan.yaml`,
  `BRIEF.md` and both approval fields are byte-unchanged — the plan at the pin equals the plan on
  disk (INV-33).
- `review_sha`: **re-pinned to `9fe5cf3112aed6782dfe3f1833b5e7077b31d953`** before any validator ran
  (INV-6). That is HEAD of the feature branch and the commit carrying the test edit. The previous pin
  `b5eb8f8e` predates the edit and would have graded a tree the new cases are absent from.
- mirror: unchanged — parent #1407 and all nine sub-issues (#1408-#1416) are at review from c17. No
  station moved this cycle, so no `gh-sync.py` write was owed.
- budget: **`cycles_used` 16 of `max_total_cycles` 16 — EXHAUSTED.** Incremented by one for this
  cycle: it is an unmet-SC re-dispatch, which is rework under DEC-157. Both leads reported ZERO
  send-backs inside the run. **No further fix of any kind is dispatchable on this feature without an
  operator budget decision.** `len(runs)` 52 of `max_total_runs` 20 — INFORMATIONAL (INV-22); the
  count is high because this feature has run fifteen remediation and grading cycles, and the last
  three each closed a named defect rather than re-treading one.

### The c18 result — two of the three gaps are closed by measurement, a fourth clause was found

- **The suite at the pin: 36 ok, 0 FAIL, `ALL PASSED`, rc=0** captured from a variable, not a pipe
  (`notes/qa-c18.md` section 1). `matrix_ok: true`. Panel PASS, `severity_max: med`, `must_fix: []`,
  all four reviewers ran and each recorded its own verdict on a measured census.
- **Gap A — CLOSED.** `T-05 non-era absent build_entry denies naming feature and re-run command` now
  asserts the conjunction SC-04 states (`"FEAT-9001-fixture-non-era" in reason` AND
  `"gh-sync.py open" in reason`), and it is proven discriminating.
- **Gap C — CLOSED.** All four noise kinds are now fixtured, and each of the four handling arms was
  individually removed from a scratch copy of `merge-gate.py` with the case reddening every time
  (`notes/qa-c18.md` section 3), reproduced independently by the security reviewer.
- **Gap B — the case exists and passes; pm ruled the clause MET, the panel rated the case WEAK.**
  `T-05 duplicate era-exempt claimant still denies before era gate` constructs a genuinely era-exempt
  second claimant (`BUG-1030-stale-anchor-write-hazard`, `feature_schema.py:227`), which is what the
  clause describes. It does **not** redden against an `owners[0]`-keyed era hoist, because
  `glob.glob` returns fixtures in creation order on this filesystem and the non-era fixture is
  created first — measured by qa, by the security reviewer, and independently by the orchestrator.
  pm ruled it MET on SC-04's own text, which — unlike SC-03 and SC-11 — carries no sentence requiring
  an assertion to be reddenable. The remedy, if the operator wants the stronger case, is ONE fixture
  ordering change. **The behaviour is correct in source**: `merge-gate.py:167-181` guards on
  `len(owners)` alone and never on `owners[0]`'s identity.
- **SC-11: MET at this pin.** Nothing in `94b5e465..9fe5cf31` touches a production file, and the
  commit's hunks miss the SC-11 loop entirely, so the `e374c9a2` discrimination recorded at c17
  carries forward (`notes/research-BUG-1309-goalcheck-c18.md` section 3).
- **SC-04: UNMET — on a clause the c17 grading never enumerated.** c17's table split SC-04 into ten
  clauses; c18's pm split it into eleven and found that the ambiguity deny's REASON WORDING has no
  assertion. Verified at both ends by the orchestrator: production emits `Correct the duplicated
  top-level "branch" field ...` at `merge-gate.py:174`, and the only carrying case
  (`tests/integration/test-merge-gate.py:159-163`) asserts the two claimant ids, the absence of
  `gh-sync.py` and run-to-run equality — nothing of the wording. A whole-file grep for
  `duplicat`/`Correct`/`more than one` returns only fixture identifiers. This is **not a regression
  and not a defect**: the behaviour is inspected-correct, the gap is evidence-kind, and it existed
  identically at c17 where the clause table simply had no row for it.
- **UAT Step 3b was NOT amended** — correctly gated off by its own precondition, exactly as at c17,
  because the gate required BOTH SC-04 and SC-11 MET. `notes/uat-BUG-1309-mirror-build-entry.md` is
  byte-unchanged and still carries three commands and a three-line PASS rule at Step 3b.

### Next, in order — the operator decides both steps

1. **Operator ruling on SC-04's remaining evidence gap** (blocking, and the budget is spent).
   Two options, neither the orchestrator's: **accept** the clause-(f) wording gap with a recorded
   ruling — behaviour inspected-correct at `merge-gate.py:174`, gap is evidence-kind only — and let
   SC-04 read met; or **defer** it as a follow-up bug for the one-line conjunct
   (`"Correct the duplicated" in reason`) and hold SC-04 unmet. A third choice rides with it: whether
   to also take the gap-B fixture ordering change into that same follow-up.
2. **SC-10, the hand test**, `notes/uat-BUG-1309-mirror-build-entry.md`. It is runnable exactly as
   the file stands; SC-10's pass rule at `:337-340` names Steps 3, 3b, 5, 6 and 7 and is unchanged.
3. **Only if the operator accepts on step 1** does the UAT Step 3b amendment become dispatchable —
   one pm spawn through product lead, adding the `-F`, `--cleanup strip` and global `--attr-source`
   forms measured as denies at this pin (`notes/qa-c18.md` section 5,
   `tests/integration/test-merge-gate.py:219-221`) and moving the step's rule from three lines to six.
4. Then the rewritten briefing, then the ship decision. The stale briefing at
   `notes/ship-review-2026-09-08-resume.md` and its B-1..B-13 backlog still await disposition.

## Open Questions

- Q1 (blocking, operator) — **SC-04 clause (f): the ambiguity deny's wording has no automated
  assertion, at an exhausted budget.** Accept with a recorded ruling, or defer as a follow-up bug.
  Verified at both ends by the orchestrator, not taken on the digest's word.
- Q2 (non-blocking, operator, rides with Q1) — the gap-B case is a behaviour witness, not a defence:
  it survives an `owners[0]`-keyed era hoist because this host's glob order never seats the
  era-exempt claimant first. One fixture ordering change fixes it. No budget this cycle.
- Q3 (non-blocking, UAT coverage) — the UAT script has no step exercising the duplicate-claimant
  ambiguity scenario at all. Pre-existing, untouched by this diff, relevant to any future Step 3b work.
- Q4 (non-blocking, harness defect, 5th and 6th sighting) — an agent returned a complete, well-formed
  fenced digest while the host recorded `failed (exit 1) — subagent called yield with null data`.
  Seen this cycle on the security reviewer and on the product lead itself; previously on the c17
  panel qa step, the c15 ui step and two pm runs. A tier routing on the exit code alone discards a
  PASS carrying a full mutation sweep.
- Q5 (non-blocking, harness defect) — `bash-write-guard.sh` blocked `cp` and shell redirection for a
  read-only role but did not block `python3 -c "open(path,'w')"` run through bash.
- Q6 (non-blocking, backlog) — T-05's `verify:` grade assertion takes `min(grade)` over
  `git_merge`/`words`/`direct_merge`/`gh_merge` and never names `option_end`, `first_subcommand` or
  `merge_target`. Satisfied in fact (5/5/4); the remedy edits approval-gated `plan.yaml`.
- Q7 (non-blocking, backlog) — `merge_target` matches `--abort`/`--continue`/`--quit` by exact token
  equality while git accepts unambiguous abbreviation, so `git merge --abo` would be DENIED.
  Direction is over-deny, never a bypass. Partly measured; `git merge --abo` itself is unmeasurable
  from inside a run because `bash-write-guard.sh` refuses the command name.
- Q8 (non-blocking, plan hygiene, pre-existing) — T-05's enumerated case-name contract lists 21 names
  while `verify:` gates 26; the five D-13/D-14 names never reached the enumeration.
- SC-10 UAT is still NOT executed and still blocks the ship.
