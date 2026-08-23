# FEAT-31 — where it stands, and what needs your decision

**The tool works now, and it did not before today.** `context-watch.py` finds all 105 orchestrators
on this machine and its arithmetic matches the signed specification. At the start of this session it
found **zero** and reported `current 0` for an orchestrator holding 696,472 tokens. Both defects had
been sitting behind a fully green, mutation-proofed test suite.

**The feature cannot finish without you.** Ten of eighteen tasks are done. Six are yours under the
DEC-174 carve-out, and **three of the ten requirements have no other coverage at all** — REQ-04
(T-15), REQ-09 (T-14), REQ-10 (T-10, T-14). Two more of mine, T-05 and T-09, are blocked on your
T-04. The qa gate, the review panel and the goal-check all need the finished tree, so nothing further
can move until your tasks land.

**Your two blockers are cleared.** T-16 and T-18 are done and I verified both myself rather than
taking the lead's word: `.claude/settings.json` is zero-diff so D-24 holds, and `harness.json`
changed in exactly one key. **T-17 is unblocked, and T-07 has already made its edit to
`run-unit-tests.sh`, so that file is settled — append only when you get there.**

## What was wrong, and why every gate missed it

Two defects, both in T-01's code, both already named in `STATE.md` as standing — and I still recorded
T-01 `done` after re-running its verify block. **That was my error, and it is the same error the
feature exists to prevent: I trusted a green gate over the written record.**

1. **Discovery was one level too shallow.** The projects root holds *project* directories, each
   holding *session* directories. The walk joined `root/name/subagents` and matched nothing.
   One-level glob: 0. Two-level: 2012, of which 105 are orchestrators.
2. **`_build_row` contradicted D-11** on two of three figures — a zero appended for lines carrying no
   `message.usage`, `current` taken from the file's last line rather than the measured set's last
   member, and `entries` counting all parsed lines.

**Why 65 green cases saw neither: the tool, the tests and the fixtures were all built in the same
wrong shape, so they agreed with each other and disagreed with reality.** The fix now pins depth in
*both* directions — a correct two-level fixture must find rows, and a one-level fixture must find
zero — so a permissive implementation fails too. Every red proof asserts both that the mutation
applied and that real and mutant results differ.

**Verification that matters:** `verify-context-watch-live.py a7783f0ec41e6a8c6` now reports tool and
independent recomputation agreeing exactly at current 696,472 / peak 696,472 / entries 669. That peak
matches `BRIEF.md:43` to the token, and I reproduced it a third time independently. **SC-01's live
half is discharged.** Unit 76 of 76, integration 10 of 10, both exit 0, zero MISCONFIGURED.

## Decisions I need from you

1. **Run your six tasks.** T-04 first — it unblocks my T-05 and T-09. T-17 and T-12 are clear to go.
2. **The UAT is blocking and now runnable for the first time.** SC-10 requires you to run the tool
   with no argument and with an agent named, against **at least one live orchestrator**, and answer
   its four questions from the output alone. It was impossible before today.
3. **Q-HOOKCTX is yours and gates SC-13's design** — whether hook stderr reaches the model as
   context, or only as a tool-result error string. If it is the latter, SC-13 is not met by this
   design and T-17 needs rethinking, not just writing.
4. **One signed verify line is vacuous and pm should re-anchor it** (B-1). T-13's line 6 greps
   `not found` against a nonexistent projects dir, which matches an early-return branch, so the
   function Defect 2 lived in never runs. It is the assertion that should have caught it. A
   compensating control now exists, so this is not urgent — but it is a plan edit, which is pm's.

## Corrections to things on the record

- **The `bash-write-guard.sh` heredoc hazard is false.** I tested it: a read-only `python3` heredoc
  containing `>` and `>=` runs clean. The lead caught this by reading the source rather than
  complying with my brief. The real defect is narrower — `sed -i` with a shell-*variable* target is
  refused as out-of-domain. Two mechanisms, conflated.
- **`.harness/teams/build.yaml` does not exist**; only the shipped fallback does. My dispatch said
  otherwise because my own compound `ls` hid the error.
- **"No live orchestrator was running" was false.** One was — me. The live half was undischarged
  because discovery found nothing.

## Cost and budget

**cycles_used 4 of 10; runs 9 of 20.** Runs are informational by design (INV-22), so the count is
not a constraint — cycles are, and six remain. Two runs this session: one clean six-task build with
zero send-backs, one fix cycle that closed both defects with zero send-backs. **I also wasted one
spawn** on a stray no-op fork while trying to message the lead mid-run; I have no such channel, and
it returned having done nothing.

## Proposed backlog

Unstruck rows become issues on your acceptance. Anything not listed dies silently, so this is
everything that survived.

| ID | Finding | Nature |
|---|---|---|
| B-1 | T-13's signed verify line 6 is vacuous — greps `not found` against an early-return branch, so the function Defect 2 lived in never runs | bug |
| B-2 | One-argument invocation mixes footer scopes: rows narrow to one match, but blind-spot lines 1-2 re-walk the whole corpus. Touches SC-10 step 2 | bug |
| B-3 | `_safe_listdir` swallows `OSError`, so an unreadable *directory* silently drops its subtree; REQ-07 covers sidecars and transcripts, not directories | bug |
| B-4 | Any `verify:` floor expressed as an absolute case count is vacuous — T-16's `-ge 22` was satisfied at 29 before T-16 wrote a line. Make floors deltas against a measured pre-task count | chore |
| B-5 | The footer's second full corpus read is ~49% of wall clock (0.80s vs 0.41s). Sub-second today; the fix is to have `_build_row` return its measured sizes | enhancement |
| B-6 | `bash-write-guard.sh` refuses `sed -i` whose target is a shell variable, even when the expansion is in-domain | bug |
| B-7 | Eight lines of `DECISIONS.md` anchor rot in plan citations — content correct, pointers 8 lines stale; `lanes.resolved_at` also stale | chore |
| B-8 | `BRIEF.md:247` cites DEC-90 as a live constraint; DEC-90 is STRUCK | chore |
| B-9 | `BRIEF.md:231-237` says SC-07 changes `check-domain.sh`'s write route; the tree contradicts it | chore |
| B-10 | Corpus check for the ` ##`-truncates-a-YAML-scalar shape in other plans — it cost D-21 299 invisible characters | chore |
| B-11 | DEC-197 has no implementation; its own index row says so, and T-18's correctness partly rests on it | chore |
| B-12 | Two board cards (T-01 #642, T-02 #643) read Building while the issues are closed and the plan says done; `close-task` re-run twice did not move them | chore |
| B-13 | T-08's retention blind-spot line prints `0 day(s) old` when no transcript was read — a measurement never taken. The tension is in T-08's intent, not the code | bug |
| B-14 | D-11 spec gap: an agent whose last measured entry has zero token fields reports `current 0` beside `peak 97,076`. Faithful to D-11, misleading to a reader | chore |
| B-15 | A lead was force-closed with its member in flight, twice on this feature; the member outlived it and wrote an unassessed artifact | bug |

**One item is for the panel, not the backlog:** the fix applied code *before* writing its new
assertions — a RED-first deviation the lead volunteered rather than hid. It judged the deliverable
sound because all four mutants deliver a count differential against the exact pre-fix shape, and a
second member rebuilt them independently. I am carrying it forward rather than waiving it, because
TDD ordering is qa's and the panel's call.

## Method — read this before trusting the above

**No report round was spawned.** I assembled this from the nine run digests on disk, and I read every
one, including the plan-phase runs I did not conduct:
`runs/plan-product/digest.md` (ESCALATE), `runs/plan2a-product/digest.md` (PASS),
`runs/plan2b-product/digest.md` (BLOCKED), `runs/plan3-product/digest.md` (**incomplete — a stub
marked IN PROGRESS, carrying pre-dispatch acceptance criteria and no verdict**),
`runs/plan4-product/digest.md` (PASS), `runs/plan5-product/digest.md` (ESCALATE),
`runs/build-eng/digest.md` (ESCALATE), `runs/build2-eng/digest.md` (ESCALATE),
`runs/fix1-eng/digest.md` (PASS).

For the plan-phase digests I read verdicts and headlines rather than the full text; for the two eng
runs I conducted I read them in full and re-ran the verification myself. **Every figure in this
briefing I measured directly in this worktree at `b2f7c73`,** rather than restating a member's claim
— including the ones that contradicted my own earlier report.

`runs/build2-eng/digest.md` was missing three required contract fields when it reached disk, though
the lead's return carried them. I completed them from that return and recorded the escalation's
resolution; `validate-digest.py` now passes it.

**The goal-check has not run and no SC is recorded as met.** Fourteen SCs exist (SC-01..SC-11,
SC-13..SC-15 — there is no SC-12) and pm grades them once the tree is complete. What I can say is
narrower and evidenced: SC-01's live half is discharged, and the arithmetic and discovery claims the
feature rests on are now true where this morning they were not.
