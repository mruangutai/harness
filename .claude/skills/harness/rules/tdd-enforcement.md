# TDD Enforcement

This file is injected via `agent_skills` into gsd-executor. All rules below are mandatory. No exceptions without explicit human approval in the current session.

## The Iron Law

You MUST write a failing test before writing any production code. Code written before tests must be deleted and rewritten in correct TDD order. There are no exceptions without explicit human approval.

### Deletion Penalty

If production code is discovered to have been written before a failing test existed, the production code MUST be deleted — not kept as reference, not adapted. Delete it and restart in correct TDD order.

### Human Approval Gate

The ONLY way to skip TDD is explicit human approval in the current session. "The user implied it was okay" or "the task description didn't mention tests" are NOT valid approvals.

## Red Flags — Stop Immediately If You Notice Any of These

- [ ] You are writing production code without a failing test already existing
- [ ] You wrote the test after the implementation
- [ ] You wrote multiple tests before any implementation
- [ ] You are refactoring while any test is red
- [ ] You added a feature while in the GREEN phase
- [ ] You skipped verifying the RED state (confirming the test actually fails before writing production code)
- [ ] You are about to say "this is just a simple function, tests aren't needed"
- [ ] You are about to say "the test would be too hard to write"
- [ ] You are about to say "I'll add tests after I get it working"
- [ ] You are about to say "we're in a rush, skip for now"
- [ ] You are about to say "it's obvious code, testing adds no value"
- [ ] You are modifying existing tests to make them pass instead of writing new code
- [ ] You cannot demonstrate the failing test run before your code changes

If you observe any of these, STOP, delete the out-of-order production code, and restart in correct TDD sequence.

## Zero-Placeholder Gate

Before executing any task, scan it for forbidden patterns:

- The literal string "TBD" or "TODO"
- "[placeholder]", "[fill in]", or similar bracket-notation deferral
- Task descriptions like "implement X" without exact file paths and code intent
- References like "similar to task N above" that defer specification
- Vague verbs without targets: "add error handling", "improve performance", "update the config"
- Absence of at least one concrete file path in the task

If any are found: STOP. Do not attempt to infer intent. Report the violation: "Task [name] contains a placeholder at [location]. Plan revision required before execution."

## Exemptions

Check `.planning/harness.json` field `tdd_exempt_plan_types`. If the current plan's `type` frontmatter matches one of the exempt types (currently: config, docs, scaffolding), the Iron Law (Section 2) and Red Flags (Section 3) do not apply. The Zero-Placeholder Gate (Section 4) ALWAYS applies regardless of plan type.
