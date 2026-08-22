# STATE

## Current

- feature: FEAT-31-orchestrator-context-watch
- run: runs/fix1-eng (PASS, complete) · squad: eng · phase: **build COMPLETE for the team lane**
  (phase recorded HERE; DEC-192 deleted it from feature.json, Q5 is issue #635)
- status: **AWAITING THE OPERATOR** — every team task not blocked on a main-session-direct task is
  done. Handoff: `notes/handoff-build.md` (seq-2, at `b2f7c73`) — **read it before acting.**
- briefing: `notes/ship-review-fix1.md` (+ rendered `.html`)
- budget: **cycles 4/10**, runs 9/20. Runs are INFORMATIONAL (INV-22); cycles are the hard bound.

**BOTH GATES PASS** — `BRIEF.md` and `plan.yaml` read `approved` / `operator` / `2026-08-21`.
Q-SIGN CLOSED (`notes/signature-reaffirmed-18-tasks.md`).

### TEN OF EIGHTEEN TASKS DONE AND VERIFIED, committed at `b2f7c73`, tree clean

T-01, T-02, T-03, T-06, T-07, T-08, T-11, T-13, T-16, T-18 — `status: done`, sub-issues closed.
**Each re-verified by the orchestrator against its own `verify:` block, not accepted from a digest.**

**THE OPERATOR'S TWO BLOCKERS ARE CLEARED.** T-16: 21 named cases, `.claude/settings.json`
**zero-diff** so D-24 holds. T-18: `harness.json` diffed key-by-key, exactly ONE key changed.
**T-17 is unblocked.** T-07's `run-unit-tests.sh` append also landed — one entry, nothing removed,
order preserved — so that contended file is settled and T-17 may append safely.

### THE TWO STANDING DEFECTS ARE FIXED. This was cycle 4.

1. **Discovery was ONE LEVEL TOO SHALLOW.** Fixed at 3 production sites and in every fixture.
   One-level glob **0**, two-level **2012**, of which **105** are `harness-orchestrator`. The tool
   now returns **105 rows**, matching an independent glob count exactly.
2. **`_build_row` contradicted D-11** — appended 0 for lines with no `message.usage`, took `current`
   from the file's last LINE not the measured set's last MEMBER, counted `entries` as all parsed
   lines. Fixed.

**SC-01's LIVE HALF IS DISCHARGED.** `verify-context-watch-live.py a7783f0ec41e6a8c6` reports tool
and independent recomputation agreeing exactly at **current 696,472 / peak 696,472 / entries 669**;
that peak matches `BRIEF.md:43` to the token, reproduced a third time by the orchestrator. Unit
**76/76**, integration **10/10**, both exit 0, zero MISCONFIGURED. **Depth is now pinned in BOTH
directions** (L1/L2), and all four mutant proofs assert the mutation APPLIED and that real and
mutant results DIFFER.

**WHY 65 GREEN CASES SAW NEITHER: the tool, the tests and the fixtures were built in the same wrong
shape, so they agreed with each other and disagreed with reality.**

**THE ORCHESTRATOR'S OWN ERROR, ON THE RECORD.** I re-ran T-01's verify block, saw both lines exit 0,
and recorded T-01 `done` — while this file's own heading said both defects STILL STAND. I trusted a
green gate over the written record, which is the failure this feature exists to close. T-01 and T-02
were reverted to `building`, fixed, and only then recorded done.

### WHAT REMAINS, AND NONE OF IT IS THE ORCHESTRATOR'S TO START

- **The operator's six** under DEC-174: T-04, T-10, T-12, T-14, T-15, T-17.
- **T-05 and T-09 are mine but BLOCKED on T-04** — the template still lacks
  `orchestrator_context_warn_tokens` at `b2f7c73`, so T-04 has not landed.
- **Three of ten requirements are exclusively main-session-direct**: REQ-04 (T-15), REQ-09 (T-14),
  REQ-10 (T-10, T-14). **The goal-check CANNOT pass until the operator's tasks land.**
- qa gate, SIMPLIFY, `review_sha` pin, review panel, goal-check, close-out: all after the tree is
  complete. `review_sha` is still `""` — pin it at dispatch time, never at turn start.

### Premises the next cycle must not re-derive — the rest are in `notes/handoff-build.md`

- `feature-worktree.py behind --repo harness --id FEAT-31` exits **0** — **run it from the PRIMARY
  checkout**; from inside, `dest_for()` re-inserts the path and it exits 3 on a tree that is fine.
- **Zero UI surface** — all 21 planned files are Python, shell, JSON or markdown; ui-reviewer
  self-scopes out.
- **Q-CHECKCOUNT CLOSED, benign**: 78 static `check(` sites vs 76 executed; the two unexecuted are
  lines 668-669 in case J's `INCONCLUSIVE` branch, dead because the mutation applied. Settled with
  `sys.settrace`, not inference.
- **The `bash-write-guard.sh` heredoc hazard is FALSE** — a read-only `python3` heredoc with `>` and
  `>=` runs CLEAN. **`.harness/teams/build.yaml` DOES NOT EXIST.**
- 14 SCs, SC-01..SC-11 and SC-13..SC-15 — **there is no SC-12**.
- `runs/build2-eng/digest.md` reached disk missing 3 contract fields its return carried; completed
  from that return, `validate-digest.py` now passes. `runs/plan3-product/digest.md` is an
  **incomplete stub** (IN PROGRESS, no verdict).
- Two board cards (T-01 #642, T-02 #643) read Building though closed and done — `close-task` re-run
  twice did not move them. Documented mirror shape: never re-attempted, never a gate.

## Open Questions

<The channel from subagents to the user. A non-empty entry is an ACTIVE ROUTING
SIGNAL, not a note: the orchestrator asks the user, writes the answers to
.harness/harness/features/<FEAT>/notes/answers-<runid>.md, and re-delegates with that path. Clear
each entry when it is answered.>

- **Q-HOOKCTX, BLOCKING AT T-17, THE OPERATOR'S TO SETTLE.** Unverified: that hook stderr reaches
  the model as CONTEXT rather than only as a tool-result error string. **If false, SC-13 is not met
  by this design and T-17 needs rethinking, not just writing.**
- **Q-T13VERIFY, NEW, non-blocking, PM.** T-13's *signed* verify line 6 is VACUOUS — it greps
  `not found` against a nonexistent projects dir, matching an early-return branch, so
  `_find_agent_paths` (where Defect 2 lived) never runs. It is the assertion that should have caught
  Defect 2. Fourth green-and-incapable-of-red instance here. A compensating control now exists, so
  this is a plan re-anchor, not a blocker.
- **Q-FOOTERSCOPE, NEW, non-blocking, PM.** On a ONE-ARGUMENT invocation the footer mixes scopes:
  rows narrow to the single match, but blind-spot lines 1-2 re-walk the WHOLE corpus. Lands on SC-10
  step 2. T-08's intent does not define filtered scope, so choosing one is pm's.
- **Q-IRONLAW, non-blocking, FOR QA AND THE PANEL.** The fix applied code BEFORE writing its new
  assertions — a RED-first deviation the lead volunteered. Judged sound because all four mutants
  deliver a COUNT differential against the exact pre-fix shape, independently rebuilt by a second
  member. Carried forward, NOT waived: TDD ordering is qa's and the panel's to weigh.
- **Q-DIRFAILOPEN / Q-FOOTERPERF, non-blocking tool findings.** `_safe_listdir` swallows `OSError`,
  so an unreadable DIRECTORY silently drops its subtree (REQ-07 covers sidecars and transcripts, not
  directories). The footer's second corpus read is ~49% of wall clock (0.80s vs 0.41s) — sub-second
  at 105 orchestrators, so rule 12 says leave it; narrowing the scan would break REQ-05.
- **Q-RUTSH, non-blocking, RESOLVED IN PRACTICE.** `run-unit-tests.sh` had THREE writers, not two.
  T-07 landed cleanly, so the file is settled — **T-17 and T-12 append only.**
- **Q-VACUOUSFLOOR, non-blocking, GENERAL.** Any `verify:` floor from a PREDICTED assertion count is
  vacuous. T-16's `-ge 22` was satisfied at 29 before T-16 wrote a line. Verify by case NAME.
- **Q-D21, non-blocking.** ` ##` opens a YAML comment in a plain scalar — cost D-21 299 invisible
  characters, invisible to `safe_load` and every gate. Worth a corpus check for the same shape.
- **Q-DEC90, non-blocking.** `DEC-90` is STRUCK (`DECISIONS-INDEX.md:109`) but `BRIEF.md:247` cites
  it as a live `BLOCKS` constraint. Only the operator edits an approved BRIEF.
- **Q-BRIEF231, non-blocking.** `BRIEF.md:231-237` says SC-07 changes `check-domain.sh`'s write
  route. Measured false — `:815` already calls `feature_schema.problems_for_text` (D-23).
- **Q-ANCHOR, non-blocking.** DEC-174 content is at 4859-4862 and 4864-4867; the plan cites
  4851-4854 and 4856-4859. `lanes.resolved_at` still `7299669`.
- **Q-GUARD, non-blocking, SCOPE CORRECTED.** Heredoc half DISPROVEN; the real defect is `sed -i`
  with a shell-variable target refused as out-of-domain.
- **Q-COLLECT, non-blocking, RECURRED.** A lead force-closed with its member in flight; the member
  outlived it and wrote an unassessed artifact. Mitigation: confirm liveness from the sidecar
  transcript, never re-dispatch, verify mechanically.
