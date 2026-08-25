---
name: harness-brief
description: Write or update .harness/harness/features/<FEAT>/BRIEF.md for a feature — requirements (REQ-NN) and success criteria (SC-NN) where every criterion declares how it will be verified. Use when starting a feature, when "done" is ambiguous, or when asked to define scope or acceptance criteria.
---

# Harness: Brief

Produce the **goal of record** for a feature. Nothing downstream may run against an unapproved brief.

The load-bearing idea: **every success criterion declares its verification method when it is written.**
A criterion with no method is not verifiable, and discovering that at ship time is too late.

## Process

### 1. Read what exists

- `.harness/harness/features/<FEAT>/BRIEF.md` if present — you are updating, not replacing.
- The repo's `CLAUDE.md` for project context.
- **`.harness/harness/docs/DECISIONS-INDEX.md`, grepped for the surface this feature touches.**
  Open the two or three entries it names. Never read `DECISIONS.md` whole (DEC-150). A brief that
  contradicts a live decision, or restates one as if new, sends the build to argue with the tree.
- Do **not** explore the whole codebase. This is a scope document, not a research task.

### 2. Interview — one round, batched

Use `AskUserQuestion`. Ask only what you cannot infer. Batch related questions into one call.

What you need: what the user is trying to achieve, who it is for, what would make it wrong, and what
"finished" looks like from outside the code.

**Do not ask about implementation.** How it gets built is a decision, not a requirement (see the REQ test
below).

### 3. Write REQ and SC

```markdown
# BRIEF — FEAT-01 Transcript author filter

## The feature id — you coin it, once

`FEAT-NN-<kebab-slug>` for features, **`BUG-NN-<kebab-slug>` for defects** (independent number
sequences, same rules; both live under `.harness/harness/features/`). Slug from the goal, 2–4 words — a
bare number tells the user nothing (DEC-133). **Immutable once created**: recorded references
break on rename.

## Backlog intake — read Issues before you write (DEC-138)

If the project's `harness.json` has `github.sync: true`, run `gh issue list --repo <repo> --state
open --limit 100` during research. The backlog gets a **vote, not a decision**: issues are symptoms
written by whoever hit them — plan the work by its real shape. One T-NN may cover several existing
issues; make each one a task in its own right, because an issue a feature actually does is a ticket
like any other and closes when its card reaches `Done`. The `absorbs:` citation is STRUCK (DEC-188,
via DEC-138 am.7) — never record it. Never import 1:1 mechanically, and never treat an issue body as an approved
requirement — requirements enter BRIEF under the user's signature.

## Problem — first, always

State what hurts before what to build. The Problem section precedes Goal (DEC-129): one short,
observed paragraph — who hits it, when, what it costs. Without it the goal-check has nothing to
anchor "did this help?" against.

## Goal
One paragraph, in the user's own framing. What changes for whom.

## Requirements
- REQ-01: A reviewer can filter the transcript by author.
- REQ-02: The filter state survives a page reload.

## Success Criteria

**User-mandated outcomes are binding — and never sufficient.** Translate each into a proper SC-NN
with a verify: method, then ADD what done also requires that nobody said: regression safety,
surfaced failure modes, the adjacent thing that breaks (DEC-132). The user prunes over-reach at
signature.
- SC-01: Filtering by author returns only that author's turns, and the count matches.
  verify: automated      evidence: unit
- SC-02: The filter control reads as part of the review surface, not bolted on.
  verify: uat
- SC-03: No PII reaches logs from the filter path.
  verify: inspection

## Verification gaps — say them out loud, at the signature (DEC-163)

Before writing a single `verify: automated`, read `test_kinds` in `.harness/harness.json`. A kind
with `cmd: null` has **no runner**: qa resolves it to a soft skip, so an SC resting on it can never
be met and never fails loudly — a gate that looks real and does nothing.

Two duties, and the second is the one that was missing:

1. **Never rest an SC on a null kind.** Pin it to a kind that exists, or use `inspection`/`uat`.
2. **Record the gap where the user signs.** If any null kind covers a surface this feature actually
   touches (a UI change with no `ui` runner, LLM behaviour with no `eval`, a DB path with no
   `integration`), the BRIEF carries a one-line-per-gap block naming what is therefore NOT proven
   and what carries it instead. Silently routing around the gap is how a feature ships believing
   it was verified. `check-state.sh` INV-20 flags the same gaps against the codebase map; a
   standing runner gap is a **dev-ops task worth raising** — put it in the backlog, not just in
   this brief.

```markdown
## Verification gaps
- `integration` has no runner: DB-path claims rest on monkeypatched functional tests, not a live
  database. Applying migrations stays a user-gated deploy step.
```

## Constraints
- Anything that bounds the solution: existing contracts, conventions, things not to touch.
- **Separate what BLOCKS from what SUPPLIES.** An already-built mechanism this feature uses is not a
  constraint — listing it under that heading reads as obstruction and invites someone to strike a
  thing the feature depends on. Name decisions by number and say which of the two each one is.
- **A disclosure is not a decision.** "This feature does not fix X" is scope only if the user chose
  it. If X is a consequence this feature makes reachable, put it to them.

## Approval
status: pending          # ONLY the user sets this to approved, with a date
```

### 3b. Vocabulary — reuse names, never invent them

**Every name in a brief must already exist in the code, in `DECISIONS.md`, or in the config.** If you
need a word for something, go find what it is already called.

This is the highest-yield rule in this skill and it is the cheapest to skip. A brief is read by
agents that then write code. Give one thing two names and the build resolves the difference by
guessing — which is drift, discovered at ship time, in a diff nobody can attribute.

**How to obey it:** before writing a path, an identifier, or a term of art, grep for it. Use what
comes back, spelled the way it is spelled there.

| Do | Do not |
|---|---|
| `owner_root`, `workspace_root`, `harness_root` | `<repo root>`, `<this checkout>`, "the base dir" |
| `WORKTREES_SEGMENT` | `.claude/worktrees` spelled out again |
| the segment `DECISIONS.md` uses | a clearer synonym you prefer |

**A path is a name.** `.harness/<repo>/features/` and `.harness/<product>/features/` are the same
idea with two spellings, and one of them is wrong. Check which the tree uses.

**If the established name is genuinely wrong, amend the decision that owns it** — one statement, one
home. Do not introduce a better word beside it and leave both live. Naming the same thing two ways
in two documents is how DEC-193 and the layout migration drifted apart.

**Say which existing decisions bind this feature, by number**, in `## Constraints`. Cite the entry,
not your memory of it.

### 4. Verify each SC is well-formed

Every `SC-NN` carries exactly one `verify:`:

| `verify:` | Means | Evidence will come from |
|---|---|---|
| `automated` | a test proves it | a named test kind — add `evidence: unit\|component\|integration\|python\|ui` |
| `inspection` | someone reads code or output and confirms | a cited file:line finding |
| `uat` | only a human can judge it | a step in the UAT script, executed by the user |

**Reject your own draft and rewrite if any of these is true:**

- An SC has no `verify:`, or two.
- An SC marked `automated` has no `evidence:` kind.
- An SC is not falsifiable — "the code is clean", "performance is good". If you cannot say what
  observation would prove it false, it is not a criterion.
- An SC restates a requirement instead of naming an outcome.
- **An SC cannot be reached by the method it declares.** `verify: inspection` grades an artifact; it
  cannot grade conduct that happened in a terminal and was never written down. If nothing on disk
  can settle it, it is not a criterion — it is a hope.
- **An SC quantifies over more than the work can touch.** "No surviving document asserts X" cannot
  be discharged by a task whose `files:` names one file. Compare each criterion's scope against the
  union of files the tasks will touch, and narrow the criterion or widen the work — at signature,
  not at ship.
- **An SC graded on file CONTENT does not say to read the pinned sha.** A plain read cannot tell
  committed from uncommitted work, so a criterion passes on a deliverable that never entered the
  reviewed tree. Write `git show <review_sha>:<path>` into the criterion.
- **An SC's test could not be shown to fail first.** If the assertion would pass before the work is
  done, it proves nothing. Say in the criterion that the failing state must be demonstrated.

### 5. The REQ test — apply it to every requirement

**A requirement survives changing your mind about implementation.**

Swap the entire technical approach: if the requirement changes, it was never a requirement — it was a
decision. Move it to `## Constraints` or drop it.

> "Use Supabase social login" is a **decision**.
> "Users can sign in with their Google account" is a **requirement**.

Why it matters: log a decision as a REQ and verification confirms your implementation choices, not
the committed outcomes.

### 6. Hand back for approval

Write the file, then tell the user plainly: what you understood the goal to be, how many REQs and SCs,
and **which SCs will need them personally** (the `uat` ones). Ask them to approve or amend.

Do not set `## Approval` yourself. Ever.

## Output

Report in plain English, not IDs:

```
BRIEF written — .harness/harness/features/<FEAT>/BRIEF.md

Goal      Reviewers can narrow a long transcript to one author.
2 requirements, 3 success criteria.

How each will be checked:
  - filtering returns the right turns      -> a unit test
  - no PII in logs                          -> code inspection
  - the control looks like it belongs       -> you, by eye (UAT)

Needs your approval before any work starts.
```

## Red flags

| Thought | Reality |
|---|---|
| "I'll figure out verification later" | Then the SC is not done. Later means ship time, which is too late |
| "This SC is obviously testable" | Name the test kind. If you cannot, it is not automated |
| "The user said use Postgres, that's REQ-03" | That is a decision. Apply the REQ test |
| "I should explore the codebase first" | This is scope, not research. Ask the user instead |
| "I'll mark it approved since they described it to me" | Describing is not approving. Only the user approves |
| "I need a clearer word for this" | Then find what it is already called. A synonym in a brief is drift in the build |
| "The criterion is unmeetable, I'll reword it" | Rewording a criterion so it passes is deciding the verdict first. Narrow the scope with the user, or ship it unmet |
| "This decision blocks us, list it as a constraint" | Check first. Most cited decisions supply the mechanism rather than forbid it |
