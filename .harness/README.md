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

## Feature worktrees hold one feature (FEAT-1559)

The feature corpus is never materialised inside a worktree. A record-bearing linked checkout —
a feature worktree, a fleet planning worktree, or a validator pin under
`.claude/worktrees/.pins/` — is a git sparse checkout. It holds every tracked path outside
`.harness/*/features/`, plus `.harness/*/features/<id>/` for its ONE active feature.

- **Writes** go to the active feature only. **Reads** of any other feature go to the main corpus
  at the owner root: an ordinary absolute path under the main checkout, which is the injected
  control-plane root (`<HARNESS_CONTROL_PLANE_ROOT>/.harness/<segment>/features/<id>/…`; DEC-214
  as amended). A sibling worktree's in-progress feature is never read. Nothing symlinks or copies
  the corpus in, and nothing reads it out of git objects. Repo-wide readers (gates, audits,
  discovery) go through `bin/feature_corpus.py`. They refuse by name when the owner root or a
  tracked feature directory is missing, rather than auditing a smaller set.
- **A plain clone is unaffected.** It keeps the full corpus; `--verify` and `--repair` are no-ops
  there, as they are in the main checkout and in a probe worktree outside `.claude/worktrees/`.

**The active feature.** It is the one feature directory the checkout's record names, in that
record's own artifact segment, never the worktree's segment. Before any record exists, the id
comes from the checkout's identity: the worktree directory name, a `feat/<id>` branch, or the exact
pin name `<id>--<run>--<persona>`. The cone then excludes every `.harness/*/features` and includes
`.harness/*/features/<id>` in ALL segments, so the record can be created in whichever one it
belongs to. Two segments claiming the id, or an id that cannot be derived, refuses with cone (3)
and changes nothing. `feature-worktree.py` and `pinned-checkout.py` create checkouts exactly as
before.

**`worktree-state.py --verify | --repair [--checkout <path>] [--json]`.** Exits:

| Exit | Label | Meaning |
|---|---|---|
| 0 | — | layout correct (or a no-op checkout class) |
| 3 | cone | sparse cone missing or different from the derived one |
| 4 | skip-bits | skip-worktree bits disagree with the cone |
| 7 | materialisation | another feature's directory is on disk |
| 8 | dirty | content repair must not touch |
| 2 | — | the tool could not run |

`--verify` never changes a file, index or config byte. `--repair` classifies every status entry
before it mutates anything:

- **A** — outside the target cone, absent on disk, index entry equal to HEAD: the skip-worktree
  bit is set, and zero disk bytes are touched. An unstaged deletion inside a hidden feature is A by
  operator ruling.
- **B** — outside the cone, present and byte-identical to the index: removed.
- **C** — any content divergence:
  - a real edit;
  - a staged index entry unequal to HEAD, including a staged deletion;
  - a deletion inside the cone;
  - an untracked file in a hidden feature directory.

Any C anywhere, mixed with A or B or not, refuses with exit 8 and changes no file, index or config
byte. The class comes from content alone: no marker, note or record of where a file came from can
make a divergent file removable. Repair touches A and B only after the whole tree is classified,
and running it again changes nothing. On the owner it writes one thing, git's own:
`extensions.worktreeConfig = true`, which per-worktree sparse settings require.

**Hooks.** `post-checkout`, `post-merge` and `post-rewrite` in `.claude/skills/harness/hooks/` run
`--repair` on the checkout git just touched, whoever created it. So `git worktree add`,
`feature-worktree.py create` and `pinned-checkout.py add` all converge, as do a merge or rebase
that brings in a new top-level directory and an amend after an index rewrite.

- Each hook always exits 0, because a post hook cannot undo the operation, and reports a missing
  implementation, a failed repair or a dirty skip on stderr.
- `post-merge` then runs the terminal sweep as before.
- `core.hooksPath` is local configuration: a clone does not carry it, and the onboarding step and
  INV-31 remain how a checkout gets and keeps it.
- **`--verify` is the gate.** `check-state` runs it before any invariant in a record-bearing
  checkout. A quiet hook is never evidence of a valid layout.

**Dirty skips and recovery.** A class-C checkout stays on its old layout. After it merges or
rebases a post-FEAT-1559 `main`, `check-state` and the corpus gates refuse it for a structural
3, 4 or 7, although dirty (8) alone is only reported. To recover:

1. Preserve the work by committing it or stashing it, untracked files included.
2. Run `worktree-state.py --repair --checkout <path>`, then `--verify --checkout <path>`.
3. Rerun the refused audit or gate.
4. Restore the saved work and check again; if the structural debt returns, preserve and repair
   again.

Never force a repair, prune a worktree or erase work to get past a refusal.

**Conversion and evidence.** Existing clean worktrees are converted by one explicit `--repair`
pass that runs after FEAT-1559 is on `main` (#2101), so no worktree goes sparse while the
control-plane tools are still pre-1559 code. Dirty ones are skipped and listed. Its manifest and
migration record go in FEAT-1559's `notes/`. Until that pass, an existing worktree converts
itself through the hooks the next time it merges `main`.

- Savings are measured in files and feature directories, never as a `du` byte delta.
- Before-and-after comparisons pin immutable SHAs, never a moving ref.

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
