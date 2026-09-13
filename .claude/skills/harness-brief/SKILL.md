---
name: harness-brief
description: Write or update .harness/harness/features/<FEAT>/BRIEF.md for a feature — done stated by perspective, and success criteria (SC-NN) that each discharge one perspective and declare how they will be verified. Use when starting a feature, when "done" is ambiguous, or when asked to define scope or acceptance criteria.
---

# Harness: Brief

Produce the **goal of record** for a feature. Nothing downstream may run against an unapproved brief.

Two load-bearing ideas:

- **Done is stated once, by the people who will judge it.** `## Done when — by perspective` is the
  one statement of done for the feature; the goal-check grades it and the handoff cites it (FEAT-59
  SC-10, SC-11). There is no `## Goal` and no `## Requirements`.
- **Every success criterion declares its verification method when it is written.** A criterion
  with no method is not verifiable, and discovering that at ship time is too late.

## Process

### 1. Read what exists

- `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/BRIEF.md` if present — you are updating, not replacing.
- **The grilling artifact** whose path you were handed. `## Destination` and `## Settled` are what
  the perspectives are authored from; `## Mission` says which lane you are writing for (section 7);
  `## Facts I verified` saves you a research pass. Never re-ask what it settled.
- The repo's `CLAUDE.md` for project context.
- **`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness/docs/DECISIONS-INDEX.md`, grepped for the surface this feature touches.**
  Open the two or three entries it names. Never read `DECISIONS.md` whole (DEC-150). A brief that
  contradicts a live decision, or restates one as if new, sends the build to argue with the tree.
- Do **not** explore the whole codebase. This is a scope document, not a research task.

### 2. Interview — one round, batched, perspectives first

Use `AskUserQuestion`. Ask only what the grilling artifact does not settle. Batch related questions
into one call.

What you need, in this order: **who will judge the result** (the perspectives), what each of them
can rely on once it ships, what would make it wrong for them, and what "finished" looks like from
outside the code. The perspectives come first because the SCs derive from them — you cannot write
a criterion until you know whose promise it discharges.

**Do not ask about implementation.** How it gets built is a decision, not a perspective (see the
perspective test below).

**Uncertain? Ask one question with your recommendation** (SC-22). Never resolve doubt by adding
process — a heavier lane, a broader criterion, a hedge perspective. State what you would do and
why, and let the user pick.

### 3. Write the perspectives, then the SCs

## The feature id — you coin it, once

`FEAT-NN-<kebab-slug>` for features, **`BUG-NN-<kebab-slug>` for defects** (independent number
sequences, same rules; both live under `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/`). Slug from the destination, 2–4 words — a
bare number tells the user nothing (DEC-133). **Immutable once created**: recorded references
break on rename.

## Backlog intake — read Issues before you write (DEC-138)

If the project's `harness.json` has `github.sync: true`, run `gh issue list --repo <repo> --state
open --limit 100` during research. The backlog gets a **vote, not a decision**: issues are symptoms
written by whoever hit them — plan the work by its real shape. One T-NN may cover several existing
issues; make each one a task in its own right, because an issue a feature actually does is a ticket
like any other and closes when its card reaches `Done`. The `absorbs:` citation is STRUCK (DEC-188,
via DEC-138) — never record it. Never import 1:1 mechanically, and never treat an issue body as an
approved perspective — done enters BRIEF under the user's signature.

## Problem — first, always

State what hurts before what to build. The Problem section opens the brief (DEC-129): one short,
observed paragraph — who hits it, when, what it costs. Without it the goal-check has nothing to
anchor "did this help?" against.

## Done when — by perspective

One block, and the only statement of done. Each line is a person who will judge the result,
speaking in the first person about what they can rely on once it ships: `**<name>** — <1–3
sentences>`. The standard names, spelled exactly so:

| Name | Who |
|---|---|
| `operator` | signs, rules on rework, audits the record afterwards |
| `code maintainer` | reads, changes or extends the code six months from now |
| `end user` | the person the surface is for |
| `reader` | a reviewer, qa, or panel member grading the result |
| `orchestrator` | dispatches the phases and inherits the spend |

Add a project-specific name only when none of these fits. **A perspective with nothing to say is
omitted** — never written as "none"; an empty promise is still a promise the goal-check has to
grade. A trailing parenthetical is a gloss, not part of the name: `**reader (reviewer / qa)**`
declares `reader`, and the SC tag is `(reader)`.

```markdown
**operator** — I trust the harness to judge how much process a change deserves, and I verify that
trust after the fact from a record that states each judgement and its reason in one line.

**code maintainer** — One statement of "done" per feature, in one place, which the goal-check
grades and the handoff cites.
```

## Success criteria — each one discharges a perspective

**SCs derive from the perspectives, never the other way round.** A perspective no SC discharges is
an unverified promise; an SC that discharges no perspective is scope creep. `check-state.sh`
INV-38 refuses both, at write, on any BRIEF carrying the by-perspective heading.

**User-mandated outcomes are binding — and never sufficient.** Translate each into a proper SC-NN
with a `verify:` method, then ADD what done also requires that nobody said: regression safety,
surfaced failure modes, the adjacent thing that breaks (DEC-132). The user prunes over-reach at
signature.

```markdown
- SC-01 (operator): every autonomous judgement is appended to feature.json judgements[] with a
  one-line reason.
  verify: automated      evidence: python
- SC-02 (code maintainer): the handoff ## Done when cites a brief-perspective: authority.
  verify: automated      evidence: unit
- SC-03 (end user): the filter control reads as part of the review surface, not bolted on.
  verify: uat
```

Plan tasks `traces:` cite these SC ids. The plan `scope` reader hunts **orphan SCs** — a criterion
no task traces to — and a task tracing to an SC that does not exist (SC-12); an orphan is a
`substance` finding, because a criterion nothing builds toward is a promise nothing will keep.

## Verification gaps — say them out loud, at the signature (DEC-163)

Before writing a single `verify: automated`, read `test_kinds` in `<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json`. A kind
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

## Out of scope

What the grilling ruled beyond the destination, with the reason. Copy it from the artifact's
`## Out of scope`; do not re-litigate it.

## Approval

`status: pending` — ONLY the user sets this to approved, with a date.

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
| `WORKTREES_SEGMENT` | `<HARNESS_CONTROL_PLANE_ROOT>/.claude/worktrees` spelled out again |
| the segment `DECISIONS.md` uses | a clearer synonym you prefer |

**A path is a name.** `<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/` and `<HARNESS_FEATURE_TREE_ROOT>/.harness/<product>/features/` are the same
idea with two spellings, and one of them is wrong. Check which the tree uses.

**If the established name is genuinely wrong, amend the decision that owns it** — one statement, one
home. Do not introduce a better word beside it and leave both live. Naming the same thing two ways
in two documents is how DEC-193 and the layout migration drifted apart.

**Say which existing decisions bind this feature, by number**, in `## Constraints`. Cite the entry,
not your memory of it.

### 4. Verify each SC is well-formed

Every `SC-NN` carries exactly one perspective tag and exactly one `verify:`:

| `verify:` | Means | Evidence will come from |
|---|---|---|
| `automated` | a test proves it | a named test kind — add `evidence: unit\|component\|integration\|python\|ui`; qa requires the test's failing state before the fix (`fail_first`) |
| `inspection` | someone reads code or output and confirms | a cited file and symbol |
| `uat` | only a human can judge it | a step in the UAT script, executed by the user |

**Reject your own draft and rewrite if any of these is true:**

- An SC has no perspective tag, or its tag names a perspective the block does not declare. Write
  it `- SC-NN (<perspective>): ...`; INV-38 refuses anything else.
- A declared perspective has no SC tagged with it. Either write the criterion or delete the
  perspective — a promise nothing grades is not done.
- An SC has no `verify:`, or two.
- An SC marked `automated` has no `evidence:` kind.
- An SC is not falsifiable — "the code is clean", "performance is good". If you cannot say what
  observation would prove it false, it is not a criterion.
- An SC restates its perspective instead of naming an outcome.
- **An SC cannot be reached by the method it declares.** `verify: inspection` grades an artifact; it
  cannot grade conduct that happened in a terminal and was never written down. If nothing on disk
  can settle it, it is not a criterion — it is a hope.
- **An SC quantifies over more than the work can touch.** "No surviving document asserts X" cannot
  be discharged by a task whose `files:` names one file. Compare each criterion's scope against the
  union of files the tasks will touch, and narrow the criterion or widen the work — at signature,
  not at ship.
- **An SC asserts repository-wide state** (SC-16). A `verify:` that runs `check-state.sh` or
  `check-domain.sh` with no feature-scoped argument (`--feature`, the feature directory, or the
  feature id) grades the whole tree, and other features' debris turns it red — FEAT-54 lost three
  of six review cycles to exactly that. Repository hygiene is a merge-time check, not a feature
  criterion; INV-41 refuses it at write.
- **An SC graded on file CONTENT does not say to read the pinned sha.** A plain read cannot tell
  committed from uncommitted work, so a criterion passes on a deliverable that never entered the
  reviewed tree. Write `git show <review_sha>:<path>` into the criterion.
- **An SC's test could not be shown to fail first.** If the assertion would pass before the work is
  done, it proves nothing. Say in the criterion that the failing state must be demonstrated.

### 5. The perspective test — apply it to every perspective line

**A perspective statement survives changing your mind about implementation.**

Swap the entire technical approach: if the statement changes, it was never a perspective — it was a
decision. Move it to `## Constraints` or drop it.

> "Sign-in goes through Supabase social login" is a **decision**.
> "**end user** — I can sign in with my Google account" is a **perspective**.

Why it matters: log a decision as a perspective and the goal-check confirms your implementation
choices, not the outcomes the people judging the result committed to.

### 6. Hand back for approval

Write the file, then tell the user plainly: who judges done and what each of them was promised,
how many SCs, and **which SCs will need them personally** (the `uat` ones). Ask them to approve or
amend.

Do not set `## Approval` yourself. Ever.

### 7. The patch lane — one intake run

When the grilling artifact's `## Mission` reads `patch`, the whole intake is ONE product run and
you write both artifacts in it:

- **The BRIEF, in at most 120 lines**, same shape, no section skipped: Problem; the perspectives
  that actually judge a bug fix (usually `end user` or `operator`, plus `code maintainer` for the
  regression test); SCs that discharge them — the failing-then-passing test is the natural
  `automated` one; Verification gaps; Constraints; Out of scope; Approval pending. The bound is
  the point: a patch whose brief needs more than 120 lines was mis-judged, and you say so rather
  than trim.
- **`plan.yaml` with exactly one task**, `T-01`: `execution_mode: team`, `execution_agent` the
  owning dev, `files:` the ones the grilling named, `traces:` every SC, `change_type: bugfix`
  unless the grilling says otherwise. The lane itself is not yours to record: `feature.json` is
  the orchestrator's domain, and it wrote `mission: patch` from the grilling's `## Mission` block
  before it dispatched you (playbook step 1).

No panel and no goal-check run read the patch intake; it is gated at qa and review on the diff,
not at plan on a document (DEC-139 as amended by FEAT-59). After signature the orchestrator runs
build → validate → ship. If, while writing, the diff turns out unbounded or a new public interface
appears, that is a `plan` mission wearing the wrong label: return it with the reason instead of
writing a 120-line plan.

## Output

Report in plain English, not IDs:

```
BRIEF written — <HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/BRIEF.md

Done when, by perspective:
  operator          I can audit every judgement from a one-line record.
  code maintainer   One statement of done, cited by the handoff.
  end user          I can narrow a long transcript to one author.

3 perspectives, 4 success criteria, each tagged to one of them.

How each will be checked:
  - judgements land in the ledger             -> a python test
  - the handoff cites the perspective block   -> a unit test
  - filtering returns the right turns         -> a unit test
  - the control looks like it belongs         -> you, by eye (UAT)

Needs your approval before any work starts.
```

## Red flags

| Thought | Reality |
|---|---|
| "I'll figure out verification later" | Then the SC is not done. Later means ship time, which is too late |
| "This SC is obviously testable" | Name the test kind. If you cannot, it is not automated |
| "The user said use Postgres, that's the maintainer's perspective" | That is a decision. Apply the perspective test |
| "I'll write `**end user** — none` to be thorough" | A perspective with nothing to say is omitted. Written down, it is a promise INV-38 will demand an SC for |
| "This SC is important but no perspective claims it" | Then it is scope creep. Either a perspective wants it — say which — or it goes |
| "I should explore the codebase first" | This is scope, not research. Ask the user instead |
| "I'll mark it approved since they described it to me" | Describing is not approving. Only the user approves |
| "I need a clearer word for this" | Then find what it is already called. A synonym in a brief is drift in the build |
| "The criterion is unmeetable, I'll reword it" | Rewording a criterion so it passes is deciding the verdict first. Narrow the scope with the user, or ship it unmet |
| "This decision blocks us, list it as a constraint" | Check first. Most cited decisions supply the mechanism rather than forbid it |
| "`check-state.sh` exits 0 is the cleanest SC" | It grades every feature in the tree. Scope it to this one or it is a merge-time check, not a criterion |
| "I'm not sure this is a patch; I'll write the full plan to be safe" | Ask one question with your recommendation. The heavier lane is not the safe default; it is the expensive one |
