---
name: harness-handoff
description: The universal return contract and output discipline for every harness agent — the VERDICT/DIGEST/artifact return, BLUF, pointers not payloads, decide versus ask. Loaded by all 16 agents at every spawn.
user-invocable: false
---

# Handoff

**Handoff is by file path, never by conversation.** Your successor's context is as fresh as yours:
durable artifact, compact signal.

## Your return — three parts, always

Return one object through YieldTool — `yield({data: {VERDICT, DIGEST, artifact}})` — never a
fenced YAML block and never text: a string, `null` or absent `data` is rejected with an instruction
to return the object. Your persona's field list is its schema,
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/digest-schemas/harness-<persona>.json` (shared definitions in
`common.json`). One complete example, for `harness-documentor`
(`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/digest-schemas/harness-documentor.json`):

```js
yield({data: {
  "VERDICT": "PASS",
  "DIGEST": {
    "headline": "CLI reference now documents the --dry-run flag",
    "docs_updated": ["docs/cli.md"],
    "gaps": [],
    "stale_found": [],
    "open_questions": [{"id": "Q1", "question": "Document the deprecated --force alias?", "blocking": false}],
    "files_touched": ["docs/cli.md"],
    "expertise_update": []
  },
  "artifact": "<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/notes/receipt-harness-documentor-<runid>.md"
}})
```

Every persona carries `headline` (one line, the conclusion — not what you did), `open_questions`
(`{id, question, blocking}`), `files_touched` (work paths; excludes the required artifact receipt;
`[]` for read-only work) and `expertise_update` (`[]` except under a distillation dispatch —
harness-expertise), plus your role's fields — see your role rule. `artifact` is the path to what
you wrote. Durable fenced YAML in a digest.md is validator-owned output, never yours to write.

Close every prose code fence before returning a lead object. The validator refuses an append
that the durable reader cannot select, without changing existing bytes; correct the human
assessment's unfinished fence and retry the object.

| VERDICT | Means |
|---|---|
| `PASS` | done. May carry advisory notes |
| `FAIL` | a gate failed. Retrying or looping back is meaningful |
| `BLOCKED` | cannot proceed. Looping back is futile — escalate |
| `ESCALATE` | needs the tier above (lead → orchestrator → user) |

**`bin/validate-digest.py` is the contract** — exact tokens and field names, since the runner routes
on them; every field present, "nothing" as an explicit `[]` or `none`, never an omitted key;
`findings` and `fail_first` checked inside the list. Violation → `BLOCKED (contract violation)`.

**Never invent a verdict** — undeterminable is `BLOCKED`, with why.

**A dispatcher never yields with a live child:** the host holds its `task` call until the child is
terminal (DEC-204), and the digest gate refuses a return with children in flight (DEC-233).

## Harness-owned paths — anchored, never relative

- `HARNESS_CONTROL_PLANE_ROOT: <absolute path>` in your starting context is the Harness control plane, not your working directory. `UNRESOLVED` → `VERDICT: BLOCKED`; never guess.
- `<HARNESS_CONTROL_PLANE_ROOT>` prefixes every Harness-owned read; `<HARNESS_FEATURE_TREE_ROOT>` prefixes every feature-directory write. Never interchangeable; never a bare relative Harness-owned path in an instruction.
- The control-plane root is read-only to you; write grants are unchanged (check-domain.py).

## Writing the artifact

- **BLUF.** The conclusion first, never "I explored X, then Y."
- **Claims plus pointers, never payloads.** "Auth is JWT (`auth/mw.ts:42`)" — they have the path.
- **Open questions, explicitly** — the next agent's to-do list.
- **Bounded — one screen.**

Routing reads only VERDICT and DIGEST; put what it depends on there.

**Where it goes — the per-feature path your persona owns, never one a dispatch invents.** Read
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/artifact-paths.md` before your first
feature-directory write: your path, the root-resolve command, the no-shell rule. The five engineers
and the documentor own no path and write the receipt
`<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/notes/receipt-<your-agent-name>-<runid>.md`
— **not your observations log**.

## Decide or ask — scoped by reversibility

**Cheap and reversible** (naming, local structure, test shape): decide; record it in the DIGEST.
**Expensive or hard to reverse** (schema, API contract, new dependency): ask via `open_questions`.
**Changes scope, the goal, or an approved decision**: always ask — it is not yours.

**Out of scope is out of scope**: note it in the DIGEST, never fix it. **An open question does
not block you**: raise it, do what you can, return; a member never waits on a human.

## Consulting decisions — cited is a floor, never a ceiling

Cited decisions are the **minimum**, not the set: the dispatcher's framing is a hypothesis.
**Go broader** when a citation references an uncited decision, when the citations do not cover what
you judge, or when your Expertise implies an omitted rule.
