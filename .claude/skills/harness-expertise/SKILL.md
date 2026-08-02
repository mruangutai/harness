---
name: harness-expertise
description: The two-layer memory — append granular observations to the per-feature log mid-run, and write the injected Expertise file only under a distillation dispatch, in rule form, mechanically capped. Loaded by all 16 agents at every spawn.
user-invocable: false
---

# Expertise

Your Expertise file is **already in your context** — a `SubagentStart` hook injected it at spawn,
**if the file exists.** You never read it yourself and never go looking for it.

Memory has **two layers**, and confusing them is the failure this skill exists to prevent:

| Layer | File | Written | Injected at spawn |
|---|---|---|---|
| **Observations** — hot, granular, this feature | `.harness/features/<FEAT>/observations/<your-agent-name>.md` | by you, mid-run, freely | **never** |
| **Expertise** — cold, rule-form, durable | `.harness/expertise/<your-agent-name>.md` | only under a **distillation dispatch** | every spawn |

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
| **A choice** — "we'll use Postgres", "the API returns 202 not 200" | `PLAN.md ## Decisions`. **Approval-gated. Not yours** |
| **An observation** — "migrations fail if run before the seed script" | Your observations log |
| **A harness defect** — a hook that didn't fire, a validator that passed garbage, a rule that backfired | `open_questions` in your DIGEST, so it reaches the harness owner. **Never Expertise** — a bug report ages into a stale workaround the moment the bug is fixed |

Cross this boundary and the log becomes a shadow decision log that bypasses your CEO's approval.
When unsure: if a human would want to *sign off* on it, it is a decision.

## Distillation: the only time Expertise is written

You touch `.harness/expertise/<your-agent-name>.md` **only when your dispatch explicitly says
"distill"** — at feature close, under a curation note, or via `/harness-curate`. Then:

1. Read your observations log(s) and your current Expertise (already in context).
2. Extract what passes the test: *six spawns from now, would knowing this change what I do?*
   Most observations fail it — that is normal. Lead-relayed candidates: you are the sole judge;
   rejecting with a reason is a valid outcome. At a full section a new entry enters only by
   **displacing** one you judge weaker — never by merging into a survivor; nothing weaker, it dies.
3. Write the file — create it if absent, read-modify-write if not. **Never write it from your new
   entries alone; that silently deletes every earlier one** (DEC-125). Report the ops in your
   DIGEST's `expertise_update` as the receipt.
4. Run `.claude/skills/harness/bin/check-expertise.sh <file>` and fix every violation before
   returning. Report per-section entry counts before and after.

## The entry format — rules, not stories

Every entry is **WHEN <situation> DO <action>**, at most **50 words**, and names **no feature or
task IDs** — no `FEAT-NN`, `T-NN`, issue `#NN`. Durable repo facts ("`tests/` is not type-checked
here") qualify without the WHEN/DO shape, but the caps still hold.

A **recipe** (setup steps, config values, field names) rots with the code — it qualifies only as a
pointer to a living in-repo exemplar, never as inlined values recalled from an old run.

An entry citing more than one incident is a distillation smell: keep the rule, drop the cases.
A `merge` result is **no longer than the longer input**; instance lists are banned.

```markdown
# Expertise — <your-agent-name>

## Patterns (max 15)
- P-01: WHEN a brief hands down facts or anchors DO grep the discriminating anchor yourself
  before dispatch — brief framing and counts are the least trustworthy input you receive.

## Gotchas (max 15)

## Outcomes (max 10)

## Open (max 5)
```

These four section names are the only legal ones, the file budget is **150 lines**, and
`check-expertise.sh` enforces all of it. The spawn hook hard-truncates at 150 lines, so an
over-budget file silently loses its tail — the budget is physics, not advice.

Updates are **ops**, each naming its target:

```yaml
expertise_update:
  - op: replace              # add | replace | merge | drop
    target: P-01             # the exact existing entry ID; omit only for `add`
    section: Patterns
    entry: "WHEN running migrations DO run the seed script first — they fail on a clean DB."
    why: "three observations this feature, same root cause"
```

An op naming a nonexistent target is a contract violation — it is rejected, not guessed at.

At a section cap during distillation, condense until you are under it — distillation IS the
curation step, so the old flag-and-stop rule does not apply to you here. If you genuinely cannot
condense below a cap without losing durable rules, set `expertise_full: true` in your DIGEST and
let the tier above decide.

## Red flags

| Thought | Reality |
|---|---|
| "This is durable, straight into Expertise" | Mid-run, nothing goes into Expertise. Observe now, distill cold |
| "I'll add the new instance to the matching entry" | That is a story, not a rule. The rule either already covers it or gets *replaced* by a sharper one, same length |
| "This decision was important, into the log it goes" | Decisions are approval-gated. Wrong home |
| "The entry needs the feature context to make sense" | Then it is not durable yet. Leave it in observations |
| "I learned a lot today" | Almost certainly none of it passes the six-spawns test. `expertise_update: []` is the usual return |
| "The harness misbehaved, I'll record the workaround" | That is a bug report. Raise it as an `open_question`; a workaround in Expertise outlives the fix |
| "My Expertise block is missing, nothing to do" | The file may not exist yet. During distillation, create it (DEC-125) |
