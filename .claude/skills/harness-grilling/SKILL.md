---
name: harness-grilling
user-invocable: false
description: Dialog to clarity before anything is built — a relentless one-question-at-a-time interview that names the destination, settles the decision tree, and records fog and out-of-scope. Blocking step zero of /harness-plan. Run by the main session only.
---

# Grilling — reach shared understanding before the org spends a spawn

**Only the main session runs this.** It is the sole tier with a user channel (DEC-120), so a
subagent cannot grill anyone — and an agent that answers its own questions has broken the
discipline entirely. Adapted from Matt Pocock's `grilling`, `batch-grill-me` (the frontier round)
and `wayfinder` (MIT), re-homed onto harness machinery (DEC-164/167).

Why it is blocking: pm plans from what it is told. Every unstated assumption at this moment
becomes a perspective nobody meant, an SC that cannot be verified, or a build cycle spent
discovering the question. **Five kaya premises briefed as fact were FALSE at HEAD** on one
feature — the cheapest possible moment to find that is here, in conversation, before a spawn.

Three ways in, and they differ only in what follows:

- **A loose idea or a feature request** — grill it to clarity, write the artifact with its
  `## Mission`, then offer `/harness-plan` or `/harness-patch` (whichever the mission names) with
  the artifact path as pm's input. Do not start planning unasked.
- **Inside repository registration** — `harness-add-repo` runs the technical interview.
- **Standalone** ("stress-test this", "grill me on X") — write the artifact and stop. Nothing
  downstream is implied.

Skipping this step is the user's call to make explicitly, never yours to assume.

## The discipline

- **One question at a time by default**, with your recommended answer attached — several *dependent*
  questions at once is bewildering and gets you the first answer plus noise. Wait for each.
- **Except: batch a round that is BOTH independent and shallow.** Hold the decision tree in mind;
  its **frontier** is every question whose prerequisites are settled. Ask as one numbered round the
  frontier questions that are *also* shallow — a recommendation plus a pick settles each — then wait;
  their answers push the frontier outward for the next round (DEC-167). **Serialise anything
  dependent** (an answer changes the later questions) **or deep** (it needs back-and-forth to reach
  an answer): independence alone does not make three deep questions one round. The user's stated
  preference — "one at a time", "give me everything" — outranks this heuristic.
- **Facts are YOURS to find; decisions are the user's.** If the filesystem, git, the codebase map,
  or a command can answer it, go look — never ask the user something you could check. Dispatch an
  `Explore` subagent for anything broad. Then put the *decision* to them and wait.
- **Walk the decision tree, dependencies first.** A question whose answer depends on an open
  question belongs later. Settle the parent, then ask what it unblocks.
- **Challenge the language as you go** — a term that conflicts with `.harness/glossary.md`
  gets called out here, not after it lands in a perspective (`harness-spec-driven`'s glossary rules).
- **Never act on it until the user confirms** you have reached shared understanding.

**One sitting is the scope of this skill.** If the destination itself needs deciding, or a question
stalls on a fact or a prototype you do not have, this idea is bigger than a conversation: promote it
to `harness-wayfinding` (a persistent map, one decision per session), carrying what is already
settled. Do not grind a fog-wrapped idea through a single exhausting session (DEC-165).

## Name the destination first

The first act is naming what reaching the end looks like — a shipped surface, a decision locked, a
migration done. **The destination fixes the scope**, so everything else is judged against it: a
question past the destination is out of scope, not fog.

## Three buckets, and the test that sorts them

| Bucket | What it holds | Test |
|---|---|---|
| **Settled** | decisions made, with the answer | the user answered it |
| **Fog** (`## Not yet specified`) | in-scope questions you cannot yet phrase sharply | can you state the question precisely *now*? If no → fog |
| **Out of scope** | ruled beyond the destination | scope, not sharpness, lands it here |

The fog test is about the *question's* sharpness, never whether you can answer it — a sharp
question you cannot yet answer is settled work for pm, not fog. **Do not pre-slice fog** into
tidy pieces; one patch may graduate into several SCs or none.

## Judge the mission — patch or plan

The last act before writing is **your own judgement** of how much process the change deserves
(SC-01). It is `patch` when all three hold, and `plan` otherwise:

1. **The cause is known** — not suspected, not "probably in the parser"; the grilling can say why
   it happens.
2. **The diff is bounded** — the grilling can name the files. If you cannot list them, you do not
   know the diff.
3. **No new public interface, schema, or enforcement surface** — nothing another feature, a hook,
   or a gate script will read that did not exist before.

Write the verdict with a one-line reason and put it to the user as one question with your
recommendation attached, like any other frontier question. They confirm or override in the same
dialog; either way the artifact records what you judged and what they ruled, so the ledger can
show later whether the harness's judgement was right (SC-21). **Do not default to `plan` because
you are unsure** — an unsure judgement is a question with a recommendation, never the heavier
lane (SC-22). `/harness-plan` and `/harness-patch` refuse to start without this block.

## The artifact

Write `.harness/notes/grilling-<slug>-<date>.md`, and hand pm its **path** — never the transcript:

```markdown
# Grilling — <what this is about> — <date>

## Destination
<what reaching the end looks like; one or two lines>

## Mission
mission: patch | plan
reason: <one line — the harness's own judgement, from the three-part rule above>
confirmed-by: operator | overridden-by: operator (<one line>)

## Settled
- <question> → <the user's answer, verbatim in substance>

## Not yet specified
- <in-scope question not yet sharp enough to state — pm may sharpen it, or it waits>

## Out of scope
- <ruled out of this effort, and why>

## Facts I verified (so pm does not re-derive them)
- <claim — how I checked it — at <sha>>
```

Bounded, one screen or so. `## Destination` and `## Settled` are what BRIEF's perspectives are
authored from; `## Mission` is the lane pm writes for; `## Facts` is what saves pm a research
pass; the other two are what stop scope creep mid-build.

## Done, and what follows

Done when the frontier is empty — every branch visited, nothing silently assumed — and the user
confirms. Then:

- **Onboarding:** the answers seed `harness.json`, the domain description, and the first glossary
  terms.
- **A feature or a bug:** hand pm the artifact **path**, with the mission recorded and confirmed —
  `patch` goes to `/harness-patch`, `plan` to `/harness-plan`. pm still owns the perspectives and
  the SCs; you have removed the guesswork and judged the lane, not done its job.

## Red flags

| Thought | Reality |
|---|---|
| "I'll ask these four together to save time" | Only if they are genuinely independent — a numbered frontier round. Dependent questions still go one at a time |
| "They're all on the frontier, so I'll dump every open question" | A question on the frontier only because you never traced its dependency is not independent |
| "I'll ask the user which file holds X" | A fact. Go look. Only decisions are theirs |
| "The user is busy; pm can figure the rest out" | pm plans from what it is told, and guesses become perspectives nobody meant |
| "This is obviously in scope" | If it is past the destination it is out of scope. Say so and record it |
| "I'll write down the fog as tickets so it's actionable" | Fog is coarser than a task. Pre-slicing it invents structure the answer may delete |
| "I'm not sure it's a patch, so `plan` is the safe call" | Uncertainty asks one question with your recommendation. `plan` is not safe, it is expensive; defaulting to it is the process tax SC-22 exists to stop |
| "I'll skip the mission line; pm can decide the lane" | pm cannot start without it, and the judgement is yours to make in dialog. Record it, with the user's confirmation or override |
| "We're aligned, I'll start" | Only the user declares shared understanding reached |
