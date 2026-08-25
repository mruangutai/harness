---
name: harness-spec-driven
description: Planning discipline for the product manager — every task fully specified with paths, intent, verification and traceability; no placeholders; requirements separated from decisions. Loaded by harness-pm.
user-invocable: false
---

# Spec-Driven Planning

You author `BRIEF.md` and `plan.yaml`. They are the spec — there is no separate spec artifact.

**`plan.yaml` is REAL YAML, and nothing in it is prose for a human** (DEC-182). The human reads
`BRIEF.md`. Instantiate from `.agents/skills/harness/templates/plan.yaml`.

**Write it through the merge tool, never whole:**

```bash
python3 .agents/skills/harness/bin/plan-merge.py apply \
  --file .harness/<repo>/features/<FEAT>/plan.yaml --proposal -
```

It unions by task and decision `id`, so a second pm spawn cannot delete the first's tasks.
The `approval:` block is carried forward byte identical and any approval block in your
proposal is ignored. Exit 7 means one `id` carries two different values — yours to resolve.

**No markdown in any value — no backticks, no `**bold**`, no links.** They are decoration in a data
file. Measured on the format this replaced: `safe_load` over every task block in the four live plans
failed 43 of 44 times, 26 of them because `files:` began with a backtick. A value carrying
decoration is either rejected by the loader or handed to a resolver as a path nobody wrote.

Shipped `PLAN.md` files are never rewritten; their reader stays. You author `plan.yaml`.

## Every task needs four things

A task missing any of them is **not written**. Identify the gap and return it rather than guessing:

1. **Exact file paths**, as a YAML list of plain strings — one path per entry. Not a comma string,
   not backticked, and **no trailing annotation** like `(delete)`: the resolver takes the value
   verbatim, so an annotation becomes part of the path and resolves to nothing. Intent about a path
   goes in `intent:`, not beside it.
2. **Complete intent.** Not "implement X" — the actual logic, types, structure, values. `intent:` is
   the LITERAL DISPATCH PROMPT: the agent doing the work receives it and nothing else about the
   task. Detail that only JUSTIFIES the instruction — probe transcripts, why an earlier draft was
   wrong — belongs in `notes/`, not here.
3. **A `verify:` command** with the expected result. Runs in under 60 seconds, gives an unambiguous
   pass/fail, needs no human interpretation. If nothing automated is possible, say so explicitly:
   `verify: MANUAL — <what must be built first to make this automatable>`.
   **Write it as a literal block `|`, never a folded `>`** — see below; this one is not a style
   preference.
4. **`traces:`** — the `REQ-NN` this task serves, as a list. A task that cannot cite its source is
   either out of scope or the brief is incomplete. `D-NN` goes in the `decisions:` block, not here:
   carrying both made the field mean two things and nothing ever read the second.

Plus **`change_type:`** on every task. The qa gate reads it to determine required tests, and a task
without one **blocks that gate** — `check-state.sh` fails the state check on it.

## Routing is resolved at plan time

Every task carries `execution_mode:`, a bare enum with exactly two legal values, and its
explanation in a sibling key:

```yaml
execution_mode: team
execution_agent: harness-backend-dev

execution_mode: main-session-direct
execution_reason: DEC-174 carve-out — check-domain.sh is a registered PreToolUse gate script
```

**A task that needs BOTH routes is TWO TASKS.** There is no split mode. FEAT-08 T-04 tried to write
one as `execution_mode: **SPLIT (D-10…)`; the regex captured `**SPLIT`, reported it as an
unrecognised token, and the eng squad hit exit 2 on it. Splitting the enum from its reason is what
makes that unwritable.

And every plan opens with a `lanes:` block, resolved against `.harness/team-config.yaml` at a named
SHA.

**Before handing a plan back, run
`python3 .agents/skills/harness/bin/check-plan-routes.py <plan path>` and fix every
violation. A non-zero exit is not a plan that is ready for signature.**
Run it here because plan time is when the fix is one edit, not a rewrite of work already built.
The `integration` CI job runs the same checker over every live plan and is a required check on
`main` (DEC-183), so skipping this does not skip the finding — it only makes it expensive.

## `verify:` is a literal block, and this one has teeth

```yaml
verify: |            # correct — newlines survive
  python3 .agents/skills/harness/bin/run-unit-tests.sh

verify: >            # WRONG — folding turns every newline into a space
  python3 ...
```

The lead carries this string **verbatim** to the member, which cross-checks it against the plan and
returns `BLOCKED` on any mismatch (`harness-zero-micro-management`). A folded scalar loads as a
different string than the one on disk, so a correct task blocks. Use `|`, or a single-line plain
scalar.

What it prevents: a task dispatched to an agent whose domain denies the write,
discovered mid-build with the build spine already open — three features running.

**An ungranted surface is legitimate.** It becomes a declared main-session step with
its ordering constraint written down — not a task that silently fails when someone
tries to dispatch it.

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

**Why it is load-bearing:** you goal-check REQ coverage against the brief — decisions logged as
requirements make the goal-check verify your own choices, not the committed outcomes.

**The D-NN bar (DEC-149):** a choice earns a `D-NN` — and the user's attention at approval — only
when ALL THREE hold: **hard to reverse**, **surprising without context**, and **a real trade-off**.
Anything failing one is a digest note. A rejected alternative a future scan would re-suggest is the
classic D-NN: record the load-bearing reason so it is not re-litigated.

## The glossary — the domain's language is yours to keep sharp

`.harness/glossary.md` is the domain's **ubiquitous language**: one
canonical term per concept, no implementation detail — a glossary, never a spec or scratch pad.
Working rules (DEC-149, adapted from domain-modeling practice):

- **Challenge drift:** a brief, dispatch or user phrase that conflicts with the glossary gets
  called out before it lands in a REQ ("the glossary defines *cancellation* as X; you seem to mean
  Y — which?").
- **Sharpen fuzz:** an overloaded term ("account" — the Customer or the User?) gets a canonical
  name before an SC is written against it.
- **Code wins:** when a stated meaning contradicts what the code does, surface the contradiction —
  the same re-derive discipline you already apply to anchors, aimed at language.
- **Update inline, at the moment a term is settled** — a feature that pins a vocabulary (an enum,
  a status set) updates the glossary in the same pass that updates your
  product-surface lens. Create the file lazily; empty is worse than absent.

## Citations and baselines rot — anchor them so they cannot (B-11, B-12)

Two failure shapes, both measured on FEAT-03 where four citations were stale before the build began:

- **Cite the FIELD, never the line, in any file the org rewrites.** `feature.json:41` was cited four
  times for `parent: none`; the orchestrator rewrote that file every run and line 41 became
  `squad: eng`. Write `feature.json github.parent` instead. Line anchors are correct only into files
  a task does not touch — source, migrations, a pinned SHA's tree.
- **A recorded baseline carries the sha it was observed at, and the condition.** "check-state.sh
  exits 1" went stale the moment the user signed the approval — the signature itself changed the
  answer. Write `observed exit 1 at <sha>, BRIEF pending`, so a later reader can tell drift from
  falsification. A bare number is unfalsifiable and therefore unverifiable.

Nothing false is asserted when either rots, which is exactly why neither gets caught: the claim
survives while the pointer dies. Both are `verify:` inputs, so a rotted anchor sends a doer to the
wrong place with a correct instruction.

## Success criteria declare how they are verified

Every `SC-NN` carries `verify: automated | inspection | uat`. An SC with no method is not verifiable, and
discovering that at ship time is too late. `automated` also names its `evidence:` test kind.

An SC must be falsifiable. "The code is clean" and "performance is good" are not criteria — if you cannot
state the observation that would prove it false, it is not one.

## Approval is not yours

You draft `BRIEF.md` and `PLAN.md`; you never mark them approved. Only the **main session** writes
`## Approval` — it is the only tier with a user channel (the orchestrator cannot reach the user
either; it returns `awaiting_user`).

**Re-planning resets approval.** If you change the task set after approval, set `## Approval` back to
pending. A stale signature must never carry onto a changed plan.

## Red flags

| Thought | Reality |
|---|---|
| "I'll specify this task loosely, the dev will figure it out" | Then you moved planning into execution, unreviewed |
| "I'll sort out who executes this at build time" | Then the build discovers it, three features running. The checker answers it now |
| "The user described it to me, so it's approved" | Describing is not approving. You cannot approve either |
| "Postgres is a requirement, they said so" | It is a decision. Apply the swap test |
| "I'll skip change_type on the trivial ones" | The qa gate blocks. `check-state.sh` will catch it |
| "This SC is obviously testable" | Then name the test kind. If you cannot, it is not `automated` |
| "I'll tidy the plan after approval" | Any change resets approval. Get it right first |
