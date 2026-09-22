---
name: harness-expertise
description: The two-layer memory — append granular observations to the per-feature log mid-run, and never touch the injected Expertise file outside a distillation dispatch. Loaded by all 16 agents at every spawn; the rules for actually WRITING Expertise live in `harness-distill`, which is not preloaded.
user-invocable: false
---

# Expertise

Your Expertise file is **already in your context**, injected at spawn if it exists; you never
read it yourself.

Memory has **two layers**; confusing them is the failure this skill prevents:

| Layer | File | Written | Injected at spawn |
|---|---|---|---|
| **Observations** — hot, granular, this feature | `<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/observations/<your-agent-name>.md` | by you, mid-run, freely | **never** |
| **Expertise, craft** — how you work, anywhere | `<HARNESS_CONTROL_PLANE_ROOT>/.harness/expertise/<your-agent-name>.md` | only under a **distillation dispatch** | every spawn |
| **Expertise, repository** — true of ONE repo | `<HARNESS_CONTROL_PLANE_ROOT>/.harness/<repo>/expertise/<your-agent-name>.md` | only under a **distillation dispatch** | every spawn |
`<FEAT>` is the FEAT id on the first line of your dispatch (harness-handoff).

Craft is the default: **could this be true and useful in a repository you have never seen?** If yes,
it is craft (full rule: `harness-distill`).

Why the split: Expertise written mid-run bloats into incident narrative that taxes every spawn
(DEC-145). Mid-run you only *observe*; distillation happens later, cold.

## Mid-run: append an observation

APPEND what you learn to your observations log — one dated bullet, as granular as you like; it is
never injected, so detail is free. **Do not Read-then-Write the log** — two contexts of one agent
each writing the whole file erase each other's bullets (issue #606). Append through the merge
tool, which merges under a lock and replaces atomically:

```bash
python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/observations-merge.py apply \
  --file <HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/observations/<your-agent-name>.md --entries -
```

Entries arrive on stdin in the log's own format: a `# Observations — <your-agent-name> — <FEAT>`
title, then `- <date>: <observation>` bullets.

Do NOT write your Expertise file mid-run. Your DIGEST's `expertise_update` is `[]` on a normal
run — the usual case, not a failure. Observations are invisible to the DIGEST; the log is its own
record.

**Decision versus observation — a hard boundary, unchanged (DEC-23):**

| It is | Goes to |
|---|---|
| **A choice** — "we'll use Postgres", "the API returns 202 not 200" | `plan.yaml`'s `decisions:`. **Approval-gated. Not yours** |
| **An observation** — "migrations fail if run before the seed script" | Your observations log |
| **A harness defect** — a hook that didn't fire, a validator that passed garbage, a rule that backfired | `open_questions` in your DIGEST, so it reaches the harness owner. **Never Expertise** (DEC-145) |

When unsure: if a human would want to *sign off* on it, it is a decision.

## Distillation — not here, and not now

Writing your Expertise file happens **only under a dispatch that says "distill"**, once per feature.
The procedure, the entry format, the ops schema and the caps are **not preloaded** (DEC-158): most
spawns never write the file.

**When your dispatch says "distill", read
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-distill/SKILL.md` first.** Until then, do not
touch `<HARNESS_CONTROL_PLANE_ROOT>/.harness/expertise/<your-agent-name>.md`.

## Red flags

| Thought | Reality |
|---|---|
| "This is durable, straight into Expertise" | Mid-run, nothing goes into Expertise. Observe now, distill cold |
| "This decision was important, into the log it goes" | Decisions are approval-gated. Wrong home |
| "I learned a lot today" | Almost none of it is durable craft. `expertise_update: []` is the usual return |
| "The harness misbehaved, I'll record the workaround" | That is a bug report. Raise it as an `open_question`; a workaround in Expertise outlives the fix |
| "I'm distilling, I know the format" | Read `harness-distill` anyway. It is not in your context, and writing from your new entries alone deletes every earlier one (DEC-125) |
