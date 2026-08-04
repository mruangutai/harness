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

## Reaching a boundary (shared by the same four)

You cannot write outside your domain; the hook names what you may write. **Never work around it** —
a path that should be yours belongs in the manifest, and a change needing another specialist's files
is a routing decision for your lead: return it in `open_questions`. Shared files (`package.json`,
lockfiles, `tsconfig.json`) are owned by nobody — allowed, serialized, and your lead attributes the
write.
