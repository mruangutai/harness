---
name: harness-tdd-enforcement
description: The test-first Iron Law and its anti-rationalization guards — write a failing test before any production code, delete code written out of order, and reject under-specified tasks. Loaded by harness-frontend-dev, harness-backend-dev, harness-ai-dev, harness-data-engineer, and harness-dev-ops.
---

# TDD Enforcement

Mandatory. No exceptions without explicit human approval **in the current session**.

## The Iron Law

**Write a failing test before writing any production code.**

Production code written before a failing test existed MUST be **deleted** — not kept as reference, not
adapted, not "tested afterward." Delete it and restart in correct order.

That sounds harsh, and it is the point: if code written test-last can be salvaged by writing tests
after, the law has no teeth and you will take that path every time you are under pressure.

**The only valid exemption is explicit human approval in this session.** "The user implied it was fine",
"the task didn't mention tests", and "the plan didn't include a test task" are **not** approvals.

## The cycle

1. **RED** — write the test. **Run it. Watch it fail.** A test you have not seen fail proves nothing;
   it may be passing vacuously.
2. **GREEN** — write the minimum production code to pass. No extra features.
3. **REFACTOR** — only while green. Never refactor a red suite.

## Red flags — stop immediately

- Writing production code with no failing test in place
- Writing the test after the implementation
- Refactoring while any test is red
- Adding a feature during GREEN
- Skipping the RED verification — never actually watching it fail
- Modifying an existing test to make it pass instead of fixing the code
- Being unable to show the failing run that preceded your change

**And these thoughts, which are rationalizations, not reasons:**

| Thought | Reality |
|---|---|
| "This is a simple function, tests add nothing" | Simple functions are where off-by-one lives |
| "The test would be too hard to write" | Hard-to-test is a design finding. Report it |
| "I'll add tests once it works" | Then you will write tests that describe the bug you shipped |
| "We're in a rush" | The rework loop is slower. Measured here: 0.44 escaped defects per feature |
| "It's obvious code" | Obvious to you, now. Not to the next reader, not in six months |

If you notice any of these: **stop, delete the out-of-order code, restart.**

## Zero-placeholder gate — always applies

Before executing a task, scan it. **Refuse it** if it contains:

- `TBD`, `TODO`, `[placeholder]`, `[fill in]`, or any bracket-notation deferral
- "implement X" with no file paths and no statement of what X produces
- "similar to the task above" or "follow the existing pattern" — deferred specification
- Vague verbs with no target: "add error handling", "improve performance", "update the config"
- No concrete file path anywhere in the task

Do **not** infer the intent. Return:

```
VERDICT: BLOCKED
DIGEST:
  headline: task T-NN is under-specified and cannot be executed as written
  blocked_on: "T-NN contains a placeholder at <location>; needs pm revision"
```

## Exemptions

Read `test_matrix` in `.harness/harness.json`. Change types mapping to `[]` — `config`, `scaffolding`,
`docs` — are exempt from the Iron Law and the cycle. This is most of `dev-ops`'s work.

**The zero-placeholder gate is never exempt.** It applies to every task of every type.

A behavioural change is never exempt because it is small. Size is not a change type.
