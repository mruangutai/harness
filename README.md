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

## Canonical surfaces

| Surface | Location |
| --- | --- |
| Shared project guidance | `AGENTS.md` |
| OMP configuration | `.omp/config.yml` |
| Provider mappings | `.omp/providers/*.yml` |
| Canonical agents | `.omp/agents/harness-*.md` |
| OMP lifecycle enforcement | `.omp/extensions/harness-hooks.ts` |
| Canonical skills and utilities | `.agents/skills/harness-*/` |
| Project state and durable artifacts | `.harness/` |
| Organization, routing, and write domains | `.harness/team-config.yaml` |

`CLAUDE.md`, `.claude/agents/`, `.claude/skills`, and `.claude/settings.json` are Claude Code compatibility adapters. `sync-agent-adapters.py` generates Claude role files from the OMP definitions, and `.claude/skills` points to the canonical Agent Skills tree.

OMP project configuration disables Claude-format discovery. This proves the Harness runtime does not depend on `.claude/**` even though Claude Code remains supported.

## Guardrails

The native OMP extension preserves the Harness enforcement contracts:

- inject tiered Expertise and the codebase index before a task agent starts;
- deny out-of-domain writes;
- deny reviewer writes through Bash;
- require work-tracked branch names;
- prevent per-dispatch model overrides;
- report post-write state-shape failures;
- reject malformed task-agent digests before accepting a handoff.

Policy remains in the tested shell/Python modules under `.agents/skills/harness/bin/`; the TypeScript extension adapts OMP lifecycle events and does not duplicate policy.

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

To add a skill, create `.agents/skills/harness-<name>/SKILL.md` and add its name to the applicable agents' `autoloadSkills` lists.

## Factory repositories

The Harness repository holds the organization and skills. Product repositories hold their own `.harness/` state. Add a repository to `.harness/factory/fleet.yaml`; the factory materializes its checkout under the declared `workspace_root`, and `/harness-init` creates that repository's state.
