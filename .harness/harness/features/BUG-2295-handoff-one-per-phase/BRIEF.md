# BRIEF — BUG-2295 One handoff per phase

## Problem

FEAT-2229 reached ship with recorded validation but only cycle-suffixed validate handoffs, so the ship gate refused it until main supplied notes/handoff-validate.md. At origin/main dd04e52a, the main-session measurement found every feature without that canonical note had an all-main-session-direct plan except team-built FEAT-2229; this is naming drift, not a missing-validation generalization. Writers can currently create the suffixed names despite the documented supersede convention, and the ship comment incorrectly attributes its requirement at done to INV-17 after DEC-252.

## Done when — by perspective

**operator** — I receive an actionable refusal when I try a cycle-suffixed handoff name, pointing me to the single note to supersede. Shipping retains its existing validation prerequisite and shipped history remains untouched.

**code maintainer** — I have regression coverage for the filename rule without losing existing handoff shape checks, and the ship comment accurately explains the remaining prerequisite.

## Success criteria

- SC-01 (operator): Writing notes/handoff-<phase>-c<N>.md is refused with guidance to supersede notes/handoff-<phase>.md; a valid canonical note remains accepted. Cover multiple phases and multi-digit cycles, with qa demonstrating the new refusal assertions fail before the production fix.
  verify: automated evidence: integration
- SC-02 (code maintainer): The integration handoff regressions exercise suffixed names through Write and Edit reconstruction while retaining canonical acceptance and existing cap, required-section and Done when checks; qa records failing-then-passing filename assertions.
  verify: automated evidence: integration
- SC-03 (code maintainer): At git show <review_sha>:.claude/skills/harness/bin/gh-sync.py, cmd_ship no longer claims INV-17 requires a validate handoff at done; its comment distinguishes the preventive ship prerequisite from DEC-252's shipped-feature exemption.
  verify: inspection
- SC-04 (operator): Comparing git show dd04e52a:.claude/skills/harness/bin/gh-sync.py with git show <review_sha>:.claude/skills/harness/bin/gh-sync.py shows the cmd_ship handoff predicate and exemption behavior unchanged. The pinned diff from dd04e52a to <review_sha> contains no rename, deletion or content change to shipped FEAT-2225 -c2/-c3/-c5 or FEAT-2229 -c3/-c4/-c5 handoff notes.
  verify: inspection

## Verification gaps

None for this bounded Python filename-rule surface: integration has an active runner covering tests/integration/**. SC-03 and SC-04 require pinned inspection, not a claim from a green suite. No interactive surface requires UAT or a prototype. Production tests are not run during intake; main owns fail-first and final execution. Null component, ui and typecheck runners do not cover these Python files. The locally_run handoff_comprehension probe concerns successor comprehension; note contents and its contract are unchanged here.

## Constraints

- DEC-174 BLOCKS team execution of enforcement changes and their tests: the entire T-01 is main-session-direct, overriding the ordinary patch team default.
- DEC-225 SUPPLIES one intake, a brief at most 120 lines and exactly T-01, with no panel or goal-check; both signatures remain pending until main records operator approval.
- DEC-252 SUPPLIES the shipped-feature exemption: done is never an INV-17 subject. Correct the stale comment without changing cmd_ship's predicate.
- DEC-254 SUPPLIES five-field decision dispositions. This patch keeps existing decisions; no decision amendment or new public interface is needed.
- Preserve RE_HANDOFF recognition of suffixed paths so the shape rule refuses them instead of bypassing checks, including Edit reconstruction. Existing cap, sections and Done when enforcement remain intact.
- PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent in the assigned checkout. Do not invent guidance or substitute Harness control-plane documents for them; the operator-settled grilling and existing product enforcement code bound this patch.

## Out of scope

- Changing the ship gate predicate to use a recorded validate run: the operator chose canonical write enforcement, not a second ship convention.
- Accepting suffixed names: that would institutionalize the naming drift.
- Renaming or deleting already-shipped suffixed notes in FEAT-2225 and FEAT-2229: they are history; the rule reads writes, not the tree.
- #2294 prune: separate validation work.

## Approval

status: approved
approved-by: operator
date: 2026-11-22
