<!-- TEMPLATE — harness-pm authors under
     <HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/BRIEF.md, including pending
     Approval fields. Only main records the user's explicit signature; the orchestrator never approves.
     Before drafting, MUST read <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-brief/SKILL.md
     for resident authoring rules. Replace every <angle-bracket>; preserve section order.
     Nothing downstream runs unsigned. A patch uses this shape in at most 120 lines. -->

# BRIEF — <FEAT-NN> <title>

## Problem

<Observed hurt: who hits it, when, and what it costs.>

## Done when — by perspective

<First-person promises, 1–3 sentences each. Standard perspective definitions and the
implementation-neutrality test live in harness-brief; omit perspectives with nothing to say.>

**operator** — <what I can rely on, in my own words>

**code maintainer** — <...>

## KPIs

<Optional. Only when a number will be read after ship: baseline, target, and where it is measured
from. Delete the section rather than leave it empty.>

| KPI | Baseline | Target |
|---|---|---|
| <name> | <measured, with the source> | <number> |

## Success criteria

<One observable outcome per SC, with one declared perspective and one verification method.
Automated criteria also name an evidence kind. Apply harness-brief's SC well-formedness rules.>

- SC-01 (operator): <observable outcome>
  verify: automated        evidence: unit
- SC-02 (code maintainer): <observable outcome>
  verify: inspection
- SC-03 (end user): <observable outcome>
  verify: uat

## Verification gaps

<Null-runner kinds touching this feature: what is NOT proven and what carries it instead.
Name each affected SC too (INV-49). "none" is legal; silence is not.>

- <kind> has no runner: <what rests on what instead>

## Constraints

<Existing contracts, conventions, things not to touch. Cite decisions by number as BLOCKS or SUPPLIES.>

- <constraint>

## Out of scope

<The grilling artifact's exclusions, with reasons; only user-chosen scope.>

- <exclusion — why>

## Approval

status: pending
approved-by:
date:

<!-- pm authors the pending fields above; only the main session records the user's
     explicit signature. See harness-brief's Approval rule (DEC-120). -->
