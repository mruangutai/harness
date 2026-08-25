# Q6 and Q8 folded into the plan — 2026-08-25

**Both rulings are in.** Q6 lands as a new step in T-04 (`ship` schedules the audit). Q8 lands as a
NEW task, T-11, not as a fold. Two new decisions (D-12, D-13), one new requirement (REQ-12) and two
new criteria (SC-16, SC-17). `approval.status` stays `pending`, untouched — the task set changed.

## Q8: new task, not a fold — and why

T-11 owns the `close-task` deletion. Folding it into **T-06** was the live alternative and I rejected
it on two grounds, both checkable in the file:

1. **T-06 traces REQ-07**, which is about `closes` and closing keywords. The `close-task` deletion
   serves a different outcome — no harness-blessed route closes an issue without the station — so
   folding would have made one task trace a requirement that does not cover half its work, and the
   goal-check would read a deletion nobody committed to.
2. **The dependencies differ.** T-06 depends on `[T-02, T-05]`. The `close-task` deletion must land
   after T-04 (which rewrites `cmd_ship` in the same file and whose step 8c referred to
   `cmd_close_task`) and after T-06 (the other `gh-sync.py` deletion), so T-11 is
   `depends_on: [T-04, T-06]`. Two different orderings in one task is two tasks.

Folding into **T-04** was worse still: T-04 is already the largest task in the plan and its subject is
the ship rewrite.

## Q8: REQ/SC coverage CHANGED — deliberately

- **REQ-12 added**: inside the mirror, `abandon` is the only command that closes an issue directly,
  and `close-task` no longer exists. It passes the swap test — it survives changing how the deletion
  is implemented.
- **SC-16 added** (`automated`, `integration`): `close-task` exits non-zero, the string survives
  nowhere in `gh-sync.py`, `abandon` is the only closer in that file, **and the coverage
  `close-task`'s tests carried does not fall.** That last clause is the one that matters: five of the
  six `close-task` test blocks assert `_apply_parent_rule`, the loud pair, or the no-board
  precondition — properties of the function and the environment, not of the command. `start-task` is
  the surviving caller, so T-11 retargets them rather than deleting them.
- **SC-17 added** for Q6 (`automated`, `integration`): without it the compensating control would ship
  with no criterion, which is the same hole seen from the other side.
- **REQ-06 extended** with the compensating-control clause: the audit is now committed behaviour, not
  a disclaimed gap. T-04 gains `REQ-06` in `traces:`.

## Q6: how the audit is scheduled, and the one thing it must not do

T-04 step 7c. `board_lifecycle.py` gains a public `audit_findings(repo_arg=None)` that returns the
finding list, prints nothing and never exits; `cmd_audit` is rewritten to call it. `cmd_ship` imports
`board_lifecycle` and calls it after every station write, printing `gh-sync: audit — <message>`.

**The read-back bound is not widened.** The four calls are `board_lifecycle`'s own, made under its
inverse-of-the-mirror posture; `ship` performs none of them itself, so DEC-203 item 5's six purposes
stand. Getting this wrong would have forced T-03 to write a seventh purpose into a signed decision.

`ship` never gates on the audit: exit 0 regardless, and no audit line may carry `gh-sync: SKIP` or
`gh-sync: FAILED` (`post-merge-sweep.sh` greps both).

## Reconciled, so nothing reads as contradictory

- **T-08's note** (the `check-state.sh` invariant deliberately does NOT detect a closed-not-Done card)
  now says the runner exists and is somewhere else — inside `ship`, not the state checker. The two
  notes agree.
- **T-04 step 8c** no longer corrects `cmd_close_task`'s comment; the comment goes with the function.
- **T-09 part A.12**'s "either answer to Q8" branch is resolved to deletion, and T-09 now depends on
  T-11. New part A.13: leave `github-mirror.md:87`'s past-tense `close-task` measurement alone —
  deleting a measurement because its subject was removed would falsify the record.
- **SC-12's regression guard** in T-04 no longer runs `close-task` against the stub.
- **T-03 item 8** records the guardrail plus the one narrow exception (`abandon`), the deletion, and
  the audit's accepted cost.
- **`BRIEF.md:8`** keeps its `close-task --reason completed` sentence: it is a measurement pinned at
  `cc84b29` in the Problem section and stays true after the command is gone.

## Open, non-blocking

`wayfind.py:318` runs `gh issue close` on a wayfinding ticket. The Bash gate is blind to that
subprocess exactly as it was to `close-task`, so it is the same leak class outside the mirror.
Wayfinding tickets are not feature tickets; recorded in the brief's NOT-in-scope list and raised as
Q12 rather than absorbed.
