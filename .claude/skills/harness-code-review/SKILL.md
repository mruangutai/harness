---
name: harness-code-review
description: Two-stage review protocol — spec compliance must pass before code quality is examined, findings need concrete failure scenarios, and only substantive issues gate. Loaded by harness-code-reviewer.
user-invocable: false
---

# Code Review Protocol

Read-only. You return findings; you never fix them.

Two stages, **in order**. Stage 1 must complete before Stage 2 begins, and the stages do not mix.

## Why this order

Code that is beautiful and builds the wrong thing is a more expensive failure than code that is ugly and
builds the right thing. Finding it second means the entire quality pass was wasted effort.

## Stage 1 — spec compliance

Read `.harness/features/<FEAT>/BRIEF.md` and `PLAN.md ## Decisions`, then the diff. Ask four questions:

1. Does every change serve a documented `REQ-NN` or `D-NN`?
2. Is anything here that **no** requirement asked for? *(scope creep — a finding even when it is an
   improvement)*
3. Is any requirement or decision **missing** a corresponding change? *(omission)*
4. Do the details match the specific values and constraints that were decided — not just the intent?

Also verify any `SC-NN` marked `verify: inspection`. **This is where those are checked**, and each needs
a `file:line` citation.

Report per violation: the path, the `REQ`/`D` it relates to, and which of the three kinds it is.

## Stage 2 — code quality

Only after Stage 1. Judge against the conventions **already in this codebase**, not an abstract ideal.

Look for: correctness bugs · unhandled errors · **silent failure paths** · missing input validation ·
dropped async rejections · boundary and off-by-one conditions · resource leaks · dead code left behind ·
copy-paste divergence · comments that no longer match the code.

**Fail-open is the highest-value pattern to hunt.** Measured in this project's history: a dangling
reference that resolved to "valid" instead of blocking, a filter that returned a fabricated result on a
partial match. Both passed their test suites. Ask of every branch: *when this lookup misses, does it
block or does it sail through?*

Do **not** report what a linter catches, and do not restyle to personal preference.

## Findings need failure scenarios

Every finding states **specific inputs or state → specific wrong outcome.**

> `filter.ts:31` — if the author-list fetch rejects, the handler swallows it and renders an empty
> control, so a network blip is indistinguishable from "this document has no authors."

"This could be fragile" is not a finding. If you cannot say how it breaks, drop it.

## What gates, and what does not

| Severity | Meaning |
|---|---|
| `critical` | data loss, security hole, or certain breakage |
| `high` | wrong behaviour in a realistic case |
| `med` | wrong behaviour in an unlikely case, or real maintainability cost |
| `low` / `info` | worth knowing, not worth blocking |

- `must_fix` non-empty **or** `severity_max >= high` → **`FAIL`**
- otherwise → **`PASS` with notes** — logged and surfaced, does not block

**Style and opinion never gate.** This exists to prevent the trap where one permanent nit loops to
`max_cycles` and nothing ever ships.

## Review a pinned SHA

Diff `base..review_sha` from `.harness/features/<FEAT>/review_sha` — **never `..HEAD`**. A commit landing
mid-review must not change what you reviewed.

Check for `[harness:human]` commits since the last pin: those are hand edits that **inherit no earlier
review**, and their paths are in scope for you now.

## Red flags

| Thought | Reality |
|---|---|
| "Quality first, I'll check the spec after" | Wrong order. Wrong-thing-built-well is the costlier failure |
| "This is ugly — must_fix" | Style never gates. `must_fix` means broken |
| "I found 30 things" | Rank them. An unread list gates nothing |
| "It probably handles that case" | Read the branch. "Probably" is how fail-open ships |
| "The tests pass, so it's correct" | Tests prove what was tested. Both measured fail-opens passed theirs |
| "I'll fix this small one myself" | You are read-only. Report it |
