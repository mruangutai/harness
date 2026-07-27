---
name: harness-expertise
description: When and how to update your durable Expertise file — the update-only-if-it-changes-your-behaviour rule, the decision-versus-observation boundary, the op format with stable entry IDs, and section caps. Loaded by all 16 agents at every spawn.
---

# Expertise

Your Expertise file is **already in your context** — a `SubagentStart` hook injected it at spawn,
**if the file exists.** You never read it yourself and never go looking for it.

**If you see no Expertise block, the file does not exist yet and you are the first — so create it.**
Do not treat its absence as "I have no Expertise and there is nothing to do". That reading is why
13 of 15 of these files did not exist: the hook injects nothing and raises nothing, this rule only
ever described *updating* a file it assumed was already there, and so every agent correctly did
nothing, forever (DEC-125).

Creating it is a normal `Write` to `.harness/expertise/<your-agent-name>.md`, which is in your
`domain` — the write is permitted and scoped to that one path. Only do it when you actually have
something that passes the rule below; an empty skeleton is worse than no file, because it looks
like an agent that has learned nothing rather than one that has not run yet. Start from:

```markdown
# Expertise — <your-agent-name>

## Patterns (max 15)
- P-01: <the durable truth you just learned>

## Gotchas (max 15)

## Outcomes (max 10)

## Open (max 5)
```

**You have no `Edit`, only `Write`, so updating means read-modify-write** — the current contents are
already in your context, so reproduce them and add your entry. Never write the file from your entry
alone; that silently deletes every earlier one.

It holds what you learned about *this codebase* that you would otherwise rediscover every spawn.

## The rule

**Update ONLY if you learned something that would change how you act next time.**

Most tasks teach nothing durable and should produce **no update**. That is the normal case, not a
failure. An Expertise file that grows every run is an activity log, and nobody reads activity logs.

Ask: *six spawns from now, would knowing this change what I do?* If no, do not write it.

## Decision versus observation — a hard boundary

| It is | Goes to |
|---|---|
| **A choice** — "we'll use Postgres", "the API returns 202 not 200" | `PLAN.md ## Decisions`. **Approval-gated. Not yours** |
| **An observation** — "migrations fail if run before the seed script" | Your Expertise |

Cross this boundary and Expertise becomes a shadow decision log that bypasses your CEO's approval.
When unsure: if a human would want to *sign off* on it, it is a decision.

## How to propose an update

Updates are **ops**, and every op names its target. Reconcile as you propose — you have the file in
context, so you are the best-placed to notice a contradiction:

```yaml
expertise_update:
  - op: replace              # add | replace | merge | drop
    target: P-01             # the exact existing entry ID; omit only for `add`
    section: Patterns
    entry: "Seed script no longer required before migrations (removed in #418)."
    why: "observed migrations passing on a clean DB this run"
```

**An op naming a nonexistent target is a contract violation** — it is rejected, not guessed at.

**Prefer `replace` and `merge` over `add`.** A file of twenty near-duplicates is worse than five sharp
entries. If your new observation refines an existing one, refine it.

## Sections and caps

```
## Patterns (max 15)      durable truths about this codebase
## Gotchas (max 15)       traps that cost time before
## Outcomes (max 10)      we tried X → result, so don't re-litigate
## Open (max 5)           unresolved uncertainties in my domain
```

At a cap, set `expertise_full: true` in your DIGEST and **stop**. Do not self-prune: the tier above
you sees across runs and will send a curation note, which you then apply verbatim.

**Who writes the file:** if you hold `Write`, apply your own ops in place — the domain hook scopes you
to your own file. If you do not (leads and reviewers), the orchestrator applies them for you. Either
way the op rides your DIGEST so the update is visible before it lands.

## Red flags

| Thought | Reality |
|---|---|
| "I should record what I did this run" | That is a log. Record only what changes future behaviour |
| "This decision was important, into Expertise it goes" | Decisions are approval-gated. Wrong home |
| "I'll add this alongside the similar entry" | Then `merge` them. Near-duplicates rot the file |
| "The section is full, I'll drop the oldest" | Never self-prune. Flag `expertise_full` and stop |
| "I learned a lot today" | Almost certainly none of it is durable. No update is the common case |
