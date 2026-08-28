# FEAT-37 — operator answers, plan phase, 2026-08-24

## Q1 — STRIKE THE #811 BLOCK. USER RULING.

Remove T-07, T-08, T-09, REQ-08 and SC-09. FEAT-37 fixes the loop and nothing else.

**The reason, and it is yours, not mine.** I folded #811 in on a causal hypothesis I had written up
in #831 as though it were a measurement. Your specimen falsified it: `a8f1c68d9a0d69f25` carries the
loop signature with **ZERO** occurrences of `returned with children in flight`. That lead never
attempted to stop, so the #551 refusal was not in that loop. With the inoculation in place, #831 is
independently verifiable without touching the refusal at all.

**#811 stays OPEN and goes back to the backlog.** Its own "what a fix has to preserve" section argues
from the once-only bound your measurement overturned, so that ticket needs rewriting before anyone
works it. I will do that myself; do not spend a task on it.

**Strike it as a strike, not a re-plan.** You isolated the block deliberately and that was the right
call — say so in the record so the next reader knows the shape was chosen, not accidental.

## Q2 — AMEND, DO NOT STRIKE. USER RULING.

DEC-199 keeps its entry and its ruling. Only the falsified sentence changes.

**DEC-188 does not apply and pm's distinction is the right one.** DEC-188 governs a decision the tree
*flatly contradicts*. DEC-199's ruling — that a verdict about a member still running is a verdict
about something the reporter cannot see — is still correct and still in force. What is false is one
subordinate clause about how often the refusal fires.

**All three copies get corrected, and the amendment records the measurement that overturned the
bound** — different child sets across `agent-a89be3fd837d1b779` lines 178 and 392, proving a distinct
event rather than replayed context. Verified by me at source, all three:

- `.harness/harness/docs/DECISIONS.md:6701` — "fires at most once"
- `.claude/skills/harness/bin/inflight_registry.py:274` — "this refusal fires ONCE; a second
  identical return will ship"
- `.claude/skills/harness/SKILL.md:52-53` — repeats the same claim

**The third one is mine.** FEAT-35 wrote it and I signed it. Correct it in the same voice as the
others; no apology, no amendment note, and no reference to who wrote it.

## Q3 — FIX IT. Fold into the same reopen; no extra run.

Your finding stands and I confirmed it. T-04 is `execution_mode: team`, edits
`inflight_registry.py`, and its verify runs `test-lead-stop-and-wake.py --group bound` and
`test-inflight-registry.py` — **not** `test-validate-digest.py`. `validate-digest.py` imports that
module, so DEC-174 amendment 4's condition, *"proven by showing the gate's violation set is identical
before and after"*, is asserted and never discharged. `check-plan-routes.py` prints `OK T-04` because
it reads domain grants and nothing else.

Add `test-validate-digest.py` to T-04's verify, and make the task's intent say WHY it is there — a
future reader trimming a slow verify would otherwise delete the one line that legalises the lane.

## Q4 — bring the three criteria to me at the signature.

SC-02, SC-03 and SC-07 are stated by neither ticket. **That is pm doing its job**, not scope creep:
the operator states what done must include, and pm finds what done ALSO requires. Present each with
one sentence on what breaks without it and I sign them with the BRIEF.

## Q5 — SC-08 is mine and stays `not_met`.

Do not let the goal-check grade it. Say plainly that it is outstanding. `test_kinds.eval` being null
makes the `ai_behavior` matrix requirement a soft skip that proves nothing — you disclosed that
rather than leaning on it, which is correct; keep it disclosed in the brief.

## Q6 — handoff accepted, but not yet.

Apply Q1, Q2 and Q3 first — they are narrow and you already hold the context for them. Hand off to a
fresh orchestrator for BUILD, after I sign.

## Q7 — yes, as a backlog row, not here.

A supersede mode for `plan-merge.py` is worth having. File it; do not build it in this feature.

## Q8 — file all three as backlog rows.

Both `notes/root-cause-*.md` being in no member's domain and engineer DIGESTs carrying no
`files_touched` are real gaps. The single-flight keying is a known consequence of this session
standing in another feature's worktree; record it and move on.

## Standing instruction

Every decision, question and option holds the QUALITY, PERFORMANCE and EFFICIENCY of the system as
the highest priority. A false green and a false defect are the same class of harm.
