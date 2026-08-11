# `.harness/` — the project's state

Everything the harness knows about *this* project. Plain files, read and written by agents at spawn
time — no engine, no build step, no database.

**Written by `/harness-init`, the onboarding interview.** It writes this directory once, at
onboarding; everything after that is written by the agents that own each path (see the table below).

## Layout

| Path | What it is | Written by |
|---|---|---|
| `BRIEF.md` | The **goal of record**: Goal, `REQ-NN`, Constraints, `SC-NN` (each with a `verify:` method), `## Approval`. Stable across the project. | `pm` drafts · **you** approve |
| `PLAN.md` | Active plan: `## Decisions` (`D-NN`), `## Approval`, `## Features` (`FEAT-NN`), `## Tasks` (`T-NN`, each with `change_type:`) | `pm` — except `## Approval` |
| `DESIGN.md` | The visual design contract: palette in both themes, type scale, spacing, component direction | `visual-designer` |
| `team-config.yaml` | **The org as data** — membership, `consult-when` routing, and each agent's writable `domain`. Read by `check-domain.sh` on every write | `/harness-init`, seeded from detection |
| `harness.json` | `test_matrix`, `test_kinds`, `gates`, `budgets`, `log_retention_days` | `/harness-init` · `dev-ops` fills `test_kinds` |
| `expertise/<agent>.md` | Per-agent durable knowledge, injected at every spawn by the `SubagentStart` hook | each agent, its own file only |
| `efforts/<slug>/` | A pre-feature **wayfinding map** (`MAP.md` + `tickets/`): a vague idea being taken to plannable clarity across sittings. Local markdown, never the issue tracker (DEC-165). Retired or archived once its effort hands off to `/harness-plan` | the **main session** |
| `notes/grilling-*.md` | A single-sitting dialog-to-clarity record: destination, settled decisions, fog, out-of-scope, facts verified — pm's BRIEF input (DEC-164) | the **main session** |
| `features/<FEAT>/notes/` | That feature's durable artifacts: `research-*`, `review-<persona>-c<cycle>.md`, `qa-*`, `answers-<runid>.md`, `ship-review-<runid>.md`, `uat.md`, `mockups/`, `prototypes/` — **the path carries the feature id** (DEC-130) | the owning agent |
| `codebase/` | **The codebase map** (DEC-137) — per-project structural knowledge: capped `INDEX.md` (injected at every spawn), `architecture.md`, `domains/`, and one lens per authoring role. Anchored claims, per-section provenance, ship-refreshed | each view's **authoring role**; skeleton documentor |
| `notes/` | **Project-scoped** durable artifacts only (cross-feature research, docs sweeps). Anything belonging to a FEAT lives in that feature's `notes/` | the owning agent |
| `logs/<date>.md` | Append-only **cross-flow** stream: flow started, escalation, briefing. Never loaded at spawn | **main session only** |
| `features/<FEAT>/STATE.md` | That flow's live pointer: `## Current` + `## Open Questions`. **No history** — `logs/` is for that. One per feature, so concurrent flows never share a writer | that feature's **orchestrator** |
| `features/<FEAT>/feature.yaml` | Execution facts: branch, PR, `review_sha`, `cycles_used`/`max_total_cycles`, run list | that feature's **orchestrator** |
| `features/<FEAT>/runs/<run>/` | One team run: `state.yaml` + the lead's `digest.md` | that run's **lead** |
| `teams/*.yaml` | *Optional.* Project overrides for shipped team definitions | you |
| `.claude/agents/*.md` | The org's own definitions. **Deliberately unowned by every agent** — an agent editing these is self-modification, so changing what the org *is* stays with the tier that has a user channel. Agents raise `open_questions` instead | **you** (main session) |

**Committed**, except `features/*/runs/**`, which is ephemeral scratch — and must be git-ignored, or
a dirty tree deadlocks the next run.

## Who writes what

Every path above has exactly one writer, and `check-domain.sh` enforces it on every `Write`/`Edit`.
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
squad (`harness-team` skill; definitions in `.claude/skills/harness/teams/*.yaml`).

```
main session ──▶ orchestrator ──▶ lead ──▶ members
     (user channel)   (one per flow)                depth 3: members are always leaves
```

Handoff is **by file path, never by conversation**. Each agent writes an artifact and returns a
compact **digest**:

```
VERDICT: PASS | FAIL | BLOCKED | ESCALATE
DIGEST:
  headline: <one line, conclusion first>
  files_touched: [...]        # doers
  open_questions: [...]       # non-empty routes to the user
artifact: <path>
```

Members report digests to their lead; the lead **collates and assesses** them — including sending
work back — into a **team digest** at `<run>/digest.md`; the orchestrator assesses across teams,
routes questions between leads, delegates another cycle, or calls a briefing with you. Same artifact
type at every tier. `bin/validate-digest.py` checks the shape, because a reader normalizes drift
charitably and then one routing decision quietly goes wrong.

**Cross-squad work is not one team.** A lead cannot dispatch another squad's members or spawn a peer
lead, so multi-squad lifecycles are sequenced by the orchestrator as one run per squad.

## Getting started

`BRIEF.md` missing means the project is not onboarded — run `/harness-init`.

Run `bin/check-state.sh` any time; it checks the invariants that fail silently, including the five
`settings.json` prerequisites, an unapproved brief, and tasks missing `change_type`.

> **Schemas live in `.claude/skills/harness/templates/`** — `BRIEF.md`, `PLAN.md`, `STATE.md`,
> `DESIGN.md`, `harness.json`, `team-config.yaml`. Copy from there, not from examples in prose: an
> out-of-date template in a README is how a task ends up without a `change_type` and silently skips
> the test gate.
