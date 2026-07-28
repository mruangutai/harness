---
name: harness-digest-dev
description: The return contract shared by the four engineering specialists — frontend-dev, backend-dev, ai-dev, data-engineer. One canonical copy; the agent files point here.
---

# Dev return contract

The four dev personas share one digest schema, so they share one template. This is the canonical
copy — the agent files deliberately do not restate it, because four inline copies is how they
drifted apart before (DEC-126).

```
VERDICT: PASS | FAIL | BLOCKED | ESCALATE
DIGEST:
  headline: <one line — what now works, not what you did>
  tests_added: <n>
  suite: pass|fail
  blocked_on: <text|none>
  open_questions:
    - { id: Q1, question: "<text>", blocking: true|false }   # [] if none
  files_touched: [<paths>]        # [] if you changed none
  expertise_update: [<ops>]       # [] if you learned nothing durable — the usual case
artifact: <path>
```

**Every field is required** (DEC-121) — `[]` for an empty list, `none` for an inapplicable scalar.
The `SubagentStop` hook rejects a return missing any of them.
