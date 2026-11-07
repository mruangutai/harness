---
name: harness-digest-dev
description: The return contract shared by the five engineering specialists — frontend-dev, backend-dev, ai-dev, data-engineer, dev-ops. Two schemas, one set of field rules, the verify receipt, the refusal shape, the domain boundary. One canonical copy; the agent files point here.
user-invocable: false
---

# Dev return contract

This is the shared engineering contract (DEC-126). `validate-digest.py` names any rejected field,
pairing and repair: follow its message, never guess a value. Common return fields and YieldTool
discipline live in `harness-handoff`; the injected persona schema owns the complete field list.

## dev — frontend, backend, ai, data

The **main session** returns this same contract when it builds a feature directly under DEC-174
(`feature-record.py run-start --agent main-session`): it wrote the diff, so it owns the same
`task` / `task_verify` / `suite` receipt, and `close-run` validates its digest as `dev` (#1895).

Schema: `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/digest-schemas/harness-backend-dev.json`;
frontend, ai and data have their own `harness-<persona>.json` with the same fields.
**Before your first engineering return or an under-specified-task refusal, read
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/digest-dev-examples.md`.**
- `blocked_on`: the blocking condition, or `none`; keep all common fields required by `harness-handoff`.

## dev-ops

Schema: `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/digest-schemas/harness-dev-ops.json`.
- `change_type`: `config|scaffolding|infra|ci`. `test_kinds_written`: `<kind: cmd>` entries
  when you ran detection, else `[]`; the shared field rules below apply unchanged.

## Field rules — both schemas

- **Every schema field is required**, on success or refusal; the OMP yield hook rejects omissions
  (DEC-121, DEC-237). Use the common empty-value rules in `harness-handoff`.
- **`task`** is your task's id, verbatim from your dispatch. `none` ONLY when the dispatch carries
  no PLAN task at all — a distillation, an investigation, an architecture review (DEC-175), or a
  scratch/note task the dispatch says is not in `plan.yaml`, even if it carries a `T-NN` label
  (#2145). Then `task_verify` is `none`: there was no command.
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
(the path is in `harness-handoff`). `validate-digest.py` refuses `task_verify: pass` when the receipt
your `artifact:` names is missing or does not carry the command as `plan.yaml` spells it; the
output itself is an audit trail a reviewer reads, not a gate.

## Refusing an under-specified task

The zero-placeholder gate (`harness-tdd-enforcement`) stops execution. Return `BLOCKED` with
every persona field: the concrete `task`, `suite: n/a`, `task_verify: n/a`, `files_touched: []`,
and `artifact: none`. Name the missing specification in the headline and, for dev, `blocked_on`;
a partial refusal is rejected and retried, not accepted (DEC-173/175).

Use the refusal example in the required reference above; dev-ops returns its own schema, never dev's.

## Reaching a boundary

You cannot write outside your domain; the hook names what you may write. **Never work around it** —
a path that should be yours belongs in the manifest, and a change needing another specialist's files
is a routing decision for your lead: return it in `open_questions`. Shared files (`package.json`,
lockfiles, `tsconfig.json`) are owned by nobody — allowed, serialized, and your lead attributes the
write.
