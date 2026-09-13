---
name: harness-spec-driven
description: Planning discipline for the product manager — every task fully specified with paths, intent, verification and traceability; no placeholders; perspectives separated from decisions. Loaded by harness-pm.
user-invocable: false
---

# Spec-Driven Planning

You author `BRIEF.md` and `plan.yaml`. They are the spec — there is no separate spec artifact.

**`plan.yaml` is REAL YAML, and nothing in it is prose for a human** (DEC-182). The human reads
`BRIEF.md`. Instantiate from `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/templates/plan.yaml`.

**Every write goes through a verb. There is no other route** — not an `Edit`, not a `Write`,
not a shell redirect. The shape gate denies all three, and a station outside the vocabulary
`harness.json` declares is refused before the file is opened.

```bash
python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/plan-merge.py apply \
  --file <HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/plan.yaml --proposal -
```

`apply` unions by task and decision `id`: it adds what is new and replaces the fields your
proposal names on an existing id, so a second pm spawn cannot delete the first's tasks and a
panel fix does not need a `/tmp` driver. The `approval:` block is carried forward byte identical
and any approval block in your proposal is ignored; any verb that changes the task set resets
`approval.status` to `pending` on its own (SC-08).

The other verbs change a value `apply` will not touch, each splicing under the same lock:

- `set-task-station --file <plan.yaml> --task T-NN --station <name>` — a task's station.
- `set-feature-station --file <plan.yaml> --station <name>` — the feature's own station.
- `set-lanes --file <plan.yaml> --value-file <lanes.yaml>` — the `lanes:` block.
- `record-panel --file <plan.yaml> --digest <digest.md> --cycle N` — the `panel:` key, from the
  lead's digest (below).
- `check --file <plan.yaml> --root <checkout>` — writes nothing; resolves every anchor, every
  route and every `traces:` id.
- `sign-approval --file <plan.yaml> --by <name> --date <YYYY-MM-DD> [--rework rounds=N,minutes=M
  --decision <path>]` — **the main session only.** You never sign; approval records a decision
  only the user can have made (DEC-120), and the rework ruling beside it is theirs too (SC-15).

A station is one of the six `harness.json` declares — `backlog plan ready building review
done` — or `abandoned`. `pending` is not a station and never was one.

**No markdown in any value — no backticks, no `**bold**`, no links.** They are decoration in a data
file. Measured on the format this replaced: `safe_load` over every task block in the four live plans
failed 43 of 44 times, 26 of them because `files:` began with a backtick. A value carrying
decoration is either rejected by the loader or handed to a resolver as a path nobody wrote.

Shipped `PLAN.md` files are never rewritten; their reader stays. You author `plan.yaml`.

## Every task needs four things

A task missing any of them is **not written**. Identify the gap and return it rather than guessing:

1. **Exact file anchors**, as a YAML list — one entry per file. Each entry is one of three
   forms and nothing else: `path`; `path#symbol` (a definition in the file); or
   `{path: <p>, quote: <q>}` (a line containing `<q>` verbatim). **Never `path:NN`** — a line
   number points at different code the moment `main` moves, and `apply` refuses it at write
   (SC-07). Not a comma string, not backticked, and **no trailing annotation** like `(delete)`:
   the resolver takes the value verbatim, so an annotation becomes part of the path and resolves
   to nothing. Intent about a path goes in `intent:`, not beside it.
2. **Complete intent.** Not "implement X" — the actual logic, types, structure, values. `intent:` is
   the LITERAL DISPATCH PROMPT: the agent doing the work receives it and nothing else about the
   task. Detail that only JUSTIFIES the instruction — probe transcripts, why an earlier draft was
   wrong — belongs in `notes/`, not here.
3. **A `verify:` command** with the expected result. Runs in under 60 seconds, gives an unambiguous
   pass/fail, needs no human interpretation. If nothing automated is possible, say so explicitly:
   `verify: MANUAL — <what must be built first to make this automatable>`.
   **Write it as a literal block `|`, never a folded `>`** — see below; this one is not a style
   preference.
4. **`traces:`** — the `SC-NN` ids this task serves, as a list. A task that cannot cite a
   criterion is either out of scope or the brief is incomplete; a criterion no task traces to is
   an orphan the plan `scope` reader hunts (SC-12). `D-NN` goes in the `decisions:` block, not
   here: carrying both made the field mean two things and nothing ever read the second.

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

And every plan opens with a `lanes:` block, resolved against `<HARNESS_CONTROL_PLANE_ROOT>/.harness/team-config.yaml` at a named
SHA.

**Before handing a plan back, run
`python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/plan-merge.py check --file <plan path> --root <checkout>`
and fix every FAIL line.** It resolves every `files:` anchor, every `execution_agent` route
through the same resolver the build hook consults, and every `traces:` id against the BRIEF. A
non-zero exit is not a plan that is ready for signature.
Run it here because plan time is when the fix is one edit, not a rewrite of work already built.
The `integration` CI job runs `check-plan-routes.py` over every live plan and is a required check
on `main` (DEC-183), so skipping this does not skip the finding — it only makes it expensive.

## `verify:` is a literal block, and this one has teeth

```yaml
verify: |            # correct — newlines survive
  python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/run-unit-tests.sh

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

## The panel result

`plan-merge.py record-panel --file <plan.yaml> --digest <lead digest.md> --cycle N` writes the
top-level `panel` key from the lead's fenced DIGEST block: one `panel.readers` entry for EVERY
named reader, `skipped` ones included with the persona and the lead's reason, every finding with
its `kind` and severity carried byte for byte. You never transcribe it by hand and never edit a
finding's severity (SC-05) — a run whose only work is copying one file into another is the
zero-value run FEAT-59 exists to remove. A `form` finding you fixed in the same run stays present
with disposition `resolved` and `resolved_by: T-NN`; a `substance` finding re-gates only the
tasks it names. The operator's overrule belongs in `approval.rulings`; that is the main
session's write (`sign-approval --overrule`), never pm's.

## Reject placeholders

`TBD`, `TODO`, vague verbs without targets, "similar to above", "follow the existing pattern",
"implement X" without saying what X produces. If you cannot fully specify a task, that is a signal the
*brief* is incomplete — raise it in `open_questions` rather than writing a task nobody can execute.

## Perspectives versus decisions — the boundary that matters

| It is | Where | Test |
|---|---|---|
| **a perspective** — what a named person can rely on once this ships | `BRIEF.md ## Done when — by perspective` | survives changing your mind about implementation |
| **SC-NN** — the observable outcome that discharges one perspective | `BRIEF.md ## Success criteria` | falsifiable, and tagged `(<perspective>)` |
| **D-NN** — how, architecturally | `plan.yaml decisions:` | changes if you swap the approach |

*"**end user** — I can sign in with my Google account"* is a perspective. *"Use Supabase social
login"* is a decision. Swap Supabase for Auth0: the perspective is untouched, the decision is not.

**Why it is load-bearing:** the goal-check grades each perspective against the diff — decisions
logged as perspectives make the goal-check verify your own choices, not the outcomes the people
judging the result were promised.

**The D-NN bar (DEC-149):** a choice earns a `D-NN` — and the user's attention at approval — only
when ALL THREE hold: **hard to reverse**, **surprising without context**, and **a real trade-off**.
Anything failing one is a digest note. A rejected alternative a future scan would re-suggest is the
classic D-NN: record the load-bearing reason so it is not re-litigated.

## The glossary — the domain's language is yours to keep sharp

`<HARNESS_CONTROL_PLANE_ROOT>/.harness/glossary.md` is the domain's **ubiquitous language**: one
canonical term per concept, no implementation detail — a glossary, never a spec or scratch pad.
Working rules (DEC-149, adapted from domain-modeling practice):

- **Challenge drift:** a brief, dispatch or user phrase that conflicts with the glossary gets
  called out before it lands in a perspective ("the glossary defines *cancellation* as X; you seem
  to mean Y — which?").
- **Sharpen fuzz:** an overloaded term ("account" — the Customer or the User?) gets a canonical
  name before an SC is written against it.
- **Code wins:** when a stated meaning contradicts what the code does, surface the contradiction —
  the same re-derive discipline you already apply to anchors, aimed at language.
- **Update inline, at the moment a term is settled** — a feature that pins a vocabulary (an enum,
  a status set) updates the glossary in the same pass that updates your
  product-surface lens. Create the file lazily; empty is worse than absent.

## Citations and baselines rot — anchor them so they cannot (B-11, B-12)

Two failure shapes, both measured on FEAT-03 where four citations were stale before the build began:

- **Cite the FIELD or the SYMBOL, never the line.** `feature.json:41` was cited four times for
  `parent: none`; the orchestrator rewrote that file every run and line 41 became `squad: eng`.
  Write `feature.json github.parent` instead, and in a task's `files:` write `path#symbol` or
  `{path, quote}`. There is no file a line number is safe into: FEAT-54's first build dispatch
  BLOCKED on five plan paths that seven reader cycles had passed, because nothing resolved them.
  `plan-merge.py` refuses `path:NN` at write (SC-07).
- **A recorded baseline carries the sha it was observed at, and the condition.** "check-state.sh
  exits 1" went stale the moment the user signed the approval — the signature itself changed the
  answer. Write `observed exit 1 at <sha>, BRIEF pending`, so a later reader can tell drift from
  falsification. A bare number is unfalsifiable and therefore unverifiable.

Nothing false is asserted when either rots, which is exactly why neither gets caught: the claim
survives while the pointer dies. Both are `verify:` inputs, so a rotted anchor sends a doer to the
wrong place with a correct instruction.

## Success criteria declare who they are for and how they are verified

Every `SC-NN` is written `- SC-NN (<perspective>): ...` and carries `verify: automated |
inspection | uat`. The tag names a perspective the BRIEF declares; a perspective no SC discharges
and an SC with no perspective are both refused at write (INV-38). An SC with no method is not
verifiable, and discovering that at ship time is too late. `automated` also names its `evidence:`
test kind.

An SC must be falsifiable. "The code is clean" and "performance is good" are not criteria — if you cannot
state the observation that would prove it false, it is not one. And it must be scoped to this
feature: a `verify:` that runs `check-state.sh` or `check-domain.sh` with no feature-scoped
argument grades the whole repository and is refused (INV-41, SC-16). The full well-formedness
list is in `harness-brief`.

## Approval is not yours

You draft `BRIEF.md` and `plan.yaml`; you never mark them approved. Only the **main session** writes
`## Approval` — it is the only tier with a user channel (the orchestrator cannot reach the user
either; it returns `awaiting_user`).

**Re-planning resets approval.** Any verb that changes the task set after signature sets
`approval.status` back to `pending` on its own (SC-08); only `sign-approval` writes `approved`.
A stale signature never carries onto a changed plan, and you never write the field yourself.

## Red flags

| Thought | Reality |
|---|---|
| "I'll specify this task loosely, the dev will figure it out" | Then you moved planning into execution, unreviewed |
| "I'll sort out who executes this at build time" | Then the build discovers it, three features running. The checker answers it now |
| "The user described it to me, so it's approved" | Describing is not approving. You cannot approve either |
| "Postgres is a requirement, they said so" | It is a decision. Apply the swap test — a perspective survives it, a decision does not |
| "I'll skip change_type on the trivial ones" | The qa gate blocks. `check-state.sh` will catch it |
| "This SC is obviously testable" | Then name the test kind. If you cannot, it is not `automated` |
| "I'll tidy the plan after approval" | Any change resets approval. Get it right first |
