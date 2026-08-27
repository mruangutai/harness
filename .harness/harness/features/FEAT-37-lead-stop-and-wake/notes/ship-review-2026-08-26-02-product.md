# FEAT-37 — re-plan complete, ready for your signature

**The plan is re-anchored at `8fc87f8` and both approval blocks read `pending`. All four blockers
are closed. It cost one product run and zero send-backs: runs 7 → 8 of 20, cycles 0 of 10, twelve
runs left for the entire build.**

**Correct one thing before you sign.** `plan.yaml:110`, `BRIEF.md:139` and `BRIEF.md:219` label
REQ-08/T-03/SC-09 *"the operator's scope call/addition"*. **That attribution is false.** You
delegated the B1b decision to me — *"Decide whether it enters this feature or opens a ticket, and
say which"* — and I decided it. My dispatch told pm to state it as mine; pm rendered it as yours.
It matters because you will read that label and may believe you already approved the one item in
this plan that most needs your fresh judgement. I did not spend a run and a cycle correcting three
words. It is row B-1 below.

## How the briefing was assembled (DEC-69 disclosure)

**No report round was spawned.** I read one digest from disk:
`.harness/harness/features/FEAT-37-lead-stop-and-wake/runs/2026-08-26-02-product/digest.md`.

**I did not read the six earlier plan-phase digests**, and you should know that. This briefing is
scoped to the re-plan you asked for, and the history that produced the withdrawn plan is history you
wrote. If you want a full-phase account, say so and I will read them.

**I did not take the lead's PASS on trust.** B1, B1b and B2 I measured myself at HEAD *before*
dispatching, and I re-opened every claimed fix at disk afterwards. Where a number appears below, I
ran the command.

## What the plan now does about each blocker

**B1 — T-03 had no subject and its verify passed on the empty set. Closed, both halves.**
`.claude/skills/harness/SKILL.md` is **removed from T-01's `bound` group** (`plan.yaml:227-231`).
`c5e59aa` deleted the only text that group graded there — the single-flight grep exits 1 — so a
third case would grade the empty set and exit 0 having proven nothing. The plan says so in those
words and names it as the issue-804 shape D-05 refuses. **The second half is the real fix:** every
surviving site now carries `case_floor_<site>` (`plan.yaml:234`), which asserts at least one
occurrence *before* grading and makes zero occurrences a **named FAIL**. No occurrence-grading check
in this plan can pass on an empty subject again — including checks nobody has written yet.

**B1b — the orchestrator lost its inoculation. Folded in, as REQ-08 / T-03 / SC-09.**
T-03 is repurposed from bound-correction to restoring the orchestrator's never-wait rule *and* its
expected-refusal clause. `plan.yaml:17` and `:522` record that T-03 depends on nothing and nothing
depends on it, so striking `REQ-08`, `T-03` and `SC-09` together leaves issue #831 whole. **It is
three lines to strike, not the one I promised you** — they cross-reference, so the set is traceable,
but I said one line and it is three. SC-09 is graded by a new `orchestrator` group of six presence
cases, all of which fail at `8fc87f8` today.

**The regression is live, and it was corroborated twice during this run itself.** The
`children_refusal_lines` refusal fired on my own return with a lead in flight, and again on the
product lead's return with pm in flight. It keys on *having children*, not on `SINGLE_FLIGHT_AGENTS`
(`inflight_registry.py:32` is `("harness-pm",)`), so it is the routine path for every parent in the
org. Only the surviving line 60, *"There is no waiting anywhere in this loop"*, stopped me reading
it as "you may not return yet". **Neither instance can serve as SC-08 evidence** — by DEC-201 both
playbooks were loaded from the main checkout.

**B2 — entries sliced at the wrong heading level. Closed, re-derived at level two.**
`case_entry_scope` now slices *"from its LEVEL-TWO heading to the next LEVEL-TWO heading beginning
with DEC-"* (`plan.yaml:302-303`), and `case_entry_heading` reads the level-two line
(`plan.yaml:298`). Measured independently by me and by pm: **201 lines match `^## DEC-`, 28 match
`^### DEC-`.** T-05 can now reach exit 0, so T-06 no longer stalls behind it.

**B3 — SC-04 had nothing delivering it. Closed at both ends.**
The contradicting clause is now written into **T-02 part THREE** (`plan.yaml:405-408`), the playbook
edit the decision governs, not only into T-05's decision record. And T-01
`case7_overrides_tool_text` (`plan.yaml:200`) makes it gradable: **one single sentence** must match
both the tool's nudge and a denial. A region that quotes *"continue other work in the meantime"* in
one place and denies something unrelated somewhere else **fails** — which is precisely the
silent-beside-it state SC-04 exists to catch.

## SC-08 — deferred on a measurement, and it overturned my own instruction

I directed that the zero-cost option be tested **first**: grade SC-08 from this feature's own build,
since that build is a real lead dispatching real members. **It genuinely fails, and I verified the
reason at source rather than accepting it.** `DECISIONS.md:7023` records that a spawned agent loads
its skills from the **main checkout** while the rewrite sits in a worktree. Every lead spawned during
this build would therefore read the *unedited* playbook, and any evidence collected would grade the
old text — evidence for the wrong file, which is worse than no evidence.

SC-08 is deferred to a **post-merge run by you** (D-13). Issue #866's registry keying is a second,
weaker reason and explicitly not the deciding one. This is a forced deferral, not an evasion.

## Every scope call I took rather than escalated

1. **B1b enters the feature** as a new labelled REQ + task + SC, rather than opening a ticket.
   Deferring it would ship a lead-tier never-wait rule while the tier directly above stays
   uninoculated — the exact failure T-02's own intent names. You sign the BRIEF, so your signature is
   the approval, and the item is built to be struck in one act.
2. **`inflight_registry.py:258`'s `#551` citation is NOT corrected here.** It sits in
   `refusal_lines` — a different function, a different code path from the `children_refusal_lines`
   T-04 corrects, with its own tests — and it rests on #866's measurement rather than this feature's.
   T-04 stays narrow. Row B-2.
3. **I did not spend a cycle on the false attribution** described at the top. Named here instead.
4. **I scoped this briefing to the re-plan** and did not read the six earlier plan-phase digests.

## What needs your decision

| # | Question |
|---|---|
| Q1 | Sign, or strike `REQ-08` / `T-03` / `SC-09` together. It is three lines, not one |
| Q2 | Confirm the narrower DEC-174 reading: amendment 4's proof burden attaches to the **cutover**, not to a squad writing a gate's library. The BRIEF's earlier "conditional grant" framing was wrong and is corrected |
| Q3 | Confirm SC-08's post-merge deferral (D-13) |
| Q4 | Correct the REQ-08 attribution before signing, or accept it knowing it is wrong |

## Proposed backlog

| ID | Finding | Nature |
|---|---|---|
| B-1 | `plan.yaml:110`, `BRIEF.md:139`, `BRIEF.md:219` attribute the REQ-08 scope call to the operator; it was the orchestrator's | chore |
| B-2 | `inflight_registry.py:258` cites issue #551 where #866 measures #628 as the two-writers bug | bug |
| B-3 | Issue #866 — the dispatch end of the deadlock is untouched by this feature; `refusal_lines` still prints `release-all`, which wipes every feature's live claims | bug |
| B-4 | Issue #811 — the three-task block was struck whole before approval (D-07); #811 stays open and returns to backlog | enhancement |
| B-5 | SC-08 needs a post-merge operator run to be graded at all (D-13) | chore |
| B-6 | Engineer DIGESTs carry no `files_touched`, so a member that wrote a receipt reports no files and the lead reconstructs it by hand | bug |
| B-7 | `notes/root-cause-*.md` is in no member's domain, so debug reports fall back to receipt paths | chore |
| B-8 | Single-flight is keyed per checkout, so several orchestrators' children can share one registry when run from one cwd | enhancement |

**Anything not listed here dies silently.** Strike rows by ID.

## Budget

Runs **8 of 20**, cycles **0 of 10**. The re-plan hit its one-run target with no rework, so nothing
in DEC-157's three categories fired. Twelve runs remain, which is comfortable for a six-task build
plus qa, simplify, the panel and the goal-check. No budget concern.
