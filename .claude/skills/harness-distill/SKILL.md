---
name: harness-distill
description: How to write an Expertise file — the distillation procedure, the entry format, the ops schema and the caps. NOT preloaded (DEC-158 move 2); read it when your dispatch says "distill". Mid-run observation logging is `harness-expertise`, which every agent carries.
user-invocable: false
---

# Distillation: the only time Expertise is written

**Read this because your dispatch said "distill".** Not preloaded — these rules fire once per agent
per feature (DEC-158). Mid-run observation logging is `harness-expertise`, which you already have.

You touch `<HARNESS_CONTROL_PLANE_ROOT>/.harness/expertise/<your-agent-name>.md` **only when your dispatch explicitly says
"distill"** — at feature close, under a curation note, or under the `harness-curate` skill. Then:

1. Read your observations log(s) and your current Expertise (already in context).
2. Extract what passes the test: *six spawns from now, would knowing this change what I do?*
   Most observations fail it — that is normal. Lead-relayed candidates: you are the sole judge;
   rejecting with a reason is a valid outcome. At a full section a new entry enters only by
   **displacing** one you judge weaker — never by merging into a survivor; nothing weaker, it dies.
3. **Apply through the merge tool. Never write the file yourself.** Put your proposed entries in a
   scratch file, then run:

   ```
   python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/expertise-merge.py apply \
     --file <HARNESS_CONTROL_PLANE_ROOT>/.harness/expertise/<your-agent-name>.md --entries <your scratch file>
   ```

   A **whole-file write** to an Expertise file is what loses another run's entries (DEC-125), and
   two close-outs can be in flight at once — so this is not a style preference. The tool merges;
   you no longer read-modify-write.

   The tool refuses without writing. Each exit wants a different response:

   | Exit | Subcommand | What it means | What you do |
   | --- | --- | --- | --- |
   | 6 | both | the lock is held | retry once, then report it upward |
   | 7 | both | `CONFLICT` — the same entry id carries different text | a real conflict — resolve it yourself |
   | 8 | both | `CAP EXCEEDED` | curate rather than append |
   | 9 | both | `--file` is not an Expertise file | you named the wrong path — fix it, never work around it |
   | 10 | `ops` | `MISSING TARGET` | rejected, never guessed at — a contract violation |
   | 11 | both | `AMBIGUOUS TARGET` — the id appears twice in its section, or two ops in one proposal name the same section and id | |
   | 12 | `ops` | `MALFORMED OPS` | |

   Report the ops in your DIGEST's `expertise_update` as the receipt.
4. Run `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/check-expertise.py <file>` and fix every violation before
   returning. Report per-section entry counts before and after.

**Your DIGEST reviews no diff and ran no suite, and says so.** A distill dispatch carries
`HARNESS-MISSION: distill` on its own line; the host forwards it and the digest validator then
REQUIRES the did-nothing spelling of your gate fields — qa `suite: n/a` and `matrix_ok: n/a`,
code-reviewer `code_grade: n_a` and `reviewed: none` — and refuses a `suite: pass` or a graded
range as decoration (#1855). A lead hosting distill members repeats the line in each member's
dispatch; a member whose dispatch lacks it has the lead fix the dispatch, never the digest.

## The entry format — rules, not stories

Every entry is **WHEN <situation> DO <action>**, at most **50 words**, and names **no feature or
task IDs** — no `FEAT-NN`, `T-NN`, issue `#NN`.

## Two layers you write — decide this BEFORE you write the entry

Your Expertise is split by **what the knowledge is about**, not by what you were working on.

| Layer | Holds | Lives at | Budget |
|---|---|---|---|
| **Craft** | how you work, true wherever you work | `<HARNESS_CONTROL_PLANE_ROOT>/.harness/expertise/<agent>.md` | 150 lines |
| **Repository** | what is true of ONE repository | `<HARNESS_CONTROL_PLANE_ROOT>/.harness/<repo>/expertise/<agent>.md` | 40 lines |

A third, global tier lives in your home directory (`~/.harness`, same `expertise/<agent>.md`
layout) and is injected ahead of both by `inject-expertise.py`; you never write it from a run.

**The default is craft, and the test is one question: could this entry be true and useful in a
repository you have never seen?** If yes, it is craft. It is repository-layer only when it turns on
a path, file, decision or invariant that exists in **one** repository. Measured at `ada8e99`: 4.3%
of 374 craft entries named a repo-specific token, so craft is the default by a wide margin (DEC-158).

**Durable repo facts — "`tests/` is not type-checked here" — are the repository layer**, and they
still qualify without the `WHEN/DO` shape.

**The failure this prevents:** a role that learns one repository's answers and carries them to the
next one. A craft entry mentioning a path as an *example* is still craft — `check-expertise.py`
flags such entries **advisorily**, for a human to rule on, and a flag is not a violation.

A **recipe** (setup steps, config values, field names) rots with the code — it qualifies only as a
pointer to a living in-repo exemplar, never as inlined values recalled from an old run.

An entry citing more than one incident is a distillation smell: keep the rule, drop the cases.
A `merge` result is **no longer than the longer input**; instance lists are banned.

**When a distillation touches a SKILL.md — an Expertise entry promoted into a rule skill, or a
skill edited to carry what a run learned — the three-part rule for skill text applies (DEC-158,
FEAT-60):** *if a gate refuses on it, name the gate; if a decision holds it, point; if one seam
needs it, reference it.* A skill carries the rule, one clause of why, and a pointer — never the
gate's field list, the decision's evidence, or a procedure preloaded on every wake.
`check-skill-weight.py` measures the preload and `check-state.py` notes an excess.

```markdown
# Expertise — <your-agent-name>

## Patterns (max 15)
- P-01: WHEN a brief hands down facts or anchors DO grep the discriminating anchor yourself
  before dispatch — brief framing and counts are the least trustworthy input you receive.

## Gotchas (max 15)

## Outcomes (max 10)

## Open (max 5)
```

These four section names are the only legal ones in **both** layers, and `check-expertise.py`
enforces all of it. The spawn hook hard-truncates at the budget, so an over-budget file silently
loses its tail — the budget is physics, not advice. **Craft is 150 lines; the repository layer is
40.** The repository budget is deliberately small: the measured worst case is 4 entries in one file,
and both layers are injected at every spawn, so a generous second budget would double a per-spawn
cost DEC-105 already treats as expensive.

Updates are **ops**. The vocabulary is exactly `add | replace | merge | drop`. Every op requires
both `target` and `section`: `target` names the entry ID, `section` names one of the four sections,
and resolution never leaves that section. There is no whole-file lookup and no omitted section.

```yaml
expertise_update:
  - op: replace              # add | replace | merge | drop
    target: P-01
    section: Patterns
    entry: "WHEN running migrations DO run the seed script first — they fail on a clean DB."
    why: "three observations this feature, same root cause"
```

`merge` is an authoring outcome, not a mechanism op. Express it as a replace on the surviving id
plus a drop of the absorbed id; the tool refuses an `op: merge`. Apply the JSON form of the
`expertise_update` list with:

```bash
python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/expertise-merge.py ops --file <expertise file> --ops <path or ->
```

The refusals are the table in step 3. Add-only proposals may still use `apply --entries`, unchanged.

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
