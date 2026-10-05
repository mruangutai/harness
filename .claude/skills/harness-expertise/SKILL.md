---
name: harness-expertise
description: The two-layer memory — append granular observations to the per-feature log mid-run, and never touch the injected Expertise file outside a distillation dispatch. Loaded by all 16 agents at every spawn; the rules for actually WRITING Expertise live in `harness-distill`, which is not preloaded.
user-invocable: false
---

# Expertise

Your Expertise file is **already in your context**, injected at spawn if it exists; you never
read it yourself.

Memory has **two layers**:

| Layer | File | Written | Injected at spawn |
|---|---|---|---|
| **Observations** — hot, granular, this feature | `<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/observations/<your-agent-name>.md` | by you, mid-run, freely | **never** |
| **Expertise, craft** — how you work, anywhere | `<HARNESS_CONTROL_PLANE_ROOT>/.harness/expertise/<your-agent-name>.md` | only under a **distillation dispatch** | every spawn |
| **Expertise, repository** — true of ONE repo | `<HARNESS_CONTROL_PLANE_ROOT>/.harness/<repo>/expertise/<your-agent-name>.md` | only under a **distillation dispatch** | every spawn |
`<FEAT>` is the FEAT id on the first line of your dispatch (harness-handoff).

Craft is the default: **could this be true and useful in a repository you have never seen?** If yes,
it is craft (full rule: `harness-distill`).

Mid-run you only *observe*; distillation happens later, cold (DEC-145).

## Mid-run: append an observation

APPEND one dated observation bullet, as granular as you need; logs are never injected.
**Never Read-then-Write the log** — `check-domain` blocks whole-file Write/Edit (issue #606).
Use the merge tool below: a lock and atomic replacement preserve concurrent appends.

```bash
python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/observations-merge.py apply \
  --file <HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/observations/<your-agent-name>.md --entries -
```

Entries arrive on stdin in the log's own format: a `# Observations — <your-agent-name> — <FEAT>`
title, then `- <date>: <observation>` bullets.

Do NOT write your Expertise file mid-run. Your DIGEST's `expertise_update` is `[]` on a normal
run — the usual case, not a failure.

**Decision versus observation — a hard boundary, unchanged (DEC-23):**

| It is | Goes to |
|---|---|
| **A choice** — "we'll use Postgres", "the API returns 202 not 200" | `plan.yaml`'s `decisions:`. **Approval-gated. Not yours** |
| **An observation** — "migrations fail if run before the seed script" | Your observations log |
| **A harness defect** — a hook that didn't fire, a validator that passed garbage, a rule that backfired | `open_questions` in your DIGEST, so it reaches the harness owner. **Never Expertise** (DEC-145) |

When unsure: if a human would want to *sign off* on it, it is a decision.

## Distillation — not here, and not now

**Only an explicit distill dispatch authorizes Expertise writes** (DEC-145). Then read
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-distill/SKILL.md` first: its merge-tool-only
contract preserves earlier entries (DEC-125). Format, ops and caps load at that seam, never on
ordinary spawns (DEC-158); until then, leave both injected Expertise layers untouched.
