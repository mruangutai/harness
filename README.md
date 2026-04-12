# Harness

A unified Claude Code workflow that brings engineering discipline to GSD-based projects. It injects TDD enforcement, spec-driven planning, systematic debugging, and role-based review gates into the GSD workflow — without modifying GSD itself.

**Built on:** GSD (backbone) + Superpowers (TDD discipline) + gstack (role personas)

---

## For Users

### What you get

Once harness is active in a project, GSD subagents automatically follow engineering discipline:

| GSD Agent | Harness Rules Active |
|-----------|---------------------|
| `gsd-executor` | TDD Iron Law, zero-placeholder gate, exemption checks |
| `gsd-planner` | Spec-driven planning, task completeness requirements, CONTEXT.md as single spec |
| `gsd-verifier` | TDD compliance check, spec traceability check, gate completion check |
| `gsd-debugger` | 4-phase RCA protocol (Observe → Hypothesize → Test → Fix), 3-failure cap |

You also get role-based reviewers that fire at key workflow points (see [Role Gates](#role-gates) below).

### Prerequisites

- [GSD](https://github.com/gsd-build/get-shit-done) installed globally
- Claude Code CLI

### New projects — automatic

Run `/gsd-new-project` as normal. If harness has been deployed on your machine, it activates automatically:

1. Harness skills are copied to your project
2. `agent_skills` entries are added to `.planning/config.json`
3. Your project is registered for future harness updates

Nothing extra to run. Harness is active from the first `/gsd-execute-phase`.

### Existing projects — ask the maintainer

If your project predates harness, ask the harness maintainer to run:

```
/harness-deploy /absolute/path/to/your-project
```

This copies skills, configures `config.json`, and registers your project.

### Role gates

Role-based reviewers challenge assumptions at key workflow points. They are available as agents:

| Agent | Fires when | What it does |
|-------|-----------|--------------|
| `harness-eng-reviewer` | Before + after `/gsd-discuss-phase` on architectural phases | Pre-discuss: surfaces architecture questions. Post-discuss: reviews decisions in CONTEXT.md |
| `harness-ceo-reviewer` | At `/gsd-new-project` or scope change | Challenges scope, validates fit, asks forcing questions |
| `harness-code-reviewer` | After `/gsd-execute-phase` on implementation plans | Two-stage: spec compliance then code quality |
| `harness-qa-reviewer` | Before `/gsd-ship` | Generates test cases from CONTEXT.md, verifies against source |
| `harness-security-reviewer` | Before `/gsd-ship` | OWASP Top 10 + STRIDE threat modeling |

**Current status:** Trigger instructions are in your project's `CLAUDE.md` (Harness section). Global automatic triggering across all projects is in progress — see [CLAUDE.md](./CLAUDE.md) for the current trigger lines.

---

## For Maintainers

### Architecture

```
harness repo (.claude/skills/harness/)   ← development copy (git-tracked)
        │
        │  /harness-deploy
        ▼
~/.claude/skills/harness/               ← global distribution point (survives /gsd-update)
        │
        │  /harness-deploy <path>  or  auto on /gsd-new-project
        ▼
{project}/.claude/skills/harness/       ← per-project instance
{project}/.planning/config.json         ← agent_skills entries pointing to above
~/.gsd/harness-registry.json            ← registry of enrolled projects
```

The harness repo is where you develop. `~/.claude/skills/harness/` is the distribution point. Projects get a copy via deploy or auto-activation — they never pull from the harness repo directly.

### Why this survives `/gsd-update`

`/gsd-update` replaces `~/.claude/get-shit-done/`, `~/.claude/commands/gsd/`, and `~/.claude/agents/gsd-*.md`. Everything harness uses is outside those paths:

| Harness file | Why it's safe |
|-------------|---------------|
| `~/.claude/skills/harness/` | Not in `get-shit-done/` |
| `~/.claude/agents/harness-*.md` | Not `gsd-` prefixed |
| `~/.claude/CLAUDE.md` | Never touched by GSD update |
| `~/.gsd/harness-registry.json` | Not in `get-shit-done/` |
| `{project}/.claude/`, `.planning/` | Project-level, not global |

### Repository structure

```
.claude/
  agents/                    ← role gate agent definitions
    harness-eng-reviewer.md
    harness-ceo-reviewer.md
    harness-code-reviewer.md
    harness-qa-reviewer.md
    harness-security-reviewer.md
  commands/
    harness-deploy.md        ← /harness-deploy slash command
  skills/harness/
    SKILL.md                 ← routing index (do not load subdirs directly)
    tdd/
      SKILL.md               ← injected into gsd-executor
    rules/
      SKILL.md               ← injected into gsd-verifier, gsd-planner, gsd-debugger
      tdd-enforcement.md
      spec-driven.md
      systematic-debugging.md
      code-review.md
      verification-rules.md
    personas/
      SKILL.md
      eng-review.md
      ceo-review.md
      qa-gate.md
.planning/
  harness.json               ← gate toggles, role trigger config
  config.json                ← agent_skills injection paths (project-level)
```

### Deploying skill updates

After changing anything in `.claude/skills/harness/`:

```
/harness-deploy
```

This:
1. Copies `.claude/skills/harness/` → `~/.claude/skills/harness/`
2. Regenerates `~/.claude/skills/harness/manifest.json` from `config.json` agent_skills
3. Pushes updated skills to all registered projects

### Enrolling an existing project

For any GSD project that predates harness:

```
/harness-deploy /absolute/path/to/project
```

This copies skills, merges `agent_skills` into `config.json`, and registers the project. Future `/harness-deploy` (no args) will include it automatically.

### Adding a new skill

1. Create the skill file(s) under `.claude/skills/harness/`
2. Add a `SKILL.md` index if creating a new subdirectory
3. Add the agent type → skill path mapping to `agent_skills` in `.planning/config.json`
4. Run `/harness-deploy` — manifest is regenerated and all registered projects receive the update

### The manifest

`~/.claude/skills/harness/manifest.json` is the single source of truth for which `agent_skills` entries get written to enrolled project `config.json` files. It is regenerated from `config.json` on every `/harness-deploy` — never edit it directly.

### Auto-activation trigger

`~/.claude/CLAUDE.md` contains a trigger that fires after `/gsd-new-project` completes. It reads the manifest, copies skills to the new project, merges `config.json`, and registers the project. This is the zero-setup path for all new projects going forward.

### Role gates — global integration (in progress)

Role gate agents currently live in `.claude/agents/` (harness repo only) and trigger instructions are in the harness project's `CLAUDE.md`. The next planned improvement:

- Move agents to `~/.claude/agents/` (globally available in all project sessions)
- Add trigger instructions to `~/.claude/CLAUDE.md` (apply to all GSD projects)

Until that ships, role gates work in the harness project automatically and in other projects via `CLAUDE.md` instructions added during enrollment.

### Key constraint: agent_skills paths are project-relative

GSD's `validatePath` rejects absolute paths for `agent_skills`. Skills must be under the project root. This is why each project needs its own `.claude/skills/harness/` copy rather than referencing `~/.claude/skills/harness/` directly. The deploy mechanism handles this — you never manage per-project skill files manually.
