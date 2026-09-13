<!-- TEMPLATE — /harness-plan and /harness-patch write the first draft under
     <HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/BRIEF.md; harness-pm owns it thereafter,
     EXCEPT `## Approval`, which only the orchestrator writes (SPEC 2.3). Nothing
     downstream may run against an unapproved brief. Replace every <angle-bracket>.
     Sections appear in this order and no others: there is no `## Goal` and no
     `## Requirements` — done is stated by perspective, and the SCs derive from it.
     A `patch` mission writes this same shape in at most 120 lines. -->

# BRIEF — <FEAT-NN> <title>

## Problem

<What hurts today, observed — not the solution. One short paragraph: who hits it, when, and what it
costs. If you cannot state the problem without naming the solution, you have a solution looking for
a problem (DEC-129).>

## Done when — by perspective

<One statement of "done" per feature, in one place. Each line is a person who will judge the
result, speaking in the first person about what they can rely on once this ships: 1–3 sentences,
what changes for them, never how it is built. The standard names — use them spelled exactly so,
and add a project-specific name only when none of these fits:

  operator          the person who signs, rules on rework, and audits the record afterwards
  code maintainer   whoever reads, changes or extends the code six months from now
  end user          the person the surface is for
  reader            a reviewer, qa, or panel member grading the result
  orchestrator      the agent dispatching the phases and inheriting the spend

A perspective with nothing to say is OMITTED, never written as "none". The perspective test: a
statement survives changing the implementation — swap the whole technical approach and it still
holds. A trailing parenthetical is a gloss, not part of the name: `**reader (reviewer / qa)**`
declares `reader`. check-state.sh INV-38 reads this block.>

**operator** — <what I can rely on, in my own words>

**code maintainer** — <...>

## KPIs

<Optional. Only when a number will be read after ship: baseline, target, and where it is measured
from. Delete the section rather than leave it empty.>

| KPI | Baseline | Target |
|---|---|---|
| <name> | <measured, with the source> | <number> |

## Success criteria

<Every SC discharges ONE perspective and names it in parentheses. SCs derive from the perspective
block, never the other way round: a perspective no SC discharges is an unverified promise; an SC
that discharges no perspective is scope creep. INV-38 refuses both.

Every SC declares its verification method WHEN IT IS WRITTEN. An SC with no `verify:` is not
verifiable and blocks the goal-check — the state check treats it like a task missing `change_type`.

  verify: automated   -> a test proves it. ALSO needs `evidence:` naming a test
                         kind from harness.json test_kinds. Evidence: qa, with the
                         test's fail-first state demonstrated.
  verify: inspection  -> a reviewer reads code or output and cites the file and symbol.
                         Evidence: code- / security- / ui-reviewer.
  verify: uat         -> only the user can judge it. Becomes a step in
                         .harness/features/<FEAT>/notes/uat.md, executed by the user.

An SC is scoped to this feature. One whose `verify:` runs check-state.sh or check-domain.sh with
no feature-scoped argument grades the whole repository, and other features' debris turns it red;
repository hygiene is a merge-time check, not a feature criterion. INV-41 refuses it (SC-16).

SC well-formedness rules live in `harness-brief` — the writer preloads them.>

- SC-01 (operator): <observable outcome>
  verify: automated        evidence: unit
- SC-02 (code maintainer): <observable outcome>
  verify: inspection
- SC-03 (end user): <observable outcome>
  verify: uat

## Verification gaps

<One line per test kind with `cmd: null` in harness.json that covers a surface this feature
touches: what is therefore NOT proven, and what carries it instead (DEC-163). "none" is a legal
value; silence is not.>

- <kind> has no runner: <what rests on what instead>

## Constraints

<Anything that bounds the solution: existing contracts, conventions, things not to
touch, technology decisions the user has already made. Name decisions by number and
say whether each BLOCKS or SUPPLIES — a mechanism this feature uses is not an obstruction.>

- <constraint>

## Out of scope

<What the grilling ruled beyond the destination, and why. A disclosure ("this does not fix X")
is scope only if the user chose it.>

- <exclusion — why>

## Approval

status: pending
approved-by:
date:

<!-- ONLY the user approves. The orchestrator writes this section on their explicit
     say-so and never on its own initiative; pm never touches it at all.
     `status: approved` unblocks everything downstream — it is the signature on the
     goal of record, not a formality. -->
