# Phase 1: Router & Context Infrastructure - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Create the harness routing layer — CLAUDE.md harness section, skill files, harness.json config, agent_skills registration — that integrates with GSD's existing orchestration without breaking it. This phase delivers the infrastructure that Phase 2-4 build on.

</domain>

<decisions>
## Implementation Decisions

### File Organization
- **D-01:** Nested subdirectories in `.claude/skills/harness/` — `rules/`, `personas/`, `tdd/` — each with its own SKILL.md entry point. Clean namespace separation by domain.
- **D-02:** No passive skill discovery. Use `agent_skills` config in harness.json for precise injection into specific GSD subagent types (e.g., TDD rules → gsd-executor only, verification rules → gsd-verifier only).

### Routing Design
- **D-03:** Two-layer routing hybrid: `agent_skills` config handles static per-agent-type injection (TDD into executor, verification into verifier). CLAUDE.md instructions handle phase-gate triggers (CEO review before plan-phase, etc.).
- **D-04:** Gate roles (CEO, Eng Manager, Designer, DevEx Lead, QA, Security) are implemented as custom agent definitions — `.md` files spawned as Task() at phase transitions. Each gets a fresh 200K context window with precisely scoped inputs.
- **D-05:** CLAUDE.md harness section stays lean (~50 tokens) — declares the harness exists and points to the skill directory. Uses its own marker block (`<!-- GSD:harness-start -->`) to survive GSD's `generate-claude-md` regeneration.
- **D-06:** Gate triggers are expressed as CLAUDE.md instructions (e.g., "Before running /gsd:plan-phase, spawn harness-ceo-reviewer if scope-changing phase"). No wrapper workflows, no new slash commands.

### Config Integration
- **D-07:** Separate `.planning/harness.json` sidecar config file. Zero GSD patching, survives any GSD update, harness fully owns its schema.
- **D-08:** Subagents receive harness.json via `<files_to_read>` blocks in their dispatch instructions. No dependency on GSD's `config-get`/`config-set` CLI.
- **D-09:** harness.json schema includes: gate toggles (TDD enforcement on/off, role review triggers, bypass protection), agent_skills mappings (which skills → which GSD agent types), and TDD-exempt plan types (config, docs, scaffolding).

### GSD Compatibility
- **D-10:** Verification via structural diff audit (no harness files overlap with GSD files) + gsd-tools CLI introspection (GSD commands return expected JSON with harness installed).
- **D-11:** Harness never modifies GSD files at `~/.claude/get-shit-done/`. GSD doesn't know the harness exists. The harness works alongside GSD.
- **D-12:** Phase 4 real-project validation is the definitive end-to-end proof. Phase 1 verification is install-time confidence only.

### Claude's Discretion
- Directory naming within `.claude/skills/harness/` subdirs (exact file names for rule files)
- SKILL.md content structure and format within each subdir
- Exact harness.json schema field names (as long as they cover gates, agent_skills mappings, and TDD exemptions)
- Structural diff audit implementation details (bash script approach)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### GSD Architecture
- `~/.claude/get-shit-done/bin/lib/config.cjs` — GSD config schema, VALID_CONFIG_KEYS allowlist, agent_skills structure
- `~/.claude/get-shit-done/workflows/execute-phase.md` — How GSD executor subagents are dispatched, `<execution_context>` injection mechanism
- `~/.claude/get-shit-done/workflows/discuss-phase.md` — Phase transition points where gate roles would trigger

### Research Artifacts
- `.planning/research/ARCHITECTURE.md` — Route-not-stack pattern, seven integration seams, component boundaries
- `.planning/research/FEATURES.md` — Feature landscape, role mapping table, TDD enforcement detail
- `.planning/research/PITFALLS.md` — Context budget death, governance conflicts, TDD bypass risks
- `.planning/research/SUMMARY.md` — Synthesized findings and phase ordering rationale

### Prior Art
- `council/unified-harness-gsd-gstack-superpowers/shared_reasoning.md` — Council analysis of integration approach

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- GSD's `generate-claude-md` command — produces marker-bounded sections in CLAUDE.md. Harness section uses its own marker to survive regeneration.
- GSD's `agent_skills` config field — already supports per-agent-type skill path registration via `buildAgentSkillsBlock()` in config.cjs.
- GSD's `<files_to_read>` block pattern — standard mechanism for injecting file paths into subagent prompts.

### Established Patterns
- SKILL.md per skill directory — Anthropic's agent-skills convention, used by GSD executor's `.claude/skills/` scan.
- YAML frontmatter `.md` files for agent definitions — GSD's pattern for all 19 agent types.
- `Task()` dispatch with `subagent_type` parameter — how GSD spawns typed subagents.

### Integration Points
- Project CLAUDE.md — harness adds a marker-bounded section with gate trigger instructions.
- `.planning/harness.json` — new sidecar config file read by subagents.
- `.claude/skills/harness/` — new directory tree for harness skill files.

</code_context>

<specifics>
## Specific Ideas

- User wants to explore Designer and DevEx Lead roles (from gstack) in addition to the already-scoped CEO, Architect, QA, Security roles — noted for Phase 3 scope expansion.
- User prefers precise control over which subagents get which skills (agent_skills config) over passive discovery (every subagent reads everything).
- User prioritized GSD update safety — chose separate harness.json over patching GSD's config.cjs.

</specifics>

<deferred>
## Deferred Ideas

- **Designer role gate** — Visual/UX quality audit after UI implementation. Explore in Phase 3 alongside other role gates.
- **DevEx Lead role gate** — Developer experience review for API/SDK projects. Explore in Phase 3.
- **GSD hooks/plugin system** — GSD doesn't currently have phase-transition hooks. If GSD adds this capability, the harness could migrate gate triggers from CLAUDE.md instructions to hooks.
- **Config migration to GSD namespace** — If GSD adds third-party extension support, migrate from harness.json sidecar to `harness.*` namespace in config.json.

</deferred>

---

*Phase: 01-router-context-infrastructure*
*Context gathered: 2026-04-04*
