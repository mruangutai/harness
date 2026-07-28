<!-- TEMPLATE — /harness-init writes the first draft; harness-pm owns it thereafter,
     EXCEPT `## Approval`, which only the orchestrator writes (SPEC 2.3). Nothing
     downstream may run against an unapproved brief. Replace every <angle-bracket>. -->

# BRIEF — <project name>

## Problem

<What hurts today, observed — not the solution. One short paragraph: who hits it, when, and what it
costs. If you cannot state the problem without naming the solution, you have a solution looking for
a problem (DEC-129).>

## Goal

<One paragraph, in the user's own framing. What changes, and for whom. Not how.>

## Requirements

<Apply the REQ test to each: a requirement survives changing your mind about
implementation. Swap the whole technical approach — if it changes, it was a
decision, not a requirement. Move it to Constraints or drop it.>

- REQ-01: <what a user can do, stated as an outcome>
- REQ-02: <...>

## Constraints

<Anything that bounds the solution: existing contracts, conventions, things not to
touch, technology decisions the user has already made.>

- <constraint>

## Success Criteria

<Every SC declares its verification method WHEN IT IS WRITTEN. An SC with no
`verify:` is not verifiable and blocks the goal-check — the state check treats it
like a task missing `change_type`.

  verify: automated   -> a test proves it. ALSO needs `evidence:` naming a test
                         kind from harness.json test_kinds. Evidence: qa.
  verify: inspection  -> a reviewer reads code or output and cites file:line.
                         Evidence: code- / security- / ui-reviewer.
  verify: uat         -> only the user can judge it. Becomes a step in
                         .harness/notes/uat-<FEAT>.md, executed by the user.

Reject and rewrite any SC that: has no verify: or two; is `automated` with no
`evidence:`; is not falsifiable ("the code is clean"); or restates a requirement
instead of naming an outcome.>

- SC-01: <observable outcome>
  verify: automated        evidence: unit
- SC-02: <observable outcome>
  verify: inspection
- SC-03: <observable outcome>
  verify: uat

## Approval

status: pending
approved-by:
date:

<!-- ONLY the user approves. The orchestrator writes this section on their explicit
     say-so and never on its own initiative; pm never touches it at all.
     `status: approved` unblocks everything downstream — it is the signature on the
     goal of record, not a formality. -->
