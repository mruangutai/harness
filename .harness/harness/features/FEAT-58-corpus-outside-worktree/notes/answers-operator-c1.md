# Answers — FEAT-58-corpus-outside-worktree — operator review, cycle 1

One batched review pass (DEC-176). Every open question from the plan presentation is answered
below; nothing is held back for a second pass.

## Q1 — PF-5945852660e0bd21e2b5aabb8cd48383 (high) — RESOLVED, not overruled

**Ruling: candidate (a). T-10 and T-08 refuse to sparsify any checkout whose HEAD does not
already contain the fail-closed reader commits.**

The check is `git merge-base --is-ancestor <fix-sha> HEAD` against the worktree's own HEAD. A
worktree that fails it is **left fully materialised** and named in the migration record as
skipped-pending-merge, with the reason. It is converged later, by re-running the same task, once
its branch carries the fix. T-08 applies the identical guard at creation: a new worktree cut from
a branch that does not carry the fix is created full, not sparse.

The finding's mechanism is accepted as stated and was independently confirmed: hooks are
registered through `CLAUDE_PROJECT_DIR`, so each worktree executes its own branch's
`check-state.sh`, and a sibling sparsified ahead of its branch would run a pre-fix gate over a
sparse tree — the measured 1-of-88 / EXIT=0 shape, live and host-wide. A `depends_on` edge does
not close it; only a HEAD-content precondition does.

The high finding is therefore **resolved by amendment**. No `--overrule` is recorded and none is
authorised.

Deliberately rejected: deferring migration out of the plan (the ~950 MB reclaim would then be
gated by nothing and would not happen), and naming-and-accepting the window (it ships the exact
blindness this feature exists to remove).

## Q2 — PF-46767d8b63e7aa1a1585cd4639ff2f4c — CUT T-12

**Ruling: delete T-12, drop D-05's gate-enforced declaration, amend SC-14 to grade the recorded
frame lines instead.** pm applies this; the held-off state ends.

The checkpoint's whole yield is catching a whole-corpus read that declares nowhere. REQ-05 already
has the read site print its provider and ref every time it reads, so that case can only arise by
bypassing `corpus_read` altogether — which the dispatch guard also does not catch, because it
inspects dispatch text and not the read. It buys a declaration already obtained, and pays for it
with permanent per-dispatch friction and a new exit-2 refusal path inside a gate this feature is
already modifying. The grilling artifact required only that a whole-corpus read **be stated**;
recorded output states it.

Record the cut as a decision with this reasoning, so a later reader does not re-propose it.

## Q3 — PF-5230f48fc9beeeb9461f3120ac174b21 — KEEP IT, AS ITS OWN TASK, AND TRACE IT

**Ruling: the `linked_worktrees(root)` → `linked_worktrees(corpus_root(root))` correction stays
in FEAT-58, but becomes its own task with its own test, not a rider on T-06, and it gets a REQ.**

It is not incidental to this feature — it is load-bearing for it. The claim that the corpus is
read-only inside a worktree "already, by construction" rests on claim-set binding (DEC-208 /
DEC-218) refusing writes outside the registered worktree, and that path runs through
`check-domain.sh`'s worktree tier. If that tier has been reaching nothing whenever the hook fires
from inside a worktree — `.git` is a file there, the directory read fails, the `OSError` is
swallowed — then the read-only guarantee this feature depends on is **not** currently enforced,
and shipping the corpus root as a read-only surface without fixing it would rest a safety claim
on a tier that reaches nothing.

So: separate task, its own failing-first test proving the tier reaches the siblings it should,
traced to a REQ that states the corpus root is read-only and enforced. Its new reach — every
governed write now sweeping sibling worktrees — is then reviewable on its own terms rather than
arriving as an untraced rider. Note the reach is also a cost surface: the run measured the
converted enumeration at −0.1751 ms/checkout versus the glob it replaces, so state that number
next to the change.

## Q4 — the four batched findings

- **PF-02940a5ba93ee330e767227c76901b86 (med) — drop the byte-for-byte parity clause.** Keep the
  two frame lines. The two requirements are contradictory and the frame lines are the
  requirement; parity with pre-change output was never asked for and cannot hold once output is
  added. Amend T-04.
- **PF-f9bb1e67ce6999bd98169f835f6294ed (med) — keep exactly one pin.** The instrumented
  call-count assertion in T-06 is the pin; delete the prose pins in T-03/T-04. **Apply this and
  the finding above in ONE edit**, as the panel requires, so the test file never carries two
  contradictory assertions about the same output.
- **PF-fbf676b72589815cd6aba6c677c35370 (low) — fix it, do not accept it.** T-05 must resolve
  only the candidate feature, not route all 88 through `corpus_read`. ~1.2s added to every
  merge-gate `PreToolUse` invocation is not a low-severity cost on a hook that fires on every
  governed write, and the work is unnecessary: the gate needs the one feature it is deciding
  about.
- **PF-bf86bbbece6a808224e6cdcc21465a15 (low) — drop the duplication.** Seven refusal cases
  duplicated as deletion insurance is a test-suite smell; one assertion per case. Deletion
  insurance is not a reason to assert the same thing twice.

## Q5 — DEC-174 — CONFIRMED, and the grilling artifact was wrong

The plan's reading is correct and mine was not. DEC-174 requires a change to hooks, validators
and gate scripts to be made **directly**, never dispatched through a team run whose gates are the
artifact being changed. My grilling artifact and the design comment on issue #1559 both glossed it
backwards as "may plan but must not execute". **11 of 16 tasks in the `main-session-direct` lane
is intended**, and `check-plan-routes.py` exiting 0 with informational DEVIATION lines is the
carve-out working as designed.

The grilling artifact has been corrected at source so pm is not carrying my error forward. Good
catch — that gloss would have mis-assigned execution for the whole feature.

## Q6 — no byte figure in any criterion — ACCEPTED

Confirmed. A `df` real-block bound is satisfiable by APFS clonefile, the mechanism the ruling
excludes, so a byte criterion would grade the wrong thing. Footprint is graded by **feature-
directory count and file count** — `ls .harness/*/features | wc -l` returning 1, and the on-disk
file count — with the measured MB living in the problem statement as context, not as a gate. This
is the verification trap the grilling artifact warned about, handled correctly.

## Q7 — the four harness defects

All four are accepted as real and none is to be worked around inside FEAT-58. Filed as their own
tickets; do not fold fixes for them into this plan:

- INV-37 firing VIOLATION for the whole of every plan phase, with a remedy the playbook forbids
  before signed approval.
- `plan-merge.py` having no verb that reaches a top-level key, and its `amend` re-emitting a list
  at the key's own indent.
- Two subagent dispatches returning exit 1 with "yield called with null data" while carrying a
  complete, well-formed digest.
- The missing `lanes` row for `.claude/commands/**`.

**Lane ruling for the fourth, so T-14 is not blocked:** `.claude/commands/**` is
**`main-session-direct`**, reason "command and skill prose resolves to NOBODY; no agent domain
grants it" — the same basis as the existing `.claude/skills/** outside harness/bin/` row. I
decide the lane; **pm writes the row**, since `plan-merge.py` cannot reach a top-level key and
`plan.yaml` is pm's to author.

## What happens next

Apply all of the above, re-run the panel on the amended plan, and present again. The signature is
mine and has not been given.
