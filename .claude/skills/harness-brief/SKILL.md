---
name: harness-brief
description: Write or update .harness/features/<FEAT>/BRIEF.md for a feature — requirements (REQ-NN) and success criteria (SC-NN) where every criterion declares how it will be verified. Use when starting a feature, when "done" is ambiguous, or when asked to define scope or acceptance criteria.
---

# Harness: Brief

Produce the **goal of record** for a feature. Nothing downstream may run against an unapproved brief.

The load-bearing idea: **every success criterion declares its verification method when it is written.**
A criterion with no method is not verifiable, and discovering that at ship time is too late.

## Process

### 1. Read what exists

- `.harness/features/<FEAT>/BRIEF.md` if present — you are updating, not replacing.
- The repo's `CLAUDE.md` for project context.
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
sequences, same rules; both live under `.harness/features/`). Slug from the goal, 2–4 words — a
bare number tells the user nothing (DEC-133). **Immutable once created**: recorded references
break on rename.

## Backlog intake — read Issues before you write (DEC-138)

If the project's `harness.json` has `github.sync: true`, run `gh issue list --repo <repo> --state
open --limit 100` during research. The backlog gets a **vote, not a decision**: issues are symptoms
written by whoever hit them — plan the work by its real shape. One T-NN may cover several existing
issues; record `absorbs: #12, #14` on the task so they close with it and every watcher sees where
their item went. Never import 1:1 mechanically, and never treat an issue body as an approved
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

## Approval
status: pending          # ONLY the user sets this to approved, with a date
```

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
BRIEF written — .harness/features/<FEAT>/BRIEF.md

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
