<!-- TEMPLATE — harness-pm owns this file, EXCEPT `## Approval`, which only the
     orchestrator writes (SPEC 2.3). /harness-init does NOT create it: a plan is
     written when there is something to plan. Replace every <angle-bracket>. -->

# PLAN — <milestone or feature set>

## Decisions

<Technical choices and their cost. A decision that deviates from a team convention
in team-config.yaml MUST appear here — an agent may not quietly pick a different
substrate because it found one more convenient.>

- D-01: <the choice> — rationale: <why>; tradeoffs: <what was given up>

## Approval

status: pending
approved-by:
date:

<!-- RE-PLANNING RESETS THIS. A plan approved for one task set must never carry its
     signature onto a changed one. pm resets to pending on any task-set change; the
     state check treats a stale approval as a violation. -->

## Features

- FEAT-01: <name>
  traces: REQ-01, REQ-02
  tasks: T-01, T-02

## Tasks

<Every task is FULLY specified: exact paths, complete intent, a verify command that
returns pass/fail in under 60s, and traceability. No placeholders, no "TBD", no
"as appropriate". A task a subagent has to interpret is a task it will interpret
differently from you.

`change_type:` is MANDATORY on every task — qa reads it to apply the test matrix,
and a task without one BLOCKS the gate. One of:
  logic | api | cross_module | frontend | feature | bugfix | ai_behavior
  | config | scaffolding | docs>

- T-01: <imperative title>
  files: <exact paths, not directories>
  intent: <complete description of the change — what the code must do afterwards>
  change_type: <see list above>
  verify: <command returning pass/fail in <60s>
  traces: REQ-01, D-01
  feature: FEAT-01
  status: pending
