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

### Getting your repository into the harness

**Nothing is installed into your repository.** The harness lives in *this* repository and works on
yours by checking it out: add your repository to the fleet declaration
`.harness/factory/fleet.yaml`, and the factory clones it under that file's `workspace_root` the
first time it works there.

```yaml
# .harness/factory/fleet.yaml
repos:
  - name: your-org/your-repo
    default_branch: main
workspace_root: /Users/you/GitHub
```

That entry is the whole onboarding step. `/harness-init`, run inside the checkout, then writes the
project's own `.harness/` state — see `.harness/README.md`.

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

### Architecture — one copy, checked-out targets

```
this repository                          ← the harness itself: skills, agents, factory scripts
  .harness/factory/fleet.yaml            ← the declaration: repos, board, workspace_root
        │
        │  bin/factory_workspace.py — git clone https://github.com/<repo>.git
        ▼
<workspace_root>/<repo>/                 ← a checkout of a product repository
  .harness/                              ← that project's own state, written by /harness-init
```

There is **one** copy of the harness: this repository. A product repository never holds skills,
agents or a manifest of them; it holds only its own `.harness/` state. The four factory scripts in
`.claude/skills/harness/bin/` — `factory_claim.py`, `factory_decompose.py`, `factory_land.py` and
`factory_workspace.py` — take their repository, board and workspace path from `factory_config.py`
alongside them rather than parsing the fleet declaration themselves, and `factory_workspace.py` is
the one that materialises the checkout.

### Repository structure

```
.claude/
  agents/                    ← role gate agent definitions
    harness-eng-reviewer.md
    harness-ceo-reviewer.md
    harness-code-reviewer.md
    harness-qa-reviewer.md
    harness-security-reviewer.md
  commands/                  ← slash-command entry doors (`/harness`, `/harness-plan`, …)
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

### Changing the harness, and adding a skill

**There is no publish step.** Commit the change here and the next factory run uses it — the harness
is read from this checkout, so nothing has to be pushed anywhere and nothing can be out of date in a
product repository.

To add a skill: create `.claude/skills/harness-<name>/SKILL.md` — **flat**, exactly one level under
`.claude/skills/`, never nested — and add `harness-<name>` to the `skills:` list of each agent in
`.claude/agents/` that should preload it.

### Onboarding another repository

Add it to `repos:` in `.harness/factory/fleet.yaml` (see *Getting your repository into the harness*
above). There is no per-project skill tree to create, no registry to update, and nothing to keep in
sync afterwards.

### Role gates — global integration (in progress)

Role gate agents currently live in `.claude/agents/` (harness repo only) and trigger instructions are in the harness project's `CLAUDE.md`. The next planned improvement:

- Move agents to `~/.claude/agents/` (globally available in all project sessions)
- Add trigger instructions to `~/.claude/CLAUDE.md` (apply to all GSD projects)

Until that ships, role gates work in the harness project automatically and in other projects via
`CLAUDE.md` instructions.
