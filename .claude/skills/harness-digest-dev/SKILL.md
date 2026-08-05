---
name: harness-digest-dev
description: The return contract shared by the four engineering specialists — frontend-dev, backend-dev, ai-dev, data-engineer. One canonical copy; the agent files point here.
user-invocable: false
---

# Dev return contract

The four dev personas share one digest schema, so they share one template. This is the canonical
copy — the agent files deliberately do not restate it, because four inline copies is how they
drifted apart before (DEC-126).

````
```yaml
VERDICT: PASS | FAIL | BLOCKED | ESCALATE
DIGEST:
  headline: <one line — what now works, not what you did>
  tests_added: <n>
  suite: pass|fail|n/a         # n/a ONLY if no tests ran at all (refused/blocked task).
                               # n/a with VERDICT: PASS is rejected — DEC-173
  task: T-NN|none              # your task's id, verbatim from your dispatch. `none` ONLY when
                               # this dispatch carries no PLAN task at all (DEC-175)
  task_verify: pass|fail|n/a   # your TASK's declared verify: command — NOT your test suite.
                               # n/a ONLY if you refused or were blocked. fail or n/a with
                               # VERDICT: PASS is rejected, dev-ops included — no carve-out.
                               # Omit this field entirely when task: none — there is no command
  blocked_on: <text|none>
  open_questions:
    - { id: Q1, question: "<text>", blocking: true|false }   # [] if none
  files_touched: [<paths>]        # [] if you changed none
  expertise_update: [<ops>]       # [] except under a distillation dispatch (harness-expertise)
artifact: <path>
```
````

**Every field is required** (DEC-121) — `[]` for an empty list, `none` for an inapplicable scalar.
The `SubagentStop` hook rejects a return missing any of them.

## Run your task's `verify:` before you return

Your dispatch carries two strings verbatim: your task's `T-NN` id and its `verify:` command. Run
that command. Cross-check it against the same task in `.harness/features/<FEAT>/PLAN.md` — you hold
repo-wide read — and if your dispatch and PLAN.md disagree, return `BLOCKED` naming both strings
rather than picking one; a paraphrased command verifies something nobody planned.

`suite` and `task_verify` answer different questions and a passing suite never substitutes for a
passing verify. `suite` is your own tests; `task_verify` is the check the plan declared for this
task, which is why it is the cheapest gate in the system and why it used to be authored and then run
by nobody.

## Reaching a boundary (shared by the same four)

You cannot write outside your domain; the hook names what you may write. **Never work around it** —
a path that should be yours belongs in the manifest, and a change needing another specialist's files
is a routing decision for your lead: return it in `open_questions`. Shared files (`package.json`,
lockfiles, `tsconfig.json`) are owned by nobody — allowed, serialized, and your lead attributes the
write.
