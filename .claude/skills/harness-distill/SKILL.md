---
name: harness-distill
description: How to write an Expertise file — the distillation procedure, the entry format, the ops schema and the caps. NOT preloaded (DEC-158, DEC-84 split); read it when your dispatch says "distill". Mid-run observation logging is `harness-expertise`, which every agent carries.
user-invocable: false
---

# Distillation: the only time Expertise is written

**Read this because your dispatch said "distill".** It is not preloaded — the rules below govern an
event that happens once per agent per feature, and carrying them on every spawn taxed ~33 spawns
that never write an Expertise file. Recording observations mid-run is `harness-expertise`, which you
already have.

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
| "I'll add the new instance to the matching entry" | That is a story, not a rule. The rule either already covers it or gets *replaced* by a sharper one, same length |
| "My Expertise block is missing, nothing to do" | The file may not exist yet. During distillation, create it (DEC-125) |
