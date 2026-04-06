# Harness: TDD Enforcement

TDD discipline rules for the gsd-executor agent. This skill is injected via `agent_skills` during plan execution.

## Authority

Follow ALL rules in the files below. No exceptions without explicit human approval.

## Files

- ../rules/tdd-enforcement.md — Read this file. It contains the TDD Iron Law, anti-rationalization red flags, deletion penalty, and zero-placeholder gate.

## Exemptions

Check `.planning/harness.json` field `tdd_exempt_plan_types`. If the current plan's type matches one of ["config", "docs", "scaffolding"], the TDD Iron Law does not apply. All other rules (zero-placeholder gate) still apply regardless of plan type.
