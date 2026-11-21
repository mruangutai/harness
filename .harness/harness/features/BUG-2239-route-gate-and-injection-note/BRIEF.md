# BRIEF — BUG-2239 route gate and injection note

## Problem

Operators can sign a plan that intake accepts but CI refuses, dispatchers mistake hook-injected schema fields for fields they supplied, and check-skill-weight.py --json crashes instead of producing its report. The settled grilling records BUG-2171's 75-line task passing intake before CI refused it, four schema-provenance misunderstandings, and the missing json import (NameError, exit 1 at immutable base 926383aef86ee505d2909c291ef4ab672b8ea09b); plain mode works.

## Done when — by perspective

**operator** — I can rely on intake rejecting the same per-plan violations as the route gate, on context arriving with the task call's result identifying schema fields supplied by the hook rather than me, and on a valid skill-weight report being available as JSON without losing plain output.

**code maintainer** — I can change the shared route rules without maintaining a second copy, and regression tests catch route enforcement, schema disclosure and JSON CLI defects before they recur.

## Success criteria

- SC-01 (operator): For the plan being checked, plan-merge.py check fails on every VIOLATION produced by check-plan-routes.process_plan_yaml, including machine-field budget, feature/task status and routing violations; a valid plan remains accepted. QA demonstrates red-before/green-after evidence for previously missed violations: routing red is absence of the shared VIOLATION line, since routing already exits 1; budget and status cases demonstrate exit-code red.
  verify: automated evidence: integration
- SC-02 (operator): Whenever the task branch's withDigestSchemas returns revised input, its response also carries OMP additionalContext with the exact sentence: "The hook injected outputSchema and schemaMode into this task call; never copy these fields into a task call." When no input revision occurs it emits no injection note, including non-Harness dispatches; existing refusal behavior is preserved. QA demonstrates failing-then-passing regression tests.
  verify: automated evidence: unit
- SC-03 (code maintainer): At git show <review_sha>:.claude/skills/harness/bin/plan_merge/check.py, the check delegates to check-plan-routes.process_plan_yaml for the target plan and turns its VIOLATION findings into failures without copying budget, status or routing rules.
  verify: inspection
- SC-04 (code maintainer): Automated regressions independently exercise over-budget, invalid feature/task status, routing failure, valid-plan acceptance and target-plan isolation using the shared rule processor, with red-before/green-after evidence for the previously missed violations.
  verify: automated evidence: integration
- SC-05 (code maintainer): Automated hook regressions assert the revised input and exact additionalContext together for single and batch schema injection, and absence of the note without injection, with red-before/green-after evidence for the missing-note cases.
  verify: automated evidence: unit
- SC-06 (operator): On a valid synthetic fixture, an actual check-skill-weight.py --json CLI subprocess exits 0 and its stdout parses as valid JSON with the expected report values; the same fixture's plain-mode CLI retains its successful output and status. Preserve authentic red evidence from this same new regression against immutable base 926383aef86ee505d2909c291ef4ab672b8ea09b and corresponding green evidence at the fix, recording command, subject identity, exit and output; intake gates and narrative are not substitutes.
  verify: automated evidence: integration

## Verification gaps

Unit and integration have active runners covering the named tests. Typecheck has an unresolved null runner and matches harness-hooks.ts: these criteria do not prove repository-wide static type correctness; unit runtime assertions carry SC-02 and SC-05 instead. No browser/component surface or live-model comprehension outcome is claimed; no UAT criterion requires the operator personally. No build or test suite runs during intake.

## Constraints

- DEC-174 BLOCKS team execution of hooks, gates and their tests: every task is main-session-direct and every edit stays within the assigned BUG-2239 product checkout.
- DEC-182 SUPPLIES real YAML, controlled plan writes and the 50-machine-field-line task budget; the settled remedy reuses the existing per-plan processor as the single source of rules.
- DEC-225 SUPPLIES bounded patch intake without panel or goalcheck. The operator explicitly permits one or two tasks and requires main-session-direct, overriding generic patch defaults.
- DEC-120 BLOCKS approval by spawned agents; both artifacts remain pending.
- Production/test ownership is exactly the six paths named in the plan, including check-skill-weight.py and its existing integration regression file. docs/spec.md, docs/decisions.md and docs/architecture.md are absent in the assigned product checkout; no alternate-root documents substitute for those missing inputs.

## Out of scope

- check-plan-routes.py rules themselves, CI workflow and sign-approval — the shared rules already exist and signing is downstream of check.
- BUG-2171 refusal-text line — the chosen remedy addresses successful dispatches rather than changing that shipped refusal.
- #2241 smoke run ids — explicitly assigned to a separate patch.

## Approval

status: approved
approved-by: operator
date: 2026-11-21
