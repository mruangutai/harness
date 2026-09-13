---
name: harness-spec-driven
description: Planning discipline for the product manager — every task fully specified with paths, intent, verification and traceability; no placeholders; perspectives separated from decisions. Loaded by harness-pm.
user-invocable: false
---

# Spec-Driven Planning

You author `BRIEF.md` and `plan.yaml`. They are the spec.

**`plan.yaml` is REAL YAML, and nothing in it is prose for a human** (DEC-182). Instantiate from
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/templates/plan.yaml`.

**Every write goes through a `plan-merge.py` verb. There is no other route** — the shape gate
denies `Edit`, `Write` and shell redirects.

```bash
python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/plan-merge.py apply \
  --file <HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/plan.yaml --proposal -
```

`apply` unions by `id` — adds, replaces the fields you name, never deletes — and carries the
`approval:` block forward byte identical. `plan-merge.py --help` lists every other verb and the
legal stations. `sign-approval` is **the main session's only** (DEC-120); the rework ruling beside
it is theirs too.

**No markdown in any value — no backticks, no `**bold**`, no links.** The loader rejects it or a
resolver reads it as a path nobody wrote (DEC-182).

Shipped `PLAN.md` files are never rewritten; their reader stays.

## Every task needs four things

A task missing any of them is **not written**: return the gap rather than guess. `harness_yaml.py`
(`REQUIRED_TASK_FIELDS`) refuses a task missing `id`, `title`, `change_type`, `execution_mode`,
`files`, `verify` or `intent`; the four below are what those fields must CONTAIN.

1. **Exact file anchors**, as a YAML list, one entry per file, each one of three forms: `path`;
   `path#symbol`; or `{path: <p>, quote: <q>}`. **Never `path:NN`** — a line number points at
   different code the moment `main` moves; `apply` refuses it (DEC-232). Not a comma string, not
   backticked, **no trailing annotation** like `(delete)` — the resolver takes the value verbatim.
2. **Complete intent.** Not "implement X" — the actual logic, types, structure, values. `intent:` is
   the LITERAL DISPATCH PROMPT: the doer receives it and nothing else about the task. Detail that
   only JUSTIFIES the instruction belongs in `notes/`.
3. **A `verify:` command** with the expected result: under 60 seconds, unambiguous pass/fail, no
   human interpretation. If nothing automated is possible:
   `verify: MANUAL — <what must be built first to make this automatable>`.
4. **`traces:`** — the `SC-NN` ids this task serves, as a list. No citable criterion means out of
   scope or an incomplete brief; an SC nothing traces to is an orphan the `scope` reader hunts.
   `D-NN` goes in `decisions:`, not here.

Plus **`change_type:`** on every task: the qa gate reads it to determine required tests.

## Routing is resolved at plan time

Every task carries `execution_mode:` — `team` or `main-session-direct`; the loader refuses any
other value — with `execution_agent: <persona>` for `team` or `execution_reason: <why>` for
`main-session-direct`. **A task that needs BOTH routes is TWO TASKS**; there is no split mode
(DEC-182). An ungranted surface is a **declared** main-session step with its ordering constraint
written down (DEC-179).

Every plan opens with a `lanes:` block, resolved against
`<HARNESS_CONTROL_PLANE_ROOT>/.harness/team-config.yaml` at a named SHA.

**Before handing a plan back, run
`python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/plan-merge.py check --file <plan path> --root <checkout>`
and fix every FAIL line.** It resolves every `files:` anchor, `execution_agent` route and
`traces:` id; CI re-runs the route check on `main` (DEC-183).

## `verify:` is a literal block, and this one has teeth

Write `verify:` as a literal block `|` or a single-line plain scalar, **never a folded `>`**. The
lead carries the string **verbatim** to the member, which cross-checks it against the plan and
returns `BLOCKED` on any mismatch (`harness-zero-micro-management`); a folded scalar loads as a
different string, so a correct task blocks.

## The panel result

`plan-merge.py record-panel` writes the `panel:` key from the lead's digest, every finding carried
byte for byte. **You never transcribe a panel by hand and never edit a finding's severity**
(DEC-229). Read `<HARNESS_CONTROL_PLANE_ROOT>/.claude/skills/harness/references/panel-recording.md`
in the plan team's `apply` step, when the lead's digest lands.

## Reject placeholders

`TBD`, `TODO`, vague verbs without targets, "similar to above", "follow the existing pattern",
"implement X" without saying what X produces. If you cannot fully specify a task, the *brief* is
incomplete — raise it in `open_questions`.

## Perspectives versus decisions — the boundary that matters

A **perspective** (`BRIEF.md ## Done when — by perspective`) survives changing your mind about
implementation; an **SC-NN** is the falsifiable outcome that discharges one; a **D-NN**
(`plan.yaml decisions:`) is how, architecturally, and changes if you swap the approach. The swap
test and SC well-formedness live in `harness-brief`.

**The D-NN bar (DEC-149):** a choice earns a `D-NN` — and the user's attention at approval — only
when ALL THREE hold: **hard to reverse**, **surprising without context**, **a real trade-off**.
Anything failing one is a digest note. A rejected alternative a future scan would re-suggest is the
classic D-NN — record the reason.

## The glossary — the domain's language is yours to keep sharp

`<HARNESS_CONTROL_PLANE_ROOT>/.harness/glossary.md` is the domain's **ubiquitous language**: one
canonical term per concept, no implementation detail — a glossary, never a spec (DEC-149).
**Challenge drift** — a phrase that conflicts with it is called out before it lands in a
perspective. **Sharpen fuzz** — an overloaded term gets a canonical name before an SC is written
against it. **Code wins** — a stated meaning that contradicts the code is surfaced, not adopted.
**Update inline** when a term is settled; create the file lazily, empty is worse than absent.

## Citations and baselines rot — anchor them so they cannot

- **Cite the FIELD or the SYMBOL, never the line**: `feature.json github.parent`, not
  `feature.json:41` (DEC-232).
- **A recorded baseline carries the sha it was observed at, and the condition**: `observed exit 1
  at <sha>, BRIEF pending` — the signature itself can change the answer.

Both are `verify:` inputs.

## Approval is not yours

You draft `BRIEF.md` and `plan.yaml`; you never mark them approved. Only the **main session** writes
`## Approval` — the only tier with a user channel. **Re-planning resets approval**: any verb that
changes the task set after signature sets `approval.status` back to `pending` on its own; only
`sign-approval` writes `approved`.

## Red flags

| Thought | Reality |
|---|---|
| "I'll specify this task loosely, the dev will figure it out" | Then you moved planning into execution, unreviewed |
| "I'll sort out who executes this at build time" | Then the build discovers it mid-run. `check` answers it now |
| "The user described it to me, so it's approved" | Describing is not approving. You cannot approve either |
| "Postgres is a requirement, they said so" | It is a decision. A perspective survives the swap test; a decision does not |
| "I'll skip change_type on the trivial ones" | The loader refuses the task and the qa gate blocks |
| "This SC is obviously testable" | Then name the test kind. If you cannot, it is not `automated` |
| "I'll tidy the plan after approval" | Any change resets approval. Get it right first |
