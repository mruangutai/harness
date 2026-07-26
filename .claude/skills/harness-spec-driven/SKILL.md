---
name: harness-spec-driven
description: Planning discipline for the product manager — every task fully specified with paths, intent, verification and traceability; no placeholders; requirements separated from decisions. Loaded by harness-pm.
---

# Spec-Driven Planning

You author `BRIEF.md` and `PLAN.md`. They are the spec — there is no separate spec artifact.

## Every task needs four things

A task missing any of them is **not written**. Identify the gap and return it rather than guessing:

1. **Exact file paths.** Not "update the config" — `edit .harness/harness.json`.
2. **Complete intent.** Not "implement X" — the actual logic, types, structure, values.
3. **A `verify:` command** with the expected result. Runs in under 60 seconds, gives an unambiguous
   pass/fail, needs no human interpretation. If nothing automated is possible, say so explicitly:
   `verify: MANUAL — <what must be built first to make this automatable>`.
4. **`traces:`** — the `REQ-NN` or `D-NN` this task serves. A task that cannot cite its source is either
   out of scope or the brief is incomplete.

Plus **`change_type:`** on every task. The qa gate reads it to determine required tests, and a task
without one **blocks that gate** — `check-state.sh` fails the state check on it.

## Reject placeholders

`TBD`, `TODO`, vague verbs without targets, "similar to above", "follow the existing pattern",
"implement X" without saying what X produces. If you cannot fully specify a task, that is a signal the
*brief* is incomplete — raise it in `open_questions` rather than writing a task nobody can execute.

## Requirements versus decisions — the boundary that matters

| It is | Where | Test |
|---|---|---|
| **REQ-NN** — what the product must do | `BRIEF.md` | survives changing your mind about implementation |
| **D-NN** — how, architecturally | `PLAN.md ## Decisions` | changes if you swap the approach |

*"Users can sign in with their Google account"* is a requirement. *"Use Supabase social login"* is a
decision. Swap Supabase for Auth0: the requirement is untouched, the decision is not.

**Why this is load-bearing and not bookkeeping:** you goal-check REQ coverage against the approved brief.
If implementation choices are logged as requirements, your own goal-check will "verify" that you
delivered your technical decisions rather than the outcomes that were committed to — passing green while
missing the point entirely.

## Success criteria declare how they are verified

Every `SC-NN` carries `verify: automated | inspection | uat`. An SC with no method is not verifiable, and
discovering that at ship time is too late. `automated` also names its `evidence:` test kind.

An SC must be falsifiable. "The code is clean" and "performance is good" are not criteria — if you cannot
state the observation that would prove it false, it is not one.

## Approval is not yours

You draft `BRIEF.md` and `PLAN.md`; you never mark them approved. Only the orchestrator writes
`## Approval`, because only it can reach the user.

**Re-planning resets approval.** If you change the task set after approval, set `## Approval` back to
pending. A stale signature must never carry onto a changed plan.

## Red flags

| Thought | Reality |
|---|---|
| "I'll specify this task loosely, the dev will figure it out" | Then you moved planning into execution, unreviewed |
| "The user described it to me, so it's approved" | Describing is not approving. You cannot approve either |
| "Postgres is a requirement, they said so" | It is a decision. Apply the swap test |
| "I'll skip change_type on the trivial ones" | The qa gate blocks. `check-state.sh` will catch it |
| "This SC is obviously testable" | Then name the test kind. If you cannot, it is not `automated` |
| "I'll tidy the plan after approval" | Any change resets approval. Get it right first |
