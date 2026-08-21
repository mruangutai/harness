---
name: harness-distill
description: How to write an Expertise file — the distillation procedure, the entry format, the ops schema and the caps. NOT preloaded (DEC-158 move 2); read it when your dispatch says "distill". Mid-run observation logging is `harness-expertise`, which every agent carries.
user-invocable: false
---

# Distillation: the only time Expertise is written

**Read this because your dispatch said "distill".** It is not preloaded — the rules below govern an
event that happens once per agent per feature, and carrying them on every spawn taxed ~33 spawns
that never write an Expertise file. Recording observations mid-run is `harness-expertise`, which you
already have.

This is **DEC-158 move 2** (conditionally-relevant skills load on demand), the same shape as
`harness-systematic-debugging`. It does **not** contradict DEC-158 move 3's *"feature-close
distillation stays inline"* — that governs the ORCHESTRATOR's dispatch procedure in
`harness/SKILL.md`, which still runs every ship and is still inline. What moved is the MEMBER's
write-rules, which fire once per agent per feature. Different tier, different frequency.

You touch `.harness/expertise/<your-agent-name>.md` **only when your dispatch explicitly says
"distill"** — at feature close, under a curation note, or via `/harness-curate`. Then:

1. Read your observations log(s) and your current Expertise (already in context).
2. Extract what passes the test: *six spawns from now, would knowing this change what I do?*
   Most observations fail it — that is normal. Lead-relayed candidates: you are the sole judge;
   rejecting with a reason is a valid outcome. At a full section a new entry enters only by
   **displacing** one you judge weaker — never by merging into a survivor; nothing weaker, it dies.
3. **Apply through the merge tool. Never write the file yourself.** Put your proposed entries in a
   scratch file, then run:

   ```
   python3 .claude/skills/harness/bin/expertise-merge.py apply \
     --file .harness/expertise/<your-agent-name>.md --entries <your scratch file>
   ```

   A **whole-file write** to an Expertise file is what loses another run's entries (DEC-125), and
   two close-outs can be in flight at once — so this is not a style preference. The tool merges;
   you no longer read-modify-write.

   Three refusals, and each wants a different response:

   | Exit | What it means | What you do |
   | --- | --- | --- |
   | 6 | the lock is held | retry once, then report it upward |
   | 7 | the same entry id carries different text | a real conflict — resolve it yourself |
   | 8 | the section cap is exceeded | curate rather than append |

   Report the ops in your DIGEST's `expertise_update` as the receipt.
4. Run `.claude/skills/harness/bin/check-expertise.sh <file>` and fix every violation before
   returning. Report per-section entry counts before and after.

## The entry format — rules, not stories

Every entry is **WHEN <situation> DO <action>**, at most **50 words**, and names **no feature or
task IDs** — no `FEAT-NN`, `T-NN`, issue `#NN`.

## Two layers — decide this BEFORE you write the entry

Your Expertise is split by **what the knowledge is about**, not by what you were working on.

| Layer | Holds | Lives at | Budget |
|---|---|---|---|
| **Craft** | how you work, true wherever you work | `.harness/expertise/<agent>.md` | 150 lines |
| **Repository** | what is true of ONE repository | `.harness/<repo>/expertise/<agent>.md` | 40 lines |

**The default is craft, and the test is one question: could this entry be true and useful in a
repository you have never seen?** If yes, it is craft. It is repository-layer only when it turns on
a path, file, decision or invariant that exists in **one** repository.

**The default matches what you already write.** Measured at `ada8e99` across all 374 entries in the
15 craft files: **16 name a repository-specific token — 4.3%** — and eight of the fifteen files name
none. Adjudicated under the rule above, 11 moved to the repository tier and 5 stayed craft, because
the token was an example rather than the thing the rule turned on. The `WHEN/DO` shape was already
pushing you toward craft before the layer had a name.

**Durable repo facts — "`tests/` is not type-checked here" — are the repository layer**, and they
still qualify without the `WHEN/DO` shape. They were previously written beside craft entries; they
no longer are.

**The failure this prevents:** a role that learns one repository's answers and carries them to the
next one. A craft entry mentioning a path as an *example* is still craft — `check-expertise.sh`
flags such entries **advisorily**, for a human to rule on, and a flag is not a violation.

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

These four section names are the only legal ones in **both** layers, and `check-expertise.sh`
enforces all of it. The spawn hook hard-truncates at the budget, so an over-budget file silently
loses its tail — the budget is physics, not advice. **Craft is 150 lines; the repository layer is
40.** The repository budget is deliberately small: the measured worst case is 4 entries in one file,
and both layers are injected at every spawn, so a generous second budget would double a per-spawn
cost DEC-105 already treats as expensive.

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
| "I learned this while working on repo X, so it is repository-layer" | The layer is about what the knowledge is ABOUT, never where you happened to learn it. Most of what you learn on one repository is craft |
| "It mentions a path, so it must be repository-layer" | Not if the path is an example. "WHEN a guard gates on an env var DO enumerate every other route" is craft even if its reason cites a real file |
| "The repository layer is where the detail goes" | It is 40 lines and the measured need is a handful. If it is filling up, you are writing stories or recipes — both are already banned above |
| "My Expertise block is missing, nothing to do" | The file may not exist yet. During distillation, create it (DEC-125) |
