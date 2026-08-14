---
name: harness-expertise
description: The two-layer memory — append granular observations to the per-feature log mid-run, and never touch the injected Expertise file outside a distillation dispatch. Loaded by all 16 agents at every spawn; the rules for actually WRITING Expertise live in `harness-distill`, which is not preloaded.
user-invocable: false
---

# Expertise

Your Expertise file is **already in your context** — a `SubagentStart` hook injected it at spawn,
**if the file exists.** You never read it yourself and never go looking for it.

Memory has **two layers**, and confusing them is the failure this skill exists to prevent:

| Layer | File | Written | Injected at spawn |
|---|---|---|---|
| **Observations** — hot, granular, this feature | `.harness/features/<FEAT>/observations/<your-agent-name>.md` | by you, mid-run, freely | **never** |
| **Expertise, craft** — how you work, anywhere | `.harness/expertise/<your-agent-name>.md` | only under a **distillation dispatch** | every spawn |
| **Expertise, repository** — true of ONE repo | `.harness/<repo>/expertise/<your-agent-name>.md` | only under a **distillation dispatch** | every spawn |

Craft is the default: **could this be true and useful in a repository you have never seen?** If yes,
it is craft. The full rule is in `harness-distill`, which you read when you are told to distill.

Why the split: mid-run-written Expertise bloated into incident narrative that taxed every spawn
(DEC-145). Mid-run you only *observe*; distillation happens later, cold.

## Mid-run: append an observation

Learned something that might matter later? APPEND it to your observations log — one dated bullet,
as granular as you like: feature IDs, line anchors, incident narrative, all welcome. It is never
injected, so detail is free. Create the file on first use; `Write`-not-`Edit` means appending is read-modify-write — Read the
log first if it exists.

```markdown
# Observations — <your-agent-name> — <FEAT>

- 2026-07-28: brief said two HTTP routes, app.py has four (grep `@app.route`); documentor
  propagated the wrong count into the BLUF before I caught it.
```

Do NOT write your Expertise file mid-run. Your DIGEST's `expertise_update` is `[]` on a normal
run — that is the usual case, not a failure. Observations are invisible to the DIGEST; the log is
its own record.

**Decision versus observation — a hard boundary, unchanged:**

| It is | Goes to |
|---|---|
| **A choice** — "we'll use Postgres", "the API returns 202 not 200" | `plan.yaml`'s `decisions:` (`PLAN.md ## Decisions` on the pre-DEC-182 format). **Approval-gated. Not yours** |
| **An observation** — "migrations fail if run before the seed script" | Your observations log |
| **A harness defect** — a hook that didn't fire, a validator that passed garbage, a rule that backfired | `open_questions` in your DIGEST, so it reaches the harness owner. **Never Expertise** — a bug report ages into a stale workaround the moment the bug is fixed |

Cross this boundary and the log becomes a shadow decision log that bypasses your CEO's approval.
When unsure: if a human would want to *sign off* on it, it is a decision.

## Distillation — not here, and not now

Writing your Expertise file happens **only under a dispatch that says "distill"**, once per feature.
Those rules — the procedure, the entry format, the ops schema, the caps — are **not preloaded**
(DEC-158): they governed ~33 spawns per feature that never write the file.

**When your dispatch says "distill", read
`.claude/skills/harness-distill/SKILL.md` first.** Until then the only thing you need to know is
that you do not touch `.harness/expertise/<your-agent-name>.md`.

## Red flags

| Thought | Reality |
|---|---|
| "This is durable, straight into Expertise" | Mid-run, nothing goes into Expertise. Observe now, distill cold |
| "This decision was important, into the log it goes" | Decisions are approval-gated. Wrong home |
| "The entry needs the feature context to make sense" | Then it is not durable yet. Leave it in observations |
| "I learned a lot today" | Almost certainly none of it passes the six-spawns test. `expertise_update: []` is the usual return |
| "The harness misbehaved, I'll record the workaround" | That is a bug report. Raise it as an `open_question`; a workaround in Expertise outlives the fix |
| "I'm distilling, I know the format" | Read `harness-distill` anyway. It is not in your context, and writing from your new entries alone deletes every earlier one (DEC-125) |
