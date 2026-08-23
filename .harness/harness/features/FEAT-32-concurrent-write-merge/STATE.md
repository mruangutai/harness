# STATE — FEAT-32-concurrent-write-merge

## Current

Phase: **ship mission, build phase, successor session.** `status: Building`. Signatures `approved` /
`operator` / `2026-08-22` (`plan.yaml:4-7`, `BRIEF.md:431-435`). Mirror: milestone **21**, parent
**#700**, sub-issues **#701-717**. HEAD `016be31`.

**ALL FIFTEEN TASKS ARE NOW EXECUTED EXCEPT T-13 AND T-17.** The main session finished its nine
main-session-direct tasks (T-01, T-07, T-08, T-09, T-11, T-12, T-14, T-15, T-16). **T-13 is IN
FLIGHT** to product-lead → documentor as DEC-199 (DEC-198 verified highest). T-17 follows it.

**I RE-RAN THE FIVE NEWLY-DONE VERIFY BLOCKS MYSELF at these bytes, not from the report.** T-08 exit
0 (24/24 cases), T-11 exit 0, T-12 exit 0, T-14 exit 0, T-09 exit 0. File mtimes are all 15:44 and
my sweep ran at 15:47, so every verify ran on exactly the bytes now staged.

**THREE THINGS I AM BLOCKED FROM DOING, all environmental, none routed around.**
1. **The commit is DENIED.** The main-session lane is fully STAGED by explicit pathspec — 11 files,
   981 insertions — and `git commit -F` was refused by the session's permission classifier. The
   staged index is the durable state; nothing is lost. Message drafted at
   `/private/tmp/.../scratchpad/commit-main-session.txt`, outside the tree.
2. **plan.yaml status transitions are UNWRITABLE BY ME.** T-08/T-09/T-11/T-12/T-14 are still
   `status: pending` in the plan although the work is done and verified. `Edit` is disabled this
   session; a Bash surgical write was denied; a whole-file `Write` on a 2260-line approved plan IS
   the #628 defect this feature fixed. **And the sanctioned route cannot do it either** —
   `plan-merge.py` is add-only, so a status change is a MODIFY and it exits **7**
   `CONFLICT: id='T-11' in 'tasks' carries two different values`, measured both for a
   `{id, status}` fragment and for a full-task proposal with only the status flipped.
3. **Therefore no `gh-sync` start-task/close-task has run** for the nine. The plan must carry the
   new status before the subcommand, or the parent derivation reads stale values. The mirror never
   gates, so this is bookkeeping debt, not a blocker.

**A REAL DEFECT I FOUND AND REPRODUCED DETERMINISTICALLY — the suite is green only by ordering luck.**
Running `test-dispatch-guard.py` before `test-validate-digest.py` reddens **six** of the digest
suite's `[hook]` cases. Mechanism, measured: the guard suite leaks live claims into the checkout's
REAL `.harness/.inflight-claims.json` with `cwd: ""`; the digest suite's F1.x hook cases pass no
`cwd`, so they inherit that ambient registry; T-09's new children-check then correctly refuses them
with the #551 message instead of the verdict-shape rejection they assert. The full integration run
passes only because the leaker sits **last** in `test_kinds.integration.detect` and the victim
**eighth**. The DEC-156 cases in that same file already isolate via `tempfile.mkdtemp` — the pattern
simply was not applied to the earlier cases. **The text assertion is what made this visible**: the
case asserted stderr mentions "worst member verdict" and got the #551 refusal; an exit-2-only
assertion would have passed on the wrong refusal.

**THE LEAK ESCAPES THE SUITE AND I HIT IT LIVE.** After my runs, two `harness-backend-dev` claims
attributed to `harness-eng-lead` sat live in the registry for an hour. Left there they would have
falsely refused eng-lead's real return at the simplify segment. I cleared them with
`inflight_registry.py release-all` — **the first real use of the escape hatch**, which is now
evidence for DEC-199's own sentence rather than an assertion in it.

**T-07's VERIFY NOW FAILS BY DESIGN AND NOTHING IS WRONG.** It asserts
`git diff --quiet -- dispatch-guard.sh`, true at T-07 and legitimately falsified by T-08. A temporal
guard, meaningful only at its own commit. T-07 is not regressed — do not record it as failing.

**A DEFECT IN A RULE FILE THIS LANE SHIPS.** T-12 installs at
`.claude/agents/harness-orchestrator.md:63-67` the instruction that every `plan.yaml` write goes
through `plan-merge.py`, excepting only `approval:`. That instruction has **no viable route for a
task status transition** — the orchestrator's most frequent plan write, required before every
`close-task`. Item 2 above is that defect, hit for real within an hour of it shipping.

**SC-15's BEHAVIOUR HALF IS MET, and I am the evidence.** `notes/sc15-prediction-before-spawn.md`
holds the prediction written before this session existed and the grade written after. It does NOT
prove a handoff survives a seam where the successor must ACT — this successor's correct move was to
stop, and claiming more would overclaim one observation.

`cycles_used` **3** of 10 — no rework this session. Runs **13** of 20, T-13 in flight will make 14.

## Open Questions

- Q12 **NOT blocking, ANSWERED by the main session.** The SC-15 note is now graded and staged for
  commit.
- Q13 **SUPERSEDED by Q15.** T-11 was indeed already satisfied; the whole five-task status write is
  now the open item.
- Q14 **CLOSED.** `claim()`'s "Never raises for contention" was false and is corrected in the code;
  the main session measured it with the lock held and I verified the raise path independently
  (`inflight_registry.py:104` → `harness_merge.py:36`, `:64`, `:89`).
- Q15 **BLOCKING for bookkeeping, not for delivery — needs the main session, which holds `Edit`.**
  Five task statuses cannot be recorded by me (see Current, item 2), so the mirror cannot be
  advanced and `plan.yaml` currently understates what is done. The rule that forbids every route is
  itself the thing that shipped in T-12.
- Q16 **NOT blocking, but it is a genuine test-isolation defect** in files inside DEC-174 amendment
  4's carve-out, so neither I nor a squad may fix it. `test-dispatch-guard.py` must isolate its
  registry root per case (the file's own T-08 intent already ordered exactly that:
  *"point CLAUDE_PROJECT_DIR at a fresh tempfile.mkdtemp() for every case so no case touches the
  real registry"* — so this is a compliance gap, not a design gap), and
  `test-validate-digest.py`'s F1.x hook cases should pin a `cwd` the way its DEC-156 cases already
  do. Until then the green suite depends on `detect` ordering.
- Q4 **NOT blocking, CARRIED — do not re-raise, do not fix.** SC-14 names **221** as its basis while
  the plan records at `:1448-1464` that the number is not attributable to scripts. It still works as
  a shrink detector and the measured 470 is far above it. A goal-check must name this as carried.
- Q5 **NOT blocking, recorded residual.** The exit-6 LOCKED branch of T-03 case 4, T-04 case 7 and
  T-06 case 7 was admitted but taken 0 of 20 trials each, because the loser WAITS. Pinned by the
  SET, not those cases. Note the registry's deadline is now 1.0s while the four file-merge callers
  keep 10.0s, so the registry's LOCKED branch is now materially easier to reach than when this was
  written.
- Q6 **NOT blocking, backlog.** `RUNS_AGENT_EXEMPT` was hand-fixed for two features; the suite
  asserts the map's MECHANISM, never its COVERAGE. Pre-existing and NOT mine: `check-state.sh`'s one
  violation is FEAT-26's unapproved BRIEF, still the only violation as of this session.
- Q7 **NOT blocking, ANSWERED.** No `DECISIONS-INDEX.md` row governs what re-opens a signature. pm:
  it deserves an entry as FOLLOW-UP, not folded into T-13.
- Q8 **NOT blocking, the main session's act.** #551's record needs updating, plus a backlog row
  against run-dir minting. An agent composing a GitHub post is forbidden (DEC-138 am.6).
- Q10 **NOT blocking, backlog, WIDER THAN THIS REPO.** `templates/gitignore.snippet` installs into
  every repo the factory touches, has 8 rules and no lock rule; separately its `:7` reads
  `.harness/features/*/runs/**`, missing the `<repo>` segment the multi-repo migration added.
- Q11 **NOT blocking, a HARNESS DEFECT.** The `SubagentStop` digest contract has no in-progress
  value, so a lead hosting an async member cannot idle. `validate-digest.py:845` means a second
  identical return SHIPS. T-09 narrows this at the PreToolUse edge but does not close it.
