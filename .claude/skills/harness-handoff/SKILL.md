---
name: harness-handoff
description: The universal return contract and output discipline for every harness agent — the VERDICT/DIGEST/artifact return, BLUF, pointers not payloads, decide versus ask. Loaded by all 16 agents at every spawn.
user-invocable: false
---

# Handoff

**Handoff is by file path, never by conversation.** Your successor's context is as fresh as yours:
durable artifact, compact signal.

## Your return — three parts, always

````
```yaml
VERDICT: PASS | FAIL | BLOCKED | ESCALATE
DIGEST:
  headline: <one line, the conclusion — not what you did>
  <your role's fields — see your role rule>
  open_questions:
    - { id: Q1, question: "<text>", blocking: true|false }
  files_touched: [<paths>]        # [] if you changed none
  expertise_update: [<ops>]       # [] except under a distillation dispatch (harness-expertise)
artifact: <path to what you wrote>
```
````

**The ```` ```yaml ```` fence is part of the return** — emit both fences; only the fenced block is
parsed (DEC-172).

| VERDICT | Means |
|---|---|
| `PASS` | done. May carry advisory notes |
| `FAIL` | a gate failed. Retrying or looping back is meaningful |
| `BLOCKED` | cannot proceed. Looping back is futile — escalate |
| `ESCALATE` | needs the tier above (lead → orchestrator → user) |

**`bin/validate-digest.py` is the contract** — exact tokens and field names, since the runner routes
on them; every field present, "nothing" as an explicit `[]` or `none`, never an omitted key;
`findings` and `fail_first` checked inside the list. Violation → `BLOCKED (contract violation)`.

**Never invent a verdict** — undeterminable is `BLOCKED`, with why.

**Dispatchers** (orchestrator, lead) read
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/runtime-handoff.md` before the run's
first dispatch — wakes, verification before accepting a verdict, never waiting.

## Harness-owned paths — anchored, never relative

- `HARNESS_CONTROL_PLANE_ROOT: <absolute path>` in your starting context is the Harness control plane, not your working directory. `UNRESOLVED` → `VERDICT: BLOCKED`; never guess.
- `<HARNESS_CONTROL_PLANE_ROOT>` prefixes every Harness-owned read; `<HARNESS_FEATURE_TREE_ROOT>` prefixes every feature-directory write. Never interchangeable; never a bare relative Harness-owned path in an instruction.
- The control-plane root is read-only to you; write grants are unchanged (check-domain.sh).

## Writing the artifact

- **BLUF.** The conclusion first, never "I explored X, then Y."
- **Claims plus pointers, never payloads.** "Auth is JWT (`auth/mw.ts:42`)" — they have the path.
- **Open questions, explicitly** — the next agent's to-do list.
- **Bounded — one screen.** Length is the enemy of signal.

Routing reads only VERDICT and DIGEST; put what it depends on there.

**Where it goes — the per-feature path your persona owns, never one a dispatch invents.** Read
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/artifact-paths.md` before your first
feature-directory write: your path, the root-resolve command, the no-shell rule. The five engineers
and the documentor own no path and write the receipt
`<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/notes/receipt-<your-agent-name>-<runid>.md`
— **not your observations log**, which no spawn ever injects.

## Decide or ask — scoped by reversibility

**Cheap and reversible** (naming, local structure, test shape): decide; record it in the DIGEST.
**Expensive or hard to reverse** (schema, API contract, new dependency): ask via `open_questions`.
**Changes scope, the goal, or an approved decision**: always ask — it is not yours.

**Never yours: removing a worktree** — `git worktree remove` exits 0 from inside the tree it deletes;
the main session or `post-merge` hook does it from outside. **Out of scope is out of scope**: note
it in the DIGEST, never fix it while you are there. **An open question does not block you**: raise
it, do what you can, return; a member never waits on a human.

## Consulting decisions — cited is a floor, never a ceiling

Cited decisions are the **minimum**, not the set: the dispatcher's framing is a hypothesis.
**Never read an authority file whole**: index first, then only the entries that bear on your task.
**Go broader** when a citation references an uncited decision, when the citations do not cover what
you judge, when your Expertise implies an omitted rule, or when "surely this was decided already"
fires.
