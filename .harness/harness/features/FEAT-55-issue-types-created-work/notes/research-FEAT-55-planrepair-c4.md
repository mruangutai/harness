# Plan repair c4 — FEAT-55 — the two operator rulings applied

**Both rulings are in the plan and nothing else moved.** REQ-07's refuse-before-create is now
red-then-green tested on all three writers, and D-19's `because:` records the grant it previously
denied existed. `approval:` and `panel:` are byte-unchanged; BRIEF's `## Approval` still reads
`status: pending` (BRIEF.md:205). The package returns for signature whole.

Source of authority: `notes/answers-plan-panel-20260904.md`, two rulings, neither widened.

## Ruling 1 — PF-f1031f76b4537f1cd9b60ddc0559b7d1 (high, gating): FIXED

| | added case | traces | verify |
|---|---|---|---|
| T-05 (gh-sync backlog) | **G** | `+REQ-07` | loop `A B C D E F G`; strings `+partial +github.issue_types` |
| T-07 (factory) | **I** | `+REQ-07` | loop `A B C D E F G H I`; strings `+partial +github.issue_types` |

Case letters re-derived at source, not assumed: T-05 ran A–F, T-07 ran A–H (the dispatch's expected
`I` is confirmed). Both cases are the `FAKE_TYPES=partial` shape T-03 case F uses — Bug and Feature
declared, Task absent — and each task's fake-gh fixture paragraph gained the `partial` branch, since
neither fixture answered it before.

Each case asserts the failure mode the panel named: zero `issue create`, zero `updateIssue`, non-zero
exit, and the message naming both `Task` and `github.issue_types`. T-07 case I additionally binds
the **parent's** create, because T-08 §6's required set spans parent + every `new` task, so a
parent-only or per-task check must fail it.

**T-06 and T-08 were not edited at all.** Their `traces:` already carry REQ-07, and each verify
already runs the file carrying its route's new case — T-06 runs `test-gh-backlog-issue-types.py`,
T-08 runs `test-factory-issue-types.py`. The green half needed no addition, so no overlap with the
unruled PF-452948 arose.

**Proof the new gates discriminate** (throwaway, not kept): both amended verify blocks were run
verbatim against a synthetic target file carrying every required marker (exit 0) and then against
one with each new marker dropped in turn — `CASE G:`, `CASE I:`, `partial`, `github.issue_types` —
each omission exits 1 with the naming message. A prose-only case would not have passed.

## SC-08 — REWORDED, and this is an edit to an approval-gated artifact

`BRIEF.md:132-139`. I judged it **necessary**. The panel's root cause is that SC-08 named no route,
so a goal-check could discharge it on a single command's evidence — exactly the state the operator
refused. Leaving it route-silent would make the ruling incidental: the cases would exist, but nothing
in the goal of record would require them to keep existing. SC-08 now names all three creation
commands (`gh-sync.py open`, `gh-sync.py backlog`, `factory_decompose.py`), requires the assertion
per command in that command's own test file, and states that one command's refusal never discharges
another's. Method and evidence kind unchanged (`automated` / `integration`). `## Approval` untouched.

## Ruling 2 — PF-610431f7d96408d23666cc4e60071501 (med): probe KEPT, D-19 `because:` rewritten

`choice:` is byte-unchanged; T-10 §6, SC-10's LIVE verdict and the eighth read-back purpose's third
clause all stand. Only `because:` changed, because its old text asserted "no operator grant exists" —
false on its face once the ruling landed. The new text records the grant, cites
`notes/answers-plan-panel-20260904.md`, and preserves both surviving reasons: the grant covers the
opt-in flag only, and the default stays read-only because harness.json registers the kind and a
registered kind runs unattended. No decision id added — this records the operator's act, not a new
choice.

## Coupling the next reader must not miss

**Case G is authored against the receipt shape the plan CURRENTLY specifies** — T-06 §5's plain
`json.dump` of `{"items": {"<nature>:<title>": {"number": int, "typed": bool}}}` at
`<featdir>/backlog-issues.json`. That shape is the subject of the **unruled**
`PF-1286544c197d1b0eb4a9b0dc8e1234dc`, the panel's own `must_fix` #1, whose `fix_order` says it
changes what T-05's fixtures assert. Case G's "no `backlog-issues.json` exists afterwards" assertion
**would need re-authoring** if the operator later directs that fix — as would cases C, E and F, which
already depended on it. Nothing here pre-empts that ruling.

The other four unruled findings (PF-452948, PF-e27f1c, PF-0c12a0, PF-9a71cb) were not touched, not
softened and not re-disposed.

## Mechanics — the dispatch named a verb that cannot do this

The dispatch mandated `plan-merge.py apply`. `apply` is **add-only**: it raises `CONFLICT` exit 7 on
any id whose value differs from the base (`plan-merge.py:736`), so it cannot modify an existing
T-05, T-07 or D-19. The route that can is the same tool's `amend` verb — the compare-and-swap added
by BUG-1128 for exactly this, under the same lock, reaching `tasks:` and `decisions:` and refusing
`approval:` (`AMENDABLE_KEYS`, `plan-merge.py:1232`). Six amendments, each `--expect-sha256` against
its own `--show` hash. No Edit, no Write, no redirect touched plan.yaml.

`check-plan-routes.py` on the amended plan: **0 violations, exit 0**. Note `traces:` now renders as a
block list rather than flow style — `amend --yaml-value` dumps through `safe_dump`; the parsed value
is what matters and reloads correctly.

## Open questions

- **Q1 (non-blocking):** pm's dispatch template names `apply` as the sole plan-writing route, but
  `apply` cannot revise an existing task or decision. Every revision cycle after the first needs
  `amend`. The dispatch contract should name it, or a revision dispatch reads as impossible.
