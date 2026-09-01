# Review — FEAT-41 refusal-text closures, at e5afc19

BLUF: both closures hold. F-1 and F-2 are CLOSED, quoted below against plan.yaml at e5afc19.
No new HIGH finding. One INFO-level observation on an adjacent (out-of-primary-scope) refusal.
VERDICT: PASS.

## F-1 — T-09's Edit/Write denial of plan.yaml — CLOSED

T-09's intent (plan.yaml:834-842) now requires the denial to state the reason first, then the
route:

> "On the Write and Edit routes: deny with exit 2 and a message that STATES THE REASON FIRST -
> that plan.yaml now has exactly one writer, plan-write.py, because every station value must
> be validated before it lands - and then names the four verbs and the tool path." (834-836)

It is explicitly barred from `deny()` because that helper appends the STATE.md-flavored ROUTING
constant:

> "DO NOT EMIT THIS REFUSAL THROUGH deny(). check-domain.sh defines deny() at 1063-1066 and
> its last line appends the module-level ROUTING constant defined at 879, which speaks about
> STATE.md, digests and notes/ - a different file class entirely." (843-846)

And the test list (873-878) asserts the reason clause is present and ROUTING text is absent:
"the SAME message CONTAINS the reason clause ... and DOES NOT CONTAIN the ROUTING text,
asserted by searching the denial for a distinctive substring of the ROUTING constant."

SC-05 (plan.yaml:112-117) was rewritten to match — it now requires BOTH the verb and the reason,
and states plainly that a verb-only denial fails the criterion:

> "SC-05: A `Write` or `Edit` of a `plan.yaml` is denied with exit 2 and a message that BOTH
> names the verb to use instead AND states the reason the previously-legal route is now closed
> ... A denial carrying only the verb does not meet this criterion." (112-116)

Both halves of the original finding (the WHY-less message, and SC-05 permitting it) are closed
in the plan text.

## F-2 — T-08's sign-approval refusal — CLOSED

T-08's intent (plan.yaml:768-773) now mandates the literal verb in the refusal text:

> "prints ONE refusal text, used verbatim for every denial, which NAMES sign-approval LITERALLY
> as the verb it refused rather than saying the verb: that sign-approval writes the approval
> signature ... A log line read without the command that triggered it must still say what was
> refused." (768-773)

T-08's test list (793-798) asserts this literally: "a payload with agent_type harness-orchestrator
invoking sign-approval exits 2 AND its refusal text contains the literal string sign-approval,
the exit code alone not being the assertion."

SC-07 (plan.yaml:121-124) matches: "the refusal names BOTH the refused verb - the literal string
`sign-approval` - and the sanctioned route."

## Secondary scan — plan-write.py's CLI surface (T-03, T-13)

- `apply`/`add-tasks`: unchanged exit 7/8 behavior, no new text.
- `set-task-station`: exit 3 names the ids the plan does carry (plan.yaml:267-268) — actionable.
- station validation shared by set-task-station/set-feature-station: exit 4 "one line naming the
  offending value and listing the legal ones" (284) — actionable, no WHY needed since the cause
  (typo/illegal value) is self-evident, unlike the T-09/T-08 cases where an agent could mistake a
  closed route for a stuck gate.
- `sign-approval`: writes the three approval fields; its identity refusal is T-08's, already
  covered above.
- Exit-code table extended per docstring (287-288: "3 unknown task id, 4 illegal station, and the
  existing 5, 6, 7, 8, 9 unchanged") — every code has a stated meaning.

No new HIGH/MED defect found on plan-write.py's own verbs/exit codes/messages.

## Adjacent observation (INFO, outside primary SCOPE — gh-sync.py `ship`, not plan-write.py)

T-10's "Defect two" refusal (plan.yaml:925-930) mandates only that the message name the
equivalent main-checkout path — it does not require stating *why* (that the directory is inside
a worktree about to be deleted):

> "exit 1 with one line naming the equivalent path in the main checkout ... This is a refusal,
> not a skip: skip() exits 0 and post-merge-sweep.sh would then delete the worktree." (927-930)

Lower risk than F-1's case: `ship` is main-session-direct, not an LLM agent choosing between a
denied route and a shell-write escape hatch, so the fail-open-via-misread-as-malfunction failure
mode F-1 named does not really apply here. Flagged as INFO only, not gating, and outside this
task's stated SCOPE (plan-write.py's surface).

## Housekeeping

- Reviewed via `git show e5afc19:...` only, per instructions; working-tree copies of plan.yaml/
  BRIEF.md were never opened.
- `[harness:human]` search across FEAT-41's history (`ee66ae2..e5afc19`) returns none; no hand
  edits are in scope for this re-review.
- T-12's recording form, DECISIONS.md, plan architecture/decomposition, operator rulings 1-7, and
  the FEAT-40 INV-26 residual are out of scope per dispatch and were not evaluated.
