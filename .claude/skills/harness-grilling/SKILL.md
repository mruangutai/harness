---
name: harness-grilling
description: Dialog to clarity before anything is built — a relentless one-question-at-a-time interview that names the destination, settles the decision tree, and records fog and out-of-scope. Blocking step zero of /harness-plan and of onboarding. Run by the main session only.
---

# Grilling — reach shared understanding before the org spends a spawn

**Only the main session runs this.** It is the sole tier with a user channel (DEC-120), so a
subagent cannot grill anyone — and an agent that answers its own questions has broken the
discipline entirely. Adapted from Matt Pocock's `grilling`, `batch-grill-me` (the frontier round)
and `wayfinder` (MIT), re-homed onto harness machinery (DEC-164/167).

Why it is blocking: pm plans from what it is told. Every unstated assumption at this moment
becomes a REQ nobody meant, an SC that cannot be verified, or a build cycle spent discovering the
question. **Five kaya premises briefed as fact were FALSE at HEAD** on one feature — the cheapest
possible moment to find that is here, in conversation, before a spawn.

## The discipline

- **One question at a time by default**, with your recommended answer attached — several *dependent*
  questions at once is bewildering and gets you the first answer plus noise. Wait for each.
- **Except: batch a genuinely independent round.** Hold the decision tree in mind; its **frontier**
  is every question whose prerequisites are already settled. Those do not depend on each other, so
  asking them as one numbered round — each with a recommendation — is faster and no less rigorous,
  and the user's answers then push the frontier outward for the next round (DEC-167). A question
  whose answer hangs on another still-open question belongs to a *later* round, never this one.
  When in doubt, or when a question needs real exploration, go back to one at a time.
- **Facts are YOURS to find; decisions are the user's.** If the filesystem, git, the codebase map,
  or a command can answer it, go look — never ask the user something you could check. Dispatch an
  `Explore` subagent for anything broad. Then put the *decision* to them and wait.
- **Walk the decision tree, dependencies first.** A question whose answer depends on an open
  question belongs later. Settle the parent, then ask what it unblocks.
- **Challenge the language as you go** — a term that conflicts with `.harness/codebase/glossary.md`
  gets called out here, not after it lands in a REQ (`harness-spec-driven`'s glossary rules).
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
tidy pieces; one patch may graduate into several REQs or none.

## The artifact

Write `.harness/notes/grilling-<slug>-<date>.md`, and hand pm its **path** — never the transcript:

```markdown
# Grilling — <what this is about> — <date>

## Destination
<what reaching the end looks like; one or two lines>

## Settled
- <question> → <the user's answer, verbatim in substance>

## Not yet specified
- <in-scope question not yet sharp enough to state — pm may sharpen it, or it waits>

## Out of scope
- <ruled out of this effort, and why>

## Facts I verified (so pm does not re-derive them)
- <claim — how I checked it — at <sha>>
```

Bounded, one screen or so. `## Settled` is what BRIEF's REQs are authored from; `## Facts` is what
saves pm a research pass; the other two are what stop scope creep mid-build.

## Done, and what follows

Done when the frontier is empty — every branch visited, nothing silently assumed — and the user
confirms. Then:

- **Onboarding:** the answers seed `harness.json`, the domain description, and the first glossary
  terms.
- **A feature:** hand the artifact path to pm as a BRIEF input. pm still owns REQs and SCs; you have
  removed the guesswork, not done its job.

## Red flags

| Thought | Reality |
|---|---|
| "I'll ask these four together to save time" | Only if they are genuinely independent — a numbered frontier round. Dependent questions still go one at a time |
| "They're all on the frontier, so I'll dump every open question" | A question on the frontier only because you never traced its dependency is not independent |
| "I'll ask the user which file holds X" | A fact. Go look. Only decisions are theirs |
| "The user is busy; pm can figure the rest out" | pm plans from what it is told, and guesses become REQs nobody meant |
| "This is obviously in scope" | If it is past the destination it is out of scope. Say so and record it |
| "I'll write down the fog as tickets so it's actionable" | Fog is coarser than a task. Pre-slicing it invents structure the answer may delete |
| "We're aligned, I'll start" | Only the user declares shared understanding reached |
