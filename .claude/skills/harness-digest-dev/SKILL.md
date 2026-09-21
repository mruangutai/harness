---
name: harness-digest-dev
description: The return contract shared by the five engineering specialists — frontend-dev, backend-dev, ai-dev, data-engineer, dev-ops. Two schemas, one set of field rules, the verify receipt, the refusal shape, the domain boundary. One canonical copy; the agent files point here.
user-invocable: false
---

# Dev return contract

The five engineering specialists share one return contract, so they share one template. This is
the canonical copy — the agent files deliberately do not restate it, because inline copies drifted
apart before (DEC-126). `validate-digest.py` refuses a return that breaks it and names the field,
the rejected pairing and the repair; read its message, never guess a value.

## dev — frontend, backend, ai, data

````
```yaml
VERDICT: PASS | FAIL | BLOCKED | ESCALATE
DIGEST:
  headline: <one line — what now works, not what you did>
  tests_added: <n>
  suite: pass|fail|n/a
  task: T-NN|none
  task_verify: pass|fail|n/a   # omit when task: none
  blocked_on: <text|none>
  open_questions:
    - { id: Q1, question: "<text>", blocking: true|false }   # [] if none
  files_touched: [<work paths>]   # exclude the required `artifact:` receipt
  expertise_update: [<ops>]       # [] except under a distillation dispatch (harness-expertise)
artifact: <path>
```
````

## dev-ops

````
```yaml
VERDICT: PASS | FAIL | BLOCKED | ESCALATE
DIGEST:
  headline: <one line>
  change_type: config|scaffolding|infra|ci
  applied: [<paths>]
  suite: pass|fail|n/a
  task: T-NN|none
  task_verify: pass|fail|n/a   # omit when task: none
  test_kinds_written: [<kind: cmd>]   # when you ran detection
  open_questions:
    - { id: Q1, question: "<text>", blocking: true|false }   # [] if none
  files_touched: [<paths>]        # [] if you changed none
  expertise_update: [<ops>]       # [] except under a distillation dispatch (harness-expertise)
artifact: <path>
```
````

## Field rules — both schemas

- **Every field is required** (DEC-121): `[]` for an empty list, `none` for an inapplicable
  scalar. The `SubagentStop` hook rejects a return missing any of them.
- **`task`** is your task's id, verbatim from your dispatch. `none` ONLY when the dispatch carries
  no PLAN task at all — a distillation, an investigation, an architecture review (DEC-175). Then
  omit `task_verify`: there was no command.
- **`task_verify`** is the check the plan declared for your task, never your test suite. `fail` or
  `n/a` alongside `VERDICT: PASS` is rejected for every persona, dev-ops included; `n/a` means you
  refused the task or were blocked.
- **`suite: n/a` with `PASS`**: dev-ops, for work whose change type maps to `[]` in
  `test_matrix`; a dev only with `task: none` and `files_touched: []` (DEC-173).

## Run your task's `verify:` before you return

Your dispatch carries two strings verbatim: your task's `T-NN` id and its `verify:` command. Run
that command. Cross-check it against the same task in
`<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/plan.yaml` — you hold repo-wide
read — and if your dispatch and the plan disagree, return `BLOCKED` naming both strings rather
than picking one; a paraphrased command verifies something nobody planned.

Report the result as `task_verify`. Paste the command and its **verbatim** output into your receipt
(the path is in `harness-handoff`). `task_verify: pass` is a claim; the receipt is what a reviewer
checks it against. Output can be fabricated, so it is an audit trail, not a gate.

## Refusing an under-specified task

The zero-placeholder gate (`harness-tdd-enforcement`) refuses a task before executing it. The
return, complete on purpose — a refusal digest missing any field is rejected and retried, and the
retry is where unvalidated work ships (DEC-173/175):

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
````

dev-ops returns the same refusal in its own schema.

## Reaching a boundary

You cannot write outside your domain; the hook names what you may write. **Never work around it** —
a path that should be yours belongs in the manifest, and a change needing another specialist's files
is a routing decision for your lead: return it in `open_questions`. Shared files (`package.json`,
lockfiles, `tsconfig.json`) are owned by nobody — allowed, serialized, and your lead attributes the
write.
