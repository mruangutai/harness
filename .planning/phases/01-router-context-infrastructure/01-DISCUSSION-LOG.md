# Phase 1: Router & Context Infrastructure - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-04
**Phase:** 01-router-context-infrastructure
**Areas discussed:** File Organization, Routing Design, Config Integration, GSD Compatibility

---

## File Organization

| Option | Description | Selected |
|--------|-------------|----------|
| Nested subdirs | .claude/skills/harness/ with subdirs (rules/, personas/, tdd/) + SKILL.md per subdir | ✓ |
| Flat directory | .claude/skills/harness/ with all files flat + one SKILL.md | |
| Hybrid | Flat rule files + agent_skills config for injection | |

**User's choice:** Nested subdirs — cleaner separation.

**Follow-up — Loading mechanism:**

| Option | Description | Selected |
|--------|-------------|----------|
| Passive discovery | GSD subagents auto-scan .claude/skills/*/SKILL.md | |
| agent_skills config | Precise per-agent-type injection via config | ✓ |
| Both (passive + config) | Auto-discovery baseline + config precision layer | |

**User's choice:** agent_skills config only — passive discovery is wasteful.

**Notes:** User asked how GSD agent_skills inherits/uses skills from nested subdirs. Clarified that file structure (Layer 1) and loading mechanism (Layer 2) are independent decisions, not competing options. User also asked about gstack roles that can't be used via agent_skills.

---

## Routing Design

**Gate role mechanism:**

| Option | Description | Selected |
|--------|-------------|----------|
| Custom agent definitions | Fresh context per role, Task() at transitions, matches GSD pattern | ✓ |
| Orchestrator-level skills | SKILL.md read by main session, lighter but weaker isolation | |
| Defer to Phase 3 | Lock agent_skills for Phase 1, decide gates later | |

**User's choice:** Custom agents — strong persona isolation, parallel execution.

**Gate trigger mechanism:**

| Option | Description | Selected |
|--------|-------------|----------|
| CLAUDE.md instructions | Project CLAUDE.md tells orchestrator to check gates at transitions | ✓ |
| Wrapper workflows | New /harness: slash commands wrapping GSD | |
| Explore in Phase 3 | Defer trigger mechanism | |

**User's choice:** CLAUDE.md instructions — simplest, no new commands.

**Notes:** User asked whether wrapper workflows or GSD hooks would break GSD compatibility. Confirmed none of the options break compatibility — harness adds alongside GSD, never modifies it. User also asked about GSD hooks — confirmed GSD has no phase-transition hook system (just a simple settings namespace).

---

## Config Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Separate harness.json | Sidecar config, zero GSD patching, survives updates | ✓ |
| Extend config.json | Patch GSD's VALID_CONFIG_KEYS, single file | |
| Sidecar now, merge later | harness.json for v1, revisit if GSD adds extension support | |

**User's choice:** Separate harness.json — prioritized GSD update safety.

---

## GSD Compatibility

| Option | Description | Selected |
|--------|-------------|----------|
| Structural + CLI check | Automated diff audit + gsd-tools CLI introspection | ✓ |
| Manual smoke test | Run GSD commands, observe behavior | |
| Defer to Phase 4 | Trust architecture, let real-project validation prove it | |

**User's choice:** Structural + CLI check — automated verification at install time, Phase 4 for full proof.

---

## Claude's Discretion

- Directory and file naming within harness subdirs
- SKILL.md content structure
- harness.json schema field names
- Structural diff audit implementation

## Deferred Ideas

- Designer role gate — explore in Phase 3
- DevEx Lead role gate — explore in Phase 3
- GSD hooks/plugin system — if GSD adds this, migrate gate triggers
- Config migration to GSD namespace — if GSD adds extension support
