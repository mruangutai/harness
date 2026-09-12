# STATE — FEAT-59 Proportional flow

## Current

Built and integrated on `feat/FEAT-59-proportional-flow` at `a1c3a683`; PR open for the
operator's diff review. DEC-174 main-session-direct build: no orchestrator, lead or persona ran;
eight generic subagents owned file-bounded slices under main-session decomposition. Unit and
integration suites green; port, adapter and command checkers exit 0; `check-state.sh` reports
0 violations on the branch.

Acceptance is two live flows and is OPEN: SC-23 (next real bug through `/harness-patch`) and
SC-24 (next real feature through `/harness-plan`). The brief is not done until both ship.

## Open questions

- None for the operator. The PR is the one contact point.

## Pointers

- `notes/delivery-FEAT-59.md` — SC-to-evidence map, the judgement record, known limits.
- BRIEF `## KPIs` — the numbers SC-23/24 are graded against.
