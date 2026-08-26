# Orchestrator measurements — FEAT-41 — 2026-08-25, at ee66ae2

Taken by harness-orchestrator to sharpen two of pm's open questions before they reach the
user. Both are my own measurements, not pm's claims.

## Q4 — the cost of D-07's new PreToolUse Bash gate

pm estimated "roughly 40 ms per Bash call". MEASURED, 10 runs each, this worktree, warm cache:

- bare `python3 -c pass`: min 15.8, median 16.4, max 20.7 ms
- `gh-close-gate.py` fed a Bash payload — the script D-07 explicitly models the new gate on:
  min 25.8, median 26.2, max 30.2 ms

So the real marginal cost is about 26 ms, not 40. pm's figure was conservative by roughly
half. This makes D-07 cheaper than the plan states, not more expensive.

## Q2 — the glossary note

pm's premise is correct and the path in DECISIONS-INDEX.md's summary is not.

- `check-state.sh:879` tests `os.path.isfile(H + "/glossary.md")` — that is
  `.harness/glossary.md`, NOT the `.harness/codebase/glossary.md` the index row for DEC-162
  names.
- Neither path exists on disk. `.harness/codebase/` does not exist at all.
- The note fires in my own full `check-state.sh` run: "no .harness/glossary.md — the domain's
  ubiquitous language is unrecorded (DEC-162)". It is a WARN, not a VIOLATION.
- It fires independently of this feature and predates it. Nothing FEAT-41 does causes or
  clears it.

Read: this does not gate, and adding a glossary task widens #845 past its seven items for a
warn that exists with or without this feature. Backlog row, not a task — but the scope call
is the operator's.

## INV-26, the in-scope violation

Confirmed live by my own `check-state.sh` run at ee66ae2:
"VIOLATION INV-26 FEAT-40-harness-writes-done parent (issue #842): the plan derives Review —
the board reads Done." SC-09 is the criterion that closes it.

---

# Verification of the eng squad's blocking findings — orchestrator, at ee66ae2

I checked the premise of every finding that would cost a cycle before routing it (P-06).
Four checked, four CONFIRMED. None was routed on the reader's word alone.

- **F-02 CONFIRMED.** `grep -n -- "--all" check-plan-routes.py` returns ZERO hits. The flag
  does not exist. T-04's verify would pass `--all` as a path.

- **F-04 CONFIRMED, and it is the worst of the nine.** `check-state.sh` circa 1403-1405 reads
  `_EXPECT = {"building": ..., "done": ..., "pending": _st26["backlog"]}` and circa 1475-1477
  reads `_want = _EXPECT.get(_tstat.get(_tid, "pending"))` then `if _want is None: continue`.
  That IS a fail-open. After T-04 renames `pending` to `ready`, `_EXPECT.get("ready")` returns
  None and INV-26 stops checking every not-started card SILENTLY. No task in the plan lists
  check-state.sh for this.

- **F-03 CONFIRMED.** `_renamed` and `_no_finding` are defined inside the 1660-1680 span but
  USED at roughly 1673, 1681, 1687 and 1690 — outside it. Deleting 1660-1680 leaves NameErrors,
  and a `"Shipped"` literal survives past 1687 which would red T-11's own grep. The lead's
  corrected span (1655-1691) is right; the 1660-1680 span in my own dispatch was wrong.

- **F-01 CONFIRMED, with one addition the readers missed.** Unanchored, T-04's grep returns
  **72** hits across the live plans; the four-space anchor returns **55**, matching the reader's
  count. THREE of the excess are approval blocks, not two: FEAT-19/plan.yaml:5,
  FEAT-28/plan.yaml:5, and **FEAT-41's own plan.yaml:7**, which the finding does not name.

## The eng lead's Q1 — SETTLED by measurement, and far worse than it could see

It had no Bash and asked whether the executing checkout exposes `.claude/worktrees/`. It does.

- The worktree checkout has NO `.claude/worktrees/` directory.
- The MAIN checkout does.
- T-13's verify is `grep -rn "plan-merge" .claude .omp .agents ... ; test $? -eq 1`, which
  demands ZERO hits. Run from the main checkout, `.claude` yields **10 live files and 338 files
  under `.claude/worktrees/`**.

So T-13's verify reds on a correct execution by a factor of 34, and the failure depends on
WHICH checkout the main session runs it in — which is exactly the kind of silent, location-
dependent break this feature exists to end. The grep needs an explicit worktree exclude, not a
narrower path list.

## Q5 — amend vs strike. The precedent has a SHAPE, and I read it.

pm's D-09 proposes to AMEND DEC-203 section 6, DEC-191 and DEC-182, citing DEC-138 am.7/am.8 as
the nearest precedent. I opened that precedent. Its actual form, in DECISIONS.md's own words
inside the surviving DEC-138 entry:

  "The `absorbs:` citation that recorded this is STRUCK 2026-08-25 under DEC-188 —
   see amendment 7."

So the established form is NOT amendment. It is an IN-PLACE CLAUSE STRIKE inside a surviving
entry, carrying a pointer to the amendment that replaced it. The entry lives; the dead clause
stays visible and marked dead.

Why the difference is not cosmetic: under an amendment, a reader who cites the old clause finds
it silently rewritten and cannot tell it ever said otherwise. Under the strike form the citation
still resolves AND announces that it no longer holds. DEC-188's rule is "STRUCK, never marked
stale" precisely so the record cannot quietly change under a citation — which is the same
failure mode, one level up, that this whole feature exists to end.

MY READ: D-09 should take the clause-strike form, not the amend form, and pm's own cited
precedent is the argument against pm's choice. This is a record-shape call on three SIGNED
decisions, so it is the operator's to settle and pm's to author. I am not settling it.

## The route gate, run against the AMENDED plan — orchestrator, post-repair

Nobody had run this against the repaired file, and DEC-183 makes it part of the required
`integration` CI job, so a failure here would surface after signature rather than before.

Command: `python3 .claude/skills/harness/bin/check-plan-routes.py`

Result: exit code 0. "0 violation(s) across 2 plan(s)". "examined 38 feature dir(s); 36 skipped
as shipped". 13 DEVIATION lines across both plans.

DEVIATION is not VIOLATION. Each one reads "granted to <team agent> but declared
main-session-direct" — the DEC-174 carve-out doing exactly what it should: the surface IS
grantable to harness-backend-dev or harness-dev-ops, and the plan deliberately declines the team
lane because the file is an enforcement-path file. The checker notices and does not object.
Several OK lines are the other shape — genuinely ungranted surfaces (.claude/settings.json,
.omp/agents/**, the templates) where main-session-direct is forced rather than chosen.

Read: the plan's lane block is internally consistent with the guard's own resolution, verified BY
the guard rather than by argument. This does NOT verify the lanes are RIGHT — DEC-174 is a
judgement the operator signs — only that nothing in the plan claims a lane the guard would refuse.

Incidental: this section was first written with an ASCII arrow, and bash-write-guard.sh read the
arrow inside the heredoc BODY as a shell redirect and denied the write ("redirect targets EXIT").
A false positive on heredoc content. Reworded rather than worked around.

## Run digests are EPHEMERAL. Notes are the durable record. Measured.

`.gitignore:7` ignores `.harness/*/features/*/runs/**`, so every run dir — including every
`digest.md` a briefing cites as its evidence — is worktree-local and never enters the tree.

Checked against real features rather than inferred:
- FEAT-35 (merged, worktree removed): `runs/` does not exist in the main checkout. `notes/`
  does, carrying answers files and both handoff notes.
- FEAT-40 (in flight): `runs/` does not exist in the main checkout either.

Consequence for THIS feature: the four run digests I assessed are readable now, inside the
worktree, and will not exist after the worktree is removed. Anything that must outlive the
worktree has to be in `notes/`, which is why the verifications in this file are here and not
left in a digest.

This looks like a real gap rather than a deliberate design: the orchestrator playbook's CEO
briefing step directs the author to cite `runs/<run-dir>/digest.md` BY PATH as the disclosure
that the briefing is complete, and those paths are dead the moment the checkout goes. Raising it
as an open question rather than working around it.

## Final gate state at plan-phase close

`bash .claude/skills/harness/bin/check-state.sh` exits 1 with exactly two violations:
1. "FEAT-41 BRIEF.md is NOT approved — halt that flow and surface to the user." This is the
   CORRECT terminal state for mission plan. The checker is naming the handoff I am performing.
2. "INV-26 FEAT-40 parent (issue #842): the plan derives Review — the board reads Done." The
   known, in-scope defect. T-10 closes it and SC-09 asserts the closure.
Plus one note: FEAT-41 plan.yaml approval is pending, awaiting the user.
The earlier "has STATE.md but no BRIEF.md" violation has cleared.

## Ruling 1: how many features ACTUALLY move. My independent measurement.

The operator declined to carry "28" forward unchecked and told pm to measure. I measured
independently so pm's number can be checked rather than received.

29 `plan.yaml` files on disk. 28 of them are features other than FEAT-41, which is almost
certainly where "28" came from — it is the count of OTHER PLANS, not the count of features that
MOVE.

Features carrying any task at `pending`, which is the only status ruling 1 repoints:
  FEAT-10 (11 pending, feature Done)
  FEAT-12 (14 pending, feature Done)
  FEAT-13 (2 pending, feature Done)
  FEAT-15 (5 pending, feature Done)
  FEAT-19 (7 pending, feature Abandoned)
  FEAT-28 (3 pending, feature Abandoned)
  FEAT-41 (13 pending, this feature)

So SIX existing features carry a pending task, not 28 — and every one of the six is Done or
Abandoned. The other 22 carry only `done` tasks, which ruling 1 does not touch.

The consequence worth pm's judgment: the one-time gh-sync pass may need to move ZERO cards that
matter. A Done or Abandoned feature's sub-issues are terminal; bringing their stale `pending`
cards up to Ready would move cards BACKWARD into an active column on features that are finished.
That is not what ruling 1 asks for and would be a worse board than today's.

I am NOT overriding the ruling — the ruling is that plan.yaml and the board must agree with no
exception, and that stands. What I am flagging is that its stated cost ("28 features") is roughly
five times the real live surface, and that the pass probably needs to EXCLUDE terminal features
rather than sweep all of them. pm owns that judgment; I am supplying the measurement.

## The code-review pass: what I settled, and one error of my own

### Its blocking Q1 is answered at my rung. Nothing is signed.
harness-code-reviewer asked whether SIGNED success criteria (SC-05, SC-07) may be amended in the
same pm pass as task intent, or whether that needs its own operator ruling. The premise is false:
BRIEF.md:174 reads `status: pending` and the operator has stated they will not sign until this
revision lands. The SCs are DRAFT. pm may edit them freely. No ruling required, and I did not
spend an operator round-trip on it.

### F-1's mechanism claim is CONFIRMED, and the source documents the hazard itself.
check-domain.sh at roughly 1161-1167 carries this comment in its own voice:
"ONE ROUTING SENTENCE PER FINDING, which is why this does not call deny(): deny() appends the
module-level ROUTING constant, speaking about STATE.md, digests and notes/ ... Two routing
sentences in one stderr stream contradict each other about the same file class."
So the file already knows deny() emits state-file routing advice. An orchestrator blocked from
recording a task station via deny() would be told to put it in STATE.md. F-1's remedy — forbid
deny(), use _head with plan.yaml's own routing sentence — matches what three existing branches
already do.

### An error of mine, recorded because the record must carry failures.
I ran a safe_load against plan.yaml WHILE harness-pm was mid-edit and got
"yaml.scanner.ScannerError: mapping values are not allowed here, line 83". I did NOT report this
as a defect, because it is almost certainly a torn read of an in-flight write. Two dispatches
earlier I warned harness-code-reviewer about exactly this hazard and told it to treat
half-written passages as in-flight rather than filing them. I then did the thing I warned against.
STATUS: UNVERIFIED. plan.yaml must be re-parsed after pm's run closes, and if it still fails at
line 83 that is a REAL defect that blocks signature.

## AMENDMENT to Ruling 2 — HOLD. Received after cycle 6 was already dispatched.

The operator wants struck decisions REMOVED from DECISIONS.md outright and amendments subsumed in
place, because "struck" does not today mean deleted — eight entries are marked STRUCK and still
sit in the file. That triage is SEPARATE WORK and is NOT FEAT-41's. Do not plan it here.

What changes for FEAT-41, narrowly:
- DO NOT write the three clause strikes (DEC-203 s6, DEC-191, DEC-182) yet.
- KEEP T-12 and keep its scope. Each of those three entries has one clause this feature
  contradicts and that must still be recorded somehow.
- T-12's text must make the RECORDING FORM a NAMED OPEN DEPENDENCY: in-place clause strike under
  DEC-188, versus subsuming the correction into the entry in one voice. The decisions-authority
  triage decides; T-12 executes whichever form lands.
- D-09's `because:` must say the form is PENDING, name both candidates, and say why it is pending
  — not silently swap the choice.
- Rulings 1, 3, 4 and 5 are UNCHANGED.
- This does NOT block signature. The signature covers the TASK SET; the form is a documented
  dependency inside one task. Do not wait on the triage.

TIMING PROBLEM, recorded honestly: cycle 6 was already dispatched when this arrived, and I have
NO SendMessage tool — Read, Agent, Write and Bash only. So cycle 6 is running against the
pre-amendment understanding. Its return is NOT the final state of T-12. A further cycle must
apply this hold. Anyone reading cycle 6's digest alone will believe ruling 2 is settled. It is not.

## SINGLE-FLIGHT CLAIM ON harness-pm — DO NOT CLEAR IT

As of 03:49:40Z a harness-pm dispatched by a DIFFERENT product-lead is live in the session
registry, claimed against this same repo root. It belongs to the decisions triage, not to FEAT-41.

If our product-lead hits a single-flight refusal on harness-pm, that is the cause. REPORT IT
UPWARD. Do not clear the claim.

NEVER run `inflight_registry release-all`. Clearing a live claim admits a second pm onto the same
output path, which is issue #551 exactly — two writers, one file, and the second erases the first.
This is written down because it is precisely the instruction a context-pressed successor would
talk itself out of.
