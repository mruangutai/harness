---
name: harness-uat
description: Generate and gate on a user acceptance test — turn every `verify: uat` success criterion into a hand-test script the user executes, and block the ship decision on their result. Use before shipping or merging a user-facing change, or when asked whether something is ready to ship.
---

# Harness: UAT

Turn the success criteria that **only a human can judge** into a short script the user actually runs, and
block shipping until they do.

The last gate, and the only one that is not an agent's opinion.

## Process

### 1. Collect the criteria that need a human

Read `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/BRIEF.md`. Take every `SC-NN` with `verify: uat`.

**If there are none, say so and stop.** A change with no human-judgeable criteria needs no UAT — do not
manufacture one. That is a legitimate and common outcome for backend-only work.

### 2. Confirm the prerequisites are already green

A UAT is only `ready` when every `automated` and `inspection` criterion has already passed.

Check `harness-qa` and `harness-code-reviewer` verdicts through their canonical skills. If either
is `FAIL`, report `draft — not ready` with the failing prerequisite and fix it before hand-off.

**Never hand a user a UAT for a change whose tests fail.** Their time is the most expensive input in the
system; spending it on a known-broken build wastes it.

### 3. Write the script

```markdown
# UAT — FEAT-01 Transcript author filter
status: ready              # draft | ready | passed | failed
branch: harness/author-filter
review_sha: def5678

## Setup
`pnpm -C web dev` — then open http://localhost:3003/review

## Steps
- U-01 (SC-02): Open a transcript with several authors and filter to one.
  expect: only that author's turns remain.
  result:

- U-02 (SC-02): Compare the filter control with adjacent review controls.
  expect: its styling matches the review surface.
  result:

- U-03 (SC-05): Clear the filter.
  expect: every original turn is visible again.
  result:

- U-04 (SC-05): Compare the restored transcript with its pre-filter sequence.
  expect: turn order matches the original sequence.
  result:
```

Rules for steps:

- **One observable outcome per step.** If `expect:` has two clauses joined by "and" that could fail
  independently, split it.
- **Say what to look at, not what to conclude.** "The count in the header matches the visible turns", not
  "verify it works correctly".
- **Concrete setup.** The real command and the real URL for this repo. If you do not know how to start
  it, find out — a UAT the user cannot run is worthless.
- **Keep it short.** Every step costs the user's attention. If the script exceeds ~5 steps, the criteria
  are probably too vague; go back to the BRIEF.
- **Include the failure you most suspect.** If something feels fragile, make it a step.

Write to `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/notes/uat.md`. Committed, so what was accepted and when is on the record.

### 4. Hand it over

Present it in plain English with a time estimate. Then stop and wait — do not proceed to ship.

### 5. Record the result

The **user** sets `passed` or `failed`. You never do.

| Result | Action |
|---|---|
| `passed` | Record it, mark the SCs met with the UAT as evidence, and report ready to ship |
| `failed` | **This is a `FAIL`, not a discussion.** Capture their `result:` text verbatim, and route it back as work: which SC failed, what they observed, which paths are implicated |

A failed UAT consumes a fix cycle. Do not argue with the result or reinterpret it — the user's judgment
*is* the criterion for a `verify: uat` SC.

## Output

Report the script path, step count, estimated time and observed prerequisite evidence. Point the
user to the concrete actions in the script, identify the UAT SCs, and say shipping waits for
their result. Do not duplicate the script or invent green test counts.

## Red flags

| Thought | Reality |
|---|---|
| "There are no uat criteria, I'll write some anyway" | Then you invented a gate. Say there is no UAT and move on |
| "Tests are failing but they can still eyeball it" | Never. Fix the tests first; their time is the scarcest input |
| "I'll mark it passed since it looked right in the screenshot" | Only the user passes a UAT. A screenshot is not their judgment |
| "They said it felt off, but the tests pass" | A `verify: uat` SC is *defined* by their judgment. Tests are irrelevant to it |
| "I'll write 12 thorough steps" | Nobody runs 12 steps. Short and pointed beats exhaustive |
| "expect: verify the feature works" | Unfalsifiable. Name the observation |
