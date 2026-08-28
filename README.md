# Harness

Harness is a provider-neutral OMP agent organization for taking software work from product definition through architecture, implementation, independent validation, and review.

The organization, skills, artifacts, and guardrails stay constant while OMP routes its capability roles to OpenAI, Anthropic, or another configured provider.

## What runs

```text
main session (user channel)
  → harness-orchestrator
      → harness-product-lead
          → product specialists
      → harness-eng-lead
          → engineering specialists
      → harness-validator-lead
          → QA and independent reviewers
```

All 16 roles are native OMP task agents. Spawn allowlists encode the hierarchy and members are leaves.

## Provider selection

Run OMP with an explicit provider overlay:

```bash
# OpenAI Codex
omp --config .omp/providers/openai.yml

# Anthropic Claude
omp --config .omp/providers/anthropic.yml
```

Canonical agents select provider-neutral capability aliases:

```yaml
model: "@strong"
```

The overlays map `deep`, `strong`, `standard`, and `review` to concrete models. Switching providers changes configuration only; it does not change prompts, tools, skills, spawning, hooks, artifacts, or digest schemas.

## Long-running workflow

Use the same Harness instruction under either overlay. Only the concrete models selected by the
overlay change.

```text
main session
  → one phase-scoped harness-orchestrator
      → one squad lead
          → one ready wave of members
```

Each governed task prompt starts with `HARNESS-FEATURE: FEAT-NN-slug` (or `BUG-NN-slug`). The
main session dispatches the orchestrator in the background, receives agent/job identity
immediately, and ends its turn; OMP injects the orchestrator's terminal result back into that
session.

Inside the Harness tree, every lead and member is declared `blocking: true`. An orchestrator's
task call stays inside OMP until its lead is terminal, and a lead's ready-wave call stays inside OMP
until its members are terminal. The parent model is inactive at that tool boundary: it does not
poll Agent Hub, call `hub wait`, sleep, or emit keepalives. Agent Hub still shows the full live
lineage. When the blocking tool result returns, the parent re-reads its checkpoint, verifies the
cited artifact, and advances one durable transition. A phase boundary starts a fresh orchestrator.

The OMP process is the supervisor. Running jobs do not survive that process exiting unless the OMP
process itself is kept alive by an external service supervisor. Project configuration enables async
delivery and removes the task wall-clock limit, while OMP's request budget remains the independent
runaway-turn safety bound.

## Recovery after terminal loss

Restart with the same provider overlay and resume the persisted session:

```bash
# OpenAI
omp --config .omp/providers/openai.yml --resume

# Anthropic
omp --config .omp/providers/anthropic.yml --resume
```

Then:

1. Inspect Agent Hub and `history://` first; do not revive or kill an agent merely because it is
   parked.
2. Resume the Harness feature named by `HARNESS-FEATURE:`.
3. Reconcile in this order: the feature/run checkpoint on disk, a persisted `agent://` or
   `history://` result, then landed commits.
4. A claim owned by the dead OMP PID is stale immediately. Release only that feature's targeted
   claim.
5. If the checkpoint has a valid terminal artifact, collect it. If it has no terminal artifact and
   the regular agent session is recoverable, revive that agent. Otherwise re-dispatch only the one
   unfinished checkpointed step.

Never infer PASS from a transcript, a claim file, or a card on GitHub. A repeated async delivery or
resume of an already-terminal step is an idempotent no-op.

## GitHub lifecycle

The GitHub mirror follows Harness state; it is not a heartbeat channel:

1. The signed plan opens one parent issue and one sub-issue per `T-NN`.
2. Write the task status to `plan.yaml`, then `gh-sync.py start-task` moves that task to
   `Building`.
3. Validation entry writes `Review` for the parent and task cards.
4. User-accepted ship writes eligible task, source, and parent cards to `Done`; GitHub's
   `Auto-close issue` workflow closes them.
5. A card with an open child is held open and the blocking child is named.

The orchestrator owns `open`, team-task `start-task`, and its phase `status`. The main session owns
main-session-direct transitions, ship acceptance, `ship`, `record-pr`, `backlog`, and `abandon`.
Write `plan.yaml`/`feature.json` first, then run the owned mirror command in the same act. On wake or
recovery, read those files and their stored GitHub receipts before deciding whether a transition is
still due; do not poll GitHub while a child runs and do not create replacement issues. Direct
`gh issue close` commands are blocked under OMP; `gh-sync.py abandon` is the only direct-close path.

## Canonical surfaces

| Surface | Location |
| --- | --- |
| Shared project guidance | `AGENTS.md` |
| OMP configuration | `.omp/config.yml` |
| Provider mappings | `.omp/providers/*.yml` |
| Canonical agents | `.omp/agents/harness-*.md` |
| OMP lifecycle enforcement | `.omp/extensions/harness-hooks.ts` |
| Authored skills and utilities | `.claude/skills/harness-*/` |
| Project state and durable artifacts | `.harness/` |
| Organization, routing, and write domains | `.harness/team-config.yaml` |

`.claude/skills/` is the single authored skill tree used directly by Claude Code. `.agents/skills` is a compatibility symlink to that tree, giving OMP the standard Agent Skills path without a second copy. `CLAUDE.md`, `.claude/agents/`, and `.claude/settings.json` remain Claude Code adapters; `sync-agent-adapters.py` generates Claude role files from the OMP definitions.

OMP project configuration disables Claude-format discovery. Skills remain available through `.agents/skills`, proving that OMP discovery does not depend on enabling the Claude provider even though the shared files are authored under `.claude/skills`.

## Guardrails

The native OMP extension preserves the Harness enforcement contracts:

- inject tiered Expertise and the codebase index before a task agent starts;
- deny out-of-domain writes;
- deny reviewer writes through Bash;
- require work-tracked branch names;
- prevent per-dispatch model overrides;
- report post-write state-shape failures;
- reject malformed task-agent digests before accepting a handoff.

Policy remains in the tested shell/Python modules authored under `.claude/skills/harness/bin/` and exposed to OMP through `.agents/skills/harness/bin/`; the TypeScript extension adapts OMP lifecycle events and does not duplicate policy.

## Expertise and artifacts

Expertise remains durable provider-neutral data:

```text
~/.harness/expertise/<agent>.md
.harness/expertise/<agent>.md
.harness/<repo>/expertise/<agent>.md
.harness/codebase/INDEX.md
```

Repository knowledge overrides project knowledge, which overrides global craft knowledge. Other briefs, plans, designs, run digests, review reports, UAT scripts, and handoffs remain under `.harness/` and are loaded by path only when needed.

See [`.harness/README.md`](.harness/README.md) for layout and writer ownership.

## Development

Harness develops itself only in a worktree under `.claude/worktrees/`. DEC-174 requires hooks, validators, gate scripts, and their tests to be changed directly rather than through the enforcement layer being replaced.

Run:

```bash
# Complete suite
bash .agents/skills/harness/bin/run-unit-tests.sh

# Provider-neutral surface and adapter drift
python3 .agents/skills/harness/bin/check-omp-port.py

# Project invariants
bash .agents/skills/harness/bin/check-state.sh
```

To change a role, edit `.omp/agents/<name>.md`, then regenerate and check Claude compatibility:

```bash
python3 .agents/skills/harness/bin/sync-agent-adapters.py --apply
python3 .agents/skills/harness/bin/sync-agent-adapters.py --check
```

To add a skill, create `.claude/skills/harness-<name>/SKILL.md` and add its name to the applicable agents' `autoloadSkills` lists. OMP discovers it through the `.agents/skills` symlink.

## Factory repositories

The Harness repository holds the organization and skills. Product repositories hold their own `.harness/` state. Add a repository to `.harness/factory/fleet.yaml`; the factory materializes its checkout under the declared `workspace_root`, and `/harness-init` creates that repository's state.
