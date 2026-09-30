# `.harness/` — the project's state

Everything the harness knows about *this* project. Plain files, read and written by agents at spawn
time — no engine, no build step, no database.

**Written by the `harness-init` skill, which configures this checkout.** It writes *this clone's*
directory once; everything after that is written by the agents that own each path (see the table
below). A fleet member gets no such directory — only its own `harness.json`, landed there by the
`harness-add-repo` skill (DEC-221, DEC-222).

## Layout

| Path | What it is | Written by |
|---|---|---|
| `BRIEF.md` | The **goal of record**: Goal, `REQ-NN`, Constraints, `SC-NN` (each with a `verify:` method), `## Approval`. Stable across the project. | `pm` drafts · **you** approve |
| `PLAN.md` | Active plan: `## Decisions` (`D-NN`), `## Approval`, `## Features` (`FEAT-NN`), `## Tasks` (`T-NN`, each with `change_type:`) | `pm` — except `## Approval` |
| `DESIGN.md` | The visual design contract: palette in both themes, type scale, spacing, component direction | `visual-designer` |
| `team-config.yaml` | **The org as data** — membership, `consult-when` routing, and each agent's writable `domain`. Read by `check-domain.py` on every write | `harness-init`, **in this control plane only** — no product repository has one, seeded from detection |
| `harness.json` | `test_matrix`, `test_kinds`, `gates`, `budgets`, `log_retention_days` | `harness-init` for this control plane's own copy; `harness-add-repo` for a fleet member's, which must land on that repository's default branch · `dev-ops` fills `test_kinds` |
| `expertise/<agent>.md` | Per-agent durable **craft** — how that agent works, true wherever it works. Budget **150 lines**. Injected at every OMP task-agent start; the agent never reads it itself | each agent, its own file only |
| `<repo>/expertise/<agent>.md` | Per-agent repository-specific knowledge. Budget **40 lines**. Injected by the same OMP lifecycle extension alongside craft knowledge | each agent, its own file only |
| `efforts/<slug>/` | A pre-feature **wayfinding map** (`MAP.md` + `tickets/`): a vague idea being taken to plannable clarity across sittings. Local markdown, never the issue tracker (DEC-165). Retired or archived once its effort hands off to `/harness-plan` | the **main session** |
| `notes/grilling-*.md` | A single-sitting dialog-to-clarity record: destination, settled decisions, fog, out-of-scope, facts verified — pm's BRIEF input (DEC-164) | the **main session** |
| `features/<FEAT>/notes/` | That feature's durable artifacts: `research-*`, `review-<persona>-c<cycle>.md`, `qa-*`, `answers-<runid>.md`, `ship-review-<runid>.md`, `uat.md`, `mockups/`, `prototypes/` — **the path carries the feature id** (DEC-130) | the owning agent |
| `notes/` | **Project-scoped** durable artifacts only (cross-feature research, docs sweeps). Anything belonging to a FEAT lives in that feature's `notes/` | the owning agent |
| `logs/<date>.md` | Append-only **cross-flow** stream: flow started, escalation, briefing. Never loaded at spawn | **main session only** |
| `features/<FEAT>/STATE.md` | That flow's live pointer: `## Current` + `## Open Questions`. **No history** — `logs/` is for that. One per feature, so concurrent flows never share a writer | that feature's **orchestrator** |
| `features/<FEAT>/feature.yaml` | Execution facts: branch, PR, `review_sha`, `cycles_used`/`max_total_cycles`, run list | that feature's **orchestrator** |
| `features/<FEAT>/runs/<run>/` | One team run: `state.yaml` + the lead's `digest.md` | that run's **lead** |
| `teams/*.yaml` | *Optional.* Project overrides for shipped team definitions | you |
| `.omp/agents/*.md` | Canonical role definitions. **Deliberately unowned by every agent** — editing the organization is self-modification, so agents raise `open_questions` instead. | **you** (main session) |

**Committed**, except `features/*/runs/**`, which is ephemeral scratch — and must be git-ignored, or
a dirty tree deadlocks the next run.

## Who writes what

Every path above has exactly one writer, and `check-domain.py` enforces it on every `Write`/`Edit`.
An agent that tries to write outside its `domain` is **blocked** and told which paths are its own.

Three rules explain most of the table:

- **Members write their own artifacts, never a run directory.** The run dir belongs to the lead. A
  member's outputs go to its own namespaced path — which is also what makes parallel steps safe.
- **`## Approval` is written by the main session.** `pm` owns `BRIEF.md` and `PLAN.md` but never
  signs them, because signing means asking you and only the main session has a user channel.
- **An orchestrator owns its whole feature** — that flow's `STATE.md`, `feature.yaml`, and the
  feature-wide cycle budget. Leads own one run each; the main session owns only the
  cross-flow log and your approvals.

## How work flows

A **team** is a lead plus its members. The lead conducts a DAG of steps, dispatching only its own
squad (`harness-team` skill; authored in `.claude/skills/harness/teams/*.yaml` and exposed to OMP through `.agents/skills`).

```
main session ──▶ orchestrator ──▶ lead ──▶ members
     (user channel)   (one per flow)                depth 3: members are always leaves
```

Handoff is **by file path, never by conversation**. Each agent writes an artifact, then returns one
typed object through YieldTool — never YAML/JSON text:

```js
yield({data: {
  "VERDICT": "PASS",
  "DIGEST": {
    "headline": "CLI reference now documents the --dry-run flag",
    "docs_updated": ["docs/cli.md"],
    "gaps": [],
    "stale_found": [],
    "open_questions": [],
    "files_touched": ["docs/cli.md"],
    "expertise_update": []
  },
  "artifact": "<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/notes/receipt-harness-documentor-<runid>.md"
}})
```

That example is the complete `harness-documentor` shape. Each persona's exact closed schema is
`.agents/skills/harness/bin/digest-schemas/harness-<persona>.json`, with shared definitions in
`common.json`. Every declared property is required, including conditionally meaningful fields; use
`none` or `[]` when the schema calls for no value, never null or omission. Minimal list items are
closed too.

The task hook refuses dispatcher-supplied `outputSchema` or `schemaMode`, then injects the target
persona's canonical schema in strict mode. YieldTool validates `data` as the object; malformed data
returns an actionable retryable tool error to the same job. There is no prose parser, last-message
fallback, host-synthesized digest, or compatibility alias.

Members yield objects to their lead. A lead first writes the human team report at
`<run>/digest.md`, then yields its object. `validate-digest.py` alone appends the validated object as
fenced YAML; an identical final record causes no write, and a changed one appends rather than
replaces history. A missing, unsafe, non-regular, outside-checkout, unreadable or unwritable target
refuses the yield until the named path problem is fixed.

This digest path is OMP-native. Claude Code has no supported YieldTool-object digest path and no
`SubagentStop` compatibility route is retained (DEC-237).

**Cross-squad work is not one team.** A lead cannot dispatch another squad's members or spawn a peer
lead, so multi-squad lifecycles are sequenced by the orchestrator as one run per squad.

## Getting started

A repository is not onboarded when it is absent from `.harness/factory/fleet.yaml`, when its own
`harness.json` is not readable at its default branch, or when it has no central tree at
`<control-plane>/.harness/<segment>/` — run the `harness-add-repo` skill. If this checkout itself is
unconfigured, run `harness-init` first; a `schema_version` gap calls for `harness-init --upgrade`.
An empty `features/` directory is a normal state, not a sign of missing onboarding.

Run `.agents/skills/harness/bin/check-state.py` any time; it checks invariants that fail silently,
including required lifecycle integration, approvals, and tasks missing `change_type`. Mid-edit,
`--changed` runs only the invariants whose declared inputs the dirty tree touches — and every
`plan-merge.py` and `feature_json_write` write already runs it for you, on stderr; the pre-commit
hook and CI run the full table, never `--changed`. `--list` prints the table, `--only INV-N` one row.

> **Schemas are authored in `.claude/skills/harness/templates/`** and exposed to OMP through
> `.agents/skills` — `BRIEF.md`, `plan.yaml`, `STATE.md`,
> `DESIGN.md`, `harness.json`, `team-config.yaml`. Copy from there, not from examples in prose:
> an out-of-date template silently skips required gates.
