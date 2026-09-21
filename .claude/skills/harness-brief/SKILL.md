---
name: harness-brief
description: Write or update .harness/harness/features/<FEAT>/BRIEF.md for a feature — done stated by perspective, and success criteria (SC-NN) that each discharge one perspective and declare how they will be verified. Use when starting a feature, when "done" is ambiguous, or when asked to define scope or acceptance criteria.
---

# Harness: Brief

Produce the **goal of record** for a feature. Nothing downstream may run against an unapproved brief.

- Instantiate from `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/templates/BRIEF.md`; its
  sections appear in that order and no others.
- **Done is stated once, by the people who will judge it** — `## Done when — by perspective`,
  which the goal-check grades and the handoff cites (DEC-231).
- There is no `## Goal` and no `## Requirements`.
- **Every success criterion declares its verification method when it is written.**

## Process

### 1. Read what exists

- `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/BRIEF.md` if present — you are updating, not replacing.
- **The grilling artifact** whose path you were handed. `## Destination` and `## Settled` are what
  the perspectives are authored from; `## Mission` names the lane (step 7); `## Facts I verified`
  saves you a research pass. Never re-ask what it settled.
- The repo's `CLAUDE.md` for project context.
- **`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness/docs/DECISIONS-INDEX.md`, grepped for the surface this feature touches.**
  Open the two or three entries it names; never read `DECISIONS.md` whole (DEC-150). A brief that
  contradicts a live decision sends the build to argue with the tree.
- **Backlog intake**, when `harness.json` has `github.sync: true`: read
  `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/backlog-intake.md` before any
  perspective is written. The backlog gets a **vote, not a decision** (DEC-138); an issue body is
  never an approved perspective.
- Do **not** explore the whole codebase. This is scope, not research.

### 2. Interview — one round, batched, perspectives first

Use `AskUserQuestion`. Ask only what the grilling artifact does not settle, batched into one call.
In this order: **who will judge the result** (the perspectives), what each can rely on once it
ships, what would make it wrong for them, and what "finished" looks like from outside the code.

**Do not ask about implementation** — how it gets built is a decision, not a perspective (step 5).

**Uncertain? Ask one question with your recommendation** (DEC-230). Never resolve doubt by adding
process — a heavier lane, a broader criterion, a hedge perspective.

### 3. Write the perspectives, then the SCs

## The feature id — you coin it, once

`FEAT-NN-<kebab-slug>` for features, **`BUG-NN-<kebab-slug>` for defects** (independent number
sequences, same rules, same root `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/`). Slug
from the destination, 2–4 words — a bare number tells the user nothing (DEC-133). **Immutable once
created**: recorded references break on rename.

## Problem — first, always

State what hurts before what to build (DEC-129): one short, observed paragraph — who hits it, when,
what it costs. The goal-check anchors "did this help?" on it.

## Done when — by perspective

One block, and the only statement of done. Each line is a person who will judge the result,
speaking in the first person about what they can rely on once it ships: `**<name>** — <1–3
sentences>`. The standard names — `operator`, `code maintainer`, `end user`, `reader`,
`orchestrator` — spelled exactly so; the template says who each one is. Add a project-specific
name only when none fits.

**A perspective with nothing to say is omitted** — never written as "none"; INV-38 demands an SC
for it. A trailing parenthetical is a gloss, not part of the name: `**reader (reviewer / qa)**`
declares `reader`, and the SC tag is `(reader)`.

## Success criteria — each one discharges a perspective

**SCs derive from the perspectives, never the other way round.** A perspective no SC discharges is
an unverified promise; an SC that discharges no perspective is scope creep. `check-state.py`
INV-38 refuses both at write.

**User-mandated outcomes are binding — and never sufficient.** Translate each into a proper SC-NN
with a `verify:` method, then ADD what done also requires that nobody said: regression safety,
surfaced failure modes, the adjacent thing that breaks (DEC-132). The user prunes over-reach at
signature.

## Verification gaps — say them out loud, at the signature (DEC-163)

Before writing a single `verify: automated`, read `test_kinds` in `<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json`. A kind
with `cmd: null` has **no runner**: qa soft-skips it, so an SC resting on it is never met and
never fails loudly.

1. **Never rest an SC on a null kind.** Pin it to a kind that exists, or use `inspection`/`uat`.
2. **Record the gap where the user signs.** If a null kind covers a surface this feature touches,
   the BRIEF names, one line per gap, what is therefore NOT proven and what carries it instead. A
   standing runner gap is a **dev-ops task worth raising** — backlog it too (DEC-163).

## Constraints

- Anything that bounds the solution: existing contracts, conventions, things not to touch.
- **Separate what BLOCKS from what SUPPLIES.** A mechanism this feature uses is not a constraint —
  listed as one, it invites someone to strike it. Name decisions by number and say which of the
  two each one is.
- **A disclosure is not a decision.** "This feature does not fix X" is scope only if the user chose
  it. If X is a consequence this feature makes reachable, put it to them.

## Out of scope

Copy the grilling artifact's `## Out of scope`, reasons included; do not re-litigate it.

## Approval

`status: pending` — ONLY the user sets this to approved, with a date.

### 3b. Vocabulary — reuse names, never invent them

**Every name in a brief must already exist in the code, in `DECISIONS.md`, or in the config.** If you
need a word for something, find what it is already called. Two names for one thing is drift the
build resolves by guessing (DEC-193).

**How to obey it:** before writing a path, an identifier, or a term of art, grep for it and use
the spelling that comes back — `owner_root`, not "the base dir"; the segment `DECISIONS.md` uses,
not a clearer synonym. **A path is a name**: check which spelling the tree uses before writing one.

**If the established name is genuinely wrong, amend the decision that owns it** — one statement, one
home. Never introduce a better word beside it and leave both live.

**Say which existing decisions bind this feature, by number**, in `## Constraints`. Cite the entry,
not your memory of it.

### 4. Verify each SC is well-formed

Every `SC-NN` carries exactly one perspective tag and exactly one `verify:` — `automated` with an
`evidence: <test kind>` (qa requires the failing state first), `inspection` (a cited file and
symbol), or `uat` (a step the user executes).

**Reject your own draft and rewrite if any of these is true:**

- An SC has no perspective tag, its tag names a perspective the block does not declare, or a
  declared perspective has no SC. Write `- SC-NN (<perspective>): ...`; INV-38 refuses the rest.
- An SC has no `verify:`, or two; or is `automated` with no `evidence:` kind.
- An SC is not falsifiable — "the code is clean", "performance is good". If you cannot say what
  observation would prove it false, it is not a criterion.
- An SC restates its perspective instead of naming an outcome.
- **An SC cannot be reached by the method it declares.** `verify: inspection` grades an artifact,
  not conduct that happened in a terminal. If nothing on disk can settle it, it is a hope.
- **An SC quantifies over more than the work can touch.** "No surviving document asserts X" cannot
  be discharged by a task whose `files:` names one file. Narrow the criterion or widen the work —
  at signature.
- **An SC asserts repository-wide state.** A `verify:` running `check-state.py` or
  `check-domain.py` with no feature-scoped argument grades the whole tree, and other features'
  debris turns it red (DEC-231). Repository hygiene is a merge-time check; INV-41 refuses it.
- **An SC graded on file CONTENT does not say to read the pinned sha.** A plain read cannot tell
  committed from uncommitted work. Write `git show <review_sha>:<path>` into the criterion.
- **An SC's test could not be shown to fail first.** If the assertion would pass before the work is
  done, it proves nothing. Say in the criterion that the failing state must be demonstrated.

### 5. The perspective test — apply it to every perspective line

**A perspective statement survives changing your mind about implementation.** Swap the entire
technical approach: if the statement changes, it was a decision, never a perspective. Move it to
`## Constraints` or drop it.

> "Sign-in goes through Supabase social login" is a **decision**.
> "**end user** — I can sign in with my Google account" is a **perspective**.

Logged as a perspective, a decision makes the goal-check confirm your choices, not the promises.

### 6. Hand back for approval

Write the file, then report in plain English, not IDs: the BRIEF path; who judges done and what
each was promised; how many SCs and how each will be checked ("a unit test", "you, by eye"); and
**which SCs will need them personally** (the `uat` ones). Ask them to approve or amend.

### 7. The patch lane — one intake run

When the grilling artifact's `## Mission` reads `patch`, the whole intake is ONE product run: a
BRIEF of at most 120 lines and a one-task `plan.yaml`, no panel, no goal-check (DEC-225). Read
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/patch-lane.md` at that moment,
before writing either. A patch whose brief needs more than 120 lines, or whose diff turns out
unbounded, is a `plan` mission wearing the wrong label: return it with the reason, never trim.

## Red flags

| Thought | Reality |
|---|---|
| "I'll figure out verification later" | Then the SC is not done. Later means ship time |
| "The user said use Postgres, that's the maintainer's perspective" | That is a decision. Apply the perspective test |
| "I'll write `**end user** — none` to be thorough" | Omitted, never "none". Written down, INV-38 demands an SC for it |
| "This SC is important but no perspective claims it" | Then it is scope creep. A perspective wants it — say which — or it goes |
| "I should explore the codebase first" | This is scope, not research. Ask the user instead |
| "I'll mark it approved since they described it to me" | Describing is not approving. Only the user approves |
| "This decision blocks us, list it as a constraint" | Check first. Most cited decisions supply the mechanism rather than forbid it |
| "I'm not sure this is a patch; I'll write the full plan to be safe" | Ask one question with your recommendation. The heavier lane is the expensive default, not the safe one |
