---
name: harness-tdd-enforcement
description: The test-first Iron Law and its anti-rationalization guards — write a failing test before any production code, delete code written out of order, and reject under-specified tasks. Loaded by harness-frontend-dev, harness-backend-dev, harness-ai-dev, harness-data-engineer, and harness-dev-ops.
user-invocable: false
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

````
```yaml
VERDICT: BLOCKED
DIGEST:
  headline: task T-12 is under-specified and cannot be executed as written
  tests_added: 0
  suite: n/a
  task: T-12
  task_verify: n/a
  blocked_on: "T-12 contains a placeholder at <location>; needs pm revision"
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: none
```

**Every field, including the ones that are empty.** This return used to be written with only
`headline` and `blocked_on`, and the `SubagentStop` hook rejected it with exit 2 — so the guard
against under-specified tasks was told it had committed a contract violation at the exact moment it
fired, and the forced retry shipped unvalidated. `suite: n/a` is what makes it truthful: you ran no
tests, and DEC-173 gives that a spelling. Do not write `suite: pass` here — it is the only value the
schema used to accept, and it is a lie.

**`task_verify: n/a` is the same truth about a different question.** You ran no verify command
because you refused the task, and `n/a` is its spelling. The accompanying VERDICT is `BLOCKED`,
never `PASS` — `task_verify: n/a` alongside `PASS` is rejected for every dev persona, `dev-ops`
included. Note `task:` still names the task's real id: you were dispatched for one and refused it.
`task: none` means something else entirely — a dispatch that carried no PLAN task at all — and
writing it here would misreport a refusal as a non-task run.

**The id is a concrete `T-12`, not `T-NN`.** `TASK_ID_RE` is `T-\d+|none`, so the placeholder
spelling is rejected by the validator — the same zero-placeholder discipline this skill already
enforces on tasks. This block is piped through `validate-digest.py` by T-04's own verify, so a
placeholder here would fail for a reason that has nothing to do with what the example teaches.
````

## Exemptions

Read `test_matrix` in `.harness/harness.json`. Change types mapping to `[]` — `config`, `scaffolding`,
`docs` — are exempt from the Iron Law and the cycle. This is most of `dev-ops`'s work.

**The zero-placeholder gate is never exempt.** It applies to every task of every type.

A behavioural change is never exempt because it is small. Size is not a change type.

## Your task's `verify:` and its receipt

The Iron Law governs your tests. It says nothing about the check the PLAN declared for your task,
and those are different questions — a green suite has never meant a green `verify:`.

Your dispatch carries the task's `T-NN` id and its `verify:` command **verbatim** (the lead is
required to quote both). Run the command before you return, report the result as `task_verify`, and
paste the command together with its **verbatim** output into your B-7 receipt at
`.harness/features/<FEAT>/notes/receipt-<your-agent-name>-<runid>.md`.

Why the receipt and not just the field: `task_verify: pass` is a claim, and a claim with nothing
behind it converts a skipped check into an unfalsifiable one. The receipt is what a reviewer checks
it against. It does not make skipping impossible — output can be fabricated — so treat it as an
audit trail, not a gate.
