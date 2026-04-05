# Phase 1: Router & Context Infrastructure - Research

**Researched:** 2026-04-04
**Domain:** Claude Code workflow routing layer, config integration, selective skill loading
**Confidence:** HIGH

## Summary

Phase 1 creates the harness routing infrastructure: a lean CLAUDE.md section, `.claude/skills/harness/` directory tree, `.planning/harness.json` config sidecar, and `agent_skills` registration -- all without modifying any GSD files. The CTX requirements (CTX-01 through CTX-06) are existing GSD behaviors that must be verified as preserved after harness installation, not newly implemented.

The technical surface is well-understood. GSD's `generate-claude-md` manages five marker-bounded sections (`project`, `stack`, `conventions`, `architecture`, `workflow`) and preserves any content outside those markers. The harness adds a `<!-- GSD:harness-start -->` / `<!-- GSD:harness-end -->` block that survives regeneration. GSD's `agent_skills` config already supports per-agent-type skill path registration via `buildAgentSkillsBlock()` in `config.cjs`, accepting `agent_skills.<agent-type>` as a valid config key pattern. The harness uses this existing mechanism rather than inventing a new one.

The primary risk is scope creep into actual role/TDD content that belongs in Phase 2-3. Phase 1 delivers the infrastructure (directories, config schema, CLAUDE.md section, routing SKILL.md) and verifies GSD compatibility. It does NOT deliver absorbed gstack/superpowers content -- those are placeholder stubs that Phase 2-3 populate.

**Primary recommendation:** Build the directory tree and config schema first (pure infrastructure), then add the CLAUDE.md section and routing SKILL.md (behavioral layer), then verify GSD compatibility last (validation layer). Three waves, clean dependency chain.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Nested subdirectories in `.claude/skills/harness/` -- `rules/`, `personas/`, `tdd/` -- each with its own SKILL.md entry point. Clean namespace separation by domain.
- **D-02:** No passive skill discovery. Use `agent_skills` config in harness.json for precise injection into specific GSD subagent types (e.g., TDD rules -> gsd-executor only, verification rules -> gsd-verifier only).
- **D-03:** Two-layer routing hybrid: `agent_skills` config handles static per-agent-type injection (TDD into executor, verification into verifier). CLAUDE.md instructions handle phase-gate triggers (CEO review before plan-phase, etc.).
- **D-04:** Gate roles (CEO, Eng Manager, Designer, DevEx Lead, QA, Security) are implemented as custom agent definitions -- `.md` files spawned as Task() at phase transitions. Each gets a fresh 200K context window with precisely scoped inputs.
- **D-05:** CLAUDE.md harness section stays lean (~50 tokens) -- declares the harness exists and points to the skill directory. Uses its own marker block (`<!-- GSD:harness-start -->`) to survive GSD's `generate-claude-md` regeneration.
- **D-06:** Gate triggers are expressed as CLAUDE.md instructions (e.g., "Before running /gsd:plan-phase, spawn harness-ceo-reviewer if scope-changing phase"). No wrapper workflows, no new slash commands.
- **D-07:** Separate `.planning/harness.json` sidecar config file. Zero GSD patching, survives any GSD update, harness fully owns its schema.
- **D-08:** Subagents receive harness.json via `<files_to_read>` blocks in their dispatch instructions. No dependency on GSD's `config-get`/`config-set` CLI.
- **D-09:** harness.json schema includes: gate toggles (TDD enforcement on/off, role review triggers, bypass protection), agent_skills mappings (which skills -> which GSD agent types), and TDD-exempt plan types (config, docs, scaffolding).
- **D-10:** Verification via structural diff audit (no harness files overlap with GSD files) + gsd-tools CLI introspection (GSD commands return expected JSON with harness installed).
- **D-11:** Harness never modifies GSD files at `~/.claude/get-shit-done/`. GSD doesn't know the harness exists. The harness works alongside GSD.
- **D-12:** Phase 4 real-project validation is the definitive end-to-end proof. Phase 1 verification is install-time confidence only.

### Claude's Discretion
- Directory naming within `.claude/skills/harness/` subdirs (exact file names for rule files)
- SKILL.md content structure and format within each subdir
- Exact harness.json schema field names (as long as they cover gates, agent_skills mappings, and TDD exemptions)
- Structural diff audit implementation details (bash script approach)

### Deferred Ideas (OUT OF SCOPE)
- Designer role gate -- Phase 3
- DevEx Lead role gate -- Phase 3
- GSD hooks/plugin system -- future GSD capability
- Config migration to GSD namespace -- future if GSD adds extension support
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INFRA-01 | Harness CLAUDE.md router stays under 1,000 tokens and maps lifecycle phases to exclusive framework owners | GSD marker system preserves harness section; ~50 token budget per D-05; verified generate-claude-md only manages 5 named sections |
| INFRA-02 | Route-not-stack architecture -- each phase has exactly one framework authority | Routing SKILL.md maps lifecycle points to owners; ownership table in ARCHITECTURE.md research |
| INFRA-03 | Selective context loading -- skill files load on demand, never all simultaneously | agent_skills config provides per-agent-type injection; SKILL.md at harness root acts as passive-discovery guard |
| INFRA-04 | Config extension in `.planning/config.json` -- harness gates configured alongside GSD settings | Decision changed to harness.json sidecar (D-07); GSD's config.json agent_skills field used for skill path registration only |
| INFRA-05 | Copy-and-own pattern -- no live upstream dependencies | All harness files are self-contained in `.claude/skills/harness/` and `.claude/agents/`; no imports from gstack/superpowers repos |
| CTX-01 | Thin orchestrator with subagent isolation | Existing GSD behavior; verify preserved by running gsd-tools init after harness install |
| CTX-02 | Planning artifact chain (PROJECT > REQUIREMENTS > ROADMAP > STATE > PLAN) | Existing GSD behavior; verify artifact files still created/updated correctly |
| CTX-03 | Wave-based parallel execution | Existing GSD behavior; verify execute-phase still groups plans into dependency waves |
| CTX-04 | Discussion phase -- questions and assumptions modes | Existing GSD behavior; verify discuss-phase workflow unchanged |
| CTX-05 | Research gates -- block planning if research has unresolved questions | Existing GSD behavior; verify plan-phase still checks research status |
| CTX-06 | Scope drift detection | Existing GSD behavior; verify planner still flags dropped requirements |
</phase_requirements>

## Standard Stack

### Core

This phase produces markdown files and JSON config -- no libraries needed. The "stack" is GSD's existing infrastructure.

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| GSD gsd-tools.cjs | 1.30.0 | CLI for init, config, agent-skills commands | Already installed; provides agent_skills block builder, config CRUD, generate-claude-md |
| Claude Code SKILL.md convention | Current | Skill discovery and loading | Native to Claude Code; both gstack and superpowers use it |
| GSD marker system | Current | CLAUDE.md section management | `generate-claude-md` preserves content outside its 5 managed sections |
| JSON | N/A | harness.json config format | Matches GSD's config.json pattern; Claude reads JSON natively |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `gsd-tools.cjs agent-skills` | 1.30.0 | Generates `<agent_skills>` block for subagent dispatch | Called by execute-phase workflow to inject skill paths |
| `gsd-tools.cjs generate-claude-md` | 1.30.0 | Regenerates GSD sections in CLAUDE.md | Verify harness marker block survives regeneration |
| `gsd-tools.cjs init` | 1.30.0 | Returns phase metadata JSON | Verify JSON output unchanged with harness installed |

## Architecture Patterns

### Recommended Directory Structure

```
.claude/
  skills/
    harness/
      SKILL.md                    # Router: lifecycle -> owner mapping, selective loading guard
      rules/
        SKILL.md                  # Index for rules subdirectory
        tdd-enforcement.md        # Stub (Phase 2 populates)
        verification-rules.md     # Stub (Phase 2 populates)
        code-review.md            # Stub (Phase 2 populates)
        systematic-debugging.md   # Stub (Phase 2 populates)
      personas/
        SKILL.md                  # Index for personas subdirectory
        ceo-review.md             # Stub (Phase 3 populates)
        eng-review.md             # Stub (Phase 3 populates)
        qa-gate.md                # Stub (Phase 3 populates)
        cso-audit.md              # Stub (Phase 3 populates)
      tdd/
        SKILL.md                  # Index for TDD subdirectory
  agents/
    harness-ceo-reviewer.md       # Stub (Phase 3 populates)
    harness-eng-reviewer.md       # Stub (Phase 3 populates)
.planning/
  harness.json                    # Harness config sidecar
  config.json                     # GSD config (agent_skills entries added)
```

### Pattern 1: Marker-Bounded CLAUDE.md Section

**What:** The harness adds a `<!-- GSD:harness-start -->` / `<!-- GSD:harness-end -->` block to CLAUDE.md that GSD's `generate-claude-md` does not manage and therefore preserves intact.

**When to use:** Always. This is the harness's entry point into CLAUDE.md.

**How it works:** GSD's `cmdGenerateClaudeMd` in `profile-output.cjs` manages exactly 5 section names: `project`, `stack`, `conventions`, `architecture`, `workflow`. It finds sections by `<!-- GSD:{name}-start` prefix. A `harness` section with `<!-- GSD:harness-start -->` marker is NOT in the `MANAGED_SECTIONS` array, so `generate-claude-md` will never replace, remove, or modify it.

**Example:**
```markdown
<!-- GSD:harness-start -->
## Harness

Unified workflow harness active. Skills: `.claude/skills/harness/`
Config: `.planning/harness.json`
<!-- GSD:harness-end -->
```

**Token budget:** Target ~50 tokens per D-05. This section should only declare existence and point to the skill directory. All routing logic lives in the SKILL.md, not in CLAUDE.md.

### Pattern 2: Passive Discovery Guard via Root SKILL.md

**What:** The SKILL.md at `.claude/skills/harness/SKILL.md` acts as both a routing index AND a guard that prevents subagents from loading all rule files during passive discovery.

**When to use:** Always. GSD executor prompts say "list skills, read SKILL.md for each, follow relevant rules during implementation." The root SKILL.md intercepts this.

**Example:**
```markdown
# Harness Routing Skill

This skill manages the unified workflow harness.

## Important: Selective Loading

Do NOT read rule files in subdirectories (rules/, personas/, tdd/) directly.
Rule files are injected into specific agent types via the `agent_skills` config
in `.planning/harness.json`. Only read rule files if they appear in your
`<agent_skills>` block.

## Lifecycle Routing

| Phase | Owner | Skills Loaded |
|-------|-------|---------------|
| Requirements -> Roadmap | GSD | None |
| Phase Discussion | GSD | None (CEO gate via agent at boundary) |
| Phase Planning | GSD | None |
| Plan Execution (implementation) | GSD + TDD rules | tdd-enforcement.md via agent_skills |
| Plan Execution (non-implementation) | GSD | None |
| Phase Verification | GSD + verification rules | verification-rules.md via agent_skills |
| Code Review | Harness | code-review.md via agent_skills |
| Bug Investigation | Harness | systematic-debugging.md via agent_skills |
```

### Pattern 3: Two-Layer Config (harness.json + agent_skills in config.json)

**What:** harness.json owns the harness schema (gates, toggles, exemptions). GSD's config.json `agent_skills` field stores the skill path mappings that GSD's `buildAgentSkillsBlock()` reads.

**Why two files:** D-07 mandates a separate harness.json for GSD update safety. But `agent_skills` MUST live in GSD's config.json because `buildAgentSkillsBlock()` reads from `config.agent_skills[agentType]` -- there is no way to make it read from an external file without patching GSD (which D-11 forbids).

**harness.json schema:**
```json
{
  "version": "1.0",
  "gates": {
    "tdd_enforcement": true,
    "role_reviews": true,
    "bypass_protection": true
  },
  "role_triggers": {
    "ceo_review": ["new-project", "scope-change"],
    "eng_review": ["discuss-phase"],
    "qa_gate": ["pre-ship"],
    "security_audit": ["pre-ship"]
  },
  "tdd_exempt_plan_types": ["config", "docs", "scaffolding"],
  "agent_skills_reference": {
    "_comment": "Canonical skill mappings. Actual injection uses config.json agent_skills field.",
    "gsd-executor": [".claude/skills/harness/tdd"],
    "gsd-verifier": [".claude/skills/harness/rules"]
  }
}
```

**config.json agent_skills entries:**
```json
{
  "agent_skills": {
    "gsd-executor": [".claude/skills/harness/tdd"],
    "gsd-verifier": [".claude/skills/harness/rules"]
  }
}
```

**How `buildAgentSkillsBlock()` works (verified from source):**
1. Reads `config.agent_skills[agentType]` (string or array of strings)
2. Validates each path exists within project root via `security.cjs` `validatePath()`
3. Generates `<agent_skills>` block with `- @{path}/SKILL.md` entries
4. Workflows embed this block in subagent dispatch prompts

### Pattern 4: Structural Diff Audit for GSD Compatibility

**What:** A bash script that verifies no harness files overlap with or modify GSD files.

**When to use:** Phase 1 verification step. Also useful as a pre-commit check.

**Approach:**
```bash
# 1. Verify no harness files exist in GSD's global directory
find ~/.claude/get-shit-done/ -newer $INSTALL_TIMESTAMP -type f
# Should return nothing -- harness does not touch GSD globals

# 2. Verify GSD commands still return expected JSON
node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" init execute-phase 1 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('phase_found') is not None"

# 3. Verify agent-skills command reads new config
node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" agent-skills gsd-executor 2>/dev/null
# Should output <agent_skills> block with harness paths

# 4. Verify generate-claude-md preserves harness section
node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" generate-claude-md --auto
grep "GSD:harness-start" CLAUDE.md
# Should find the harness marker intact
```

### Anti-Patterns to Avoid

- **Putting routing logic in CLAUDE.md:** CLAUDE.md should be ~50 tokens pointing to the skill. Routing tables, lifecycle maps, and conditional logic go in `.claude/skills/harness/SKILL.md`. Violating this causes context budget death (Pitfall 1).

- **Patching GSD's config.cjs to add harness keys:** D-11 forbids modifying GSD files. Use `agent_skills.<agent-type>` which is already a valid dynamic key pattern. Use harness.json for harness-specific config.

- **Creating stub files with substantial content:** Phase 1 stubs should be minimal (title + "Populated in Phase N" note). Do not pre-write TDD enforcement or role persona content -- that is Phase 2-3 scope.

- **Adding harness agent definitions to GSD's agent list:** Harness agents (harness-ceo-reviewer, etc.) are NOT GSD agent types. They should NOT be added to the `<available_agent_types>` list in execute-phase.md. They are standalone agents spawned by CLAUDE.md gate instructions.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Skill path injection into subagents | Custom dispatch wrapper | GSD's `buildAgentSkillsBlock()` + `config.agent_skills` | Already validates paths, generates correct XML format, handles string/array normalization |
| CLAUDE.md section management | Manual file editing with regex | GSD's marker system (`<!-- GSD:harness-start -->`) | `generate-claude-md` preserves non-managed markers; battle-tested |
| Config CRUD | Custom JSON reader | GSD's `config-set`/`config-get` for agent_skills entries | Handles dot-notation, type parsing, nested objects |
| Subagent dispatch | New Task() wrapper | GSD's existing execute-phase workflow + `${AGENT_SKILLS}` variable | Already embeds skills block, handles model selection, parallelization |

## Common Pitfalls

### Pitfall 1: agent_skills Paths Must Be Relative to Project Root

**What goes wrong:** `buildAgentSkillsBlock()` calls `validatePath()` from `security.cjs` which checks paths are within project root. Absolute paths or paths with `../` will be rejected silently.

**Why it happens:** The skill paths in `config.agent_skills` are treated as relative to `cwd` (project root). Using `.claude/skills/harness/tdd` works; using `/Users/name/project/.claude/skills/harness/tdd` or `~/.claude/skills/harness/tdd` will fail.

**How to avoid:** Always use project-relative paths: `.claude/skills/harness/tdd`, `.claude/skills/harness/rules`.

**Warning signs:** `agent-skills` command returns empty output when you expect a block.

### Pitfall 2: harness.json vs config.json Dual-Source Confusion

**What goes wrong:** The harness config lives in TWO places: harness.json (gates, toggles) and config.json (agent_skills paths). If they drift out of sync, the executor loads skills that the harness thinks are disabled, or vice versa.

**Why it happens:** D-07 mandates separate harness.json for GSD update safety, but `buildAgentSkillsBlock()` reads from config.json only.

**How to avoid:** harness.json is the source of truth for intent. config.json agent_skills is the mechanism. Document this relationship clearly. Consider a setup script that syncs them, or document a manual sync procedure.

**Warning signs:** Changing a gate toggle in harness.json has no effect on subagent behavior (because agent_skills in config.json was not updated).

### Pitfall 3: CLAUDE.md Token Budget Overrun

**What goes wrong:** The harness section grows beyond ~50 tokens as developers add "just one more instruction." At 1,000+ tokens, it competes with GSD's own sections for attention.

**Why it happens:** CLAUDE.md is always loaded. Every token in it is consumed on every inference. The temptation to put routing logic inline is strong.

**How to avoid:** Enforce the D-05 budget ruthlessly. The CLAUDE.md section should ONLY say: harness exists, skill directory location, config file location. Everything else goes in SKILL.md files that load on demand.

**Warning signs:** CLAUDE.md harness section exceeds 3 lines of non-comment text.

### Pitfall 4: Passive Discovery Loads All Harness Skills

**What goes wrong:** GSD executor prompt says "list skills, read SKILL.md for each." If the harness root SKILL.md does not explicitly guard against deep loading, the executor reads all SKILL.md files in subdirectories, loading TDD rules into non-implementation plans and personas into executors.

**Why it happens:** Claude Code's skill discovery is recursive -- it finds all SKILL.md files in the directory tree.

**How to avoid:** The root `.claude/skills/harness/SKILL.md` must contain explicit instructions: "Do NOT read rule files in subdirectories directly. They are injected via agent_skills config." The subdirectory SKILL.md files should also include a guard: "Only follow these rules if this file was provided in your `<agent_skills>` block."

**Warning signs:** Executor subagents reference CEO review criteria or QA gates when executing a simple implementation plan.

### Pitfall 5: Stub Files Breaking Existing GSD Skill Scan

**What goes wrong:** If the stub SKILL.md files contain invalid markdown or confusing instructions, subagents that discover them via passive scanning may become confused about their role.

**Why it happens:** Even with the passive discovery guard, Claude may still glance at subdirectory SKILL.md files.

**How to avoid:** Stubs should be minimal and unambiguous: title, one-line description, "Content delivered in Phase N," and an explicit "Do not act on this file" instruction.

## Code Examples

### harness.json Schema (Full)

```json
{
  "version": "1.0",
  "gates": {
    "tdd_enforcement": true,
    "role_reviews": true,
    "bypass_protection": true
  },
  "role_triggers": {
    "ceo_review": ["new-project", "scope-change"],
    "eng_review": ["discuss-phase"],
    "qa_gate": ["pre-ship"],
    "security_audit": ["pre-ship"]
  },
  "tdd_exempt_plan_types": ["config", "docs", "scaffolding"],
  "agent_skills_reference": {
    "gsd-executor": [".claude/skills/harness/tdd"],
    "gsd-verifier": [".claude/skills/harness/rules"]
  }
}
```

### config.json agent_skills Addition

```bash
# Use GSD's own config-set for the agent_skills entries
node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" config-set 'agent_skills.gsd-executor' '[".claude/skills/harness/tdd"]'
node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" config-set 'agent_skills.gsd-verifier' '[".claude/skills/harness/rules"]'
```

### CLAUDE.md Harness Section

```markdown
<!-- GSD:harness-start -->
## Harness

Unified workflow harness active. Skills: `.claude/skills/harness/`
Config: `.planning/harness.json`
<!-- GSD:harness-end -->
```

### Root SKILL.md Template

```markdown
# Harness: Unified Workflow Router

Route-not-stack architecture. Each lifecycle phase has one framework authority.

## Selective Loading

Do NOT read subdirectory rule files directly. They are injected into specific
agent types via `agent_skills` in `.planning/config.json`.

Only load a rule file if it appears in your `<agent_skills>` block.

## Config

Gate toggles and role triggers: `.planning/harness.json`
Skill injection paths: `.planning/config.json` `agent_skills` field

## Lifecycle Routing

| Phase | Owner | Injected Skills |
|-------|-------|-----------------|
| Project init | GSD | CEO gate at boundary (agent) |
| Requirements -> Roadmap | GSD | None |
| Phase Discussion | GSD | Eng gate at boundary (agent) |
| Phase Planning | GSD | None |
| Implementation execution | GSD | tdd-enforcement via agent_skills |
| Non-implementation execution | GSD | None |
| Phase Verification | GSD | verification-rules via agent_skills |
| Code Review | Harness | code-review via agent_skills |
| Bug Investigation | Harness | systematic-debugging via agent_skills |
| Pre-ship QA | Harness | QA gate (agent) |
| Pre-ship Security | Harness | Security audit (agent) |
```

### Subdirectory Stub Template

```markdown
# Harness: {Domain Name}

Skill content delivered in Phase {N}. Do not act on this file.

## Status

Stub -- populated during Phase {N} ({phase_name}).
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Stack all frameworks simultaneously | Route-not-stack with exclusive ownership | Identified in unified-workflow PoC (March 2026) | Prevents governance conflicts and context bloat |
| Extend GSD's config.json with harness keys | Separate harness.json sidecar + agent_skills in config.json | Decision D-07 (this project) | Zero GSD patching; harness fully owns its schema |
| Global SKILL.md with everything | Per-subdirectory SKILL.md with passive discovery guard | Decision D-01, D-02 (this project) | Prevents over-loading; enables precise per-agent injection |

## Open Questions

1. **INFRA-04 Decision Change: harness.json vs config.json**
   - What we know: INFRA-04 says "Config extension in `.planning/config.json`" but D-07 decided on separate harness.json. The agent_skills paths still go in config.json because `buildAgentSkillsBlock()` reads from there.
   - What's unclear: Whether INFRA-04 should be considered satisfied by the dual approach (harness.json + config.json agent_skills) or if the requirement text needs updating.
   - Recommendation: Treat D-07 as the authoritative decision. INFRA-04 is satisfied by: harness gates live alongside GSD settings in the `.planning/` directory (just in a sidecar file).

2. **Subdirectory SKILL.md Discovery Behavior**
   - What we know: Claude Code discovers SKILL.md files by walking the directory tree. The root SKILL.md guard should prevent deep loading.
   - What's unclear: Whether Claude Code's skill scanner respects "do not read subdirectory" instructions or recurses regardless.
   - Recommendation: Include guards in BOTH the root SKILL.md AND each subdirectory SKILL.md. Belt and suspenders.

3. **harness.json Read Mechanism in Subagents**
   - What we know: D-08 says subagents receive harness.json via `<files_to_read>`. But Phase 1 does not modify GSD's execute-phase.md to add harness.json to the files_to_read block.
   - What's unclear: How harness.json gets into subagent context without modifying GSD workflows.
   - Recommendation: CLAUDE.md harness section should include an instruction like "When dispatching subagents, include `.planning/harness.json` in the `<files_to_read>` block." The orchestrator (which reads CLAUDE.md) will follow this instruction. This avoids modifying GSD's workflow file.

## Project Constraints (from CLAUDE.md)

- **Delivery format:** Files-only for v1 -- no CLI, no build step, no dependencies
- **GSD compatibility:** Must work within GSD's existing subagent/orchestrator model
- **Context budget:** Harness must not bloat context -- selective loading, not everything-at-once
- **Copy-and-own:** Absorb patterns as harness-owned files, no live external dependencies
- **TDD scope:** Mandatory for implementation code, exempt for config/scaffolding/one-off scripts (but TDD content is Phase 2, not Phase 1)
- **GSD Workflow Enforcement:** All file changes should go through GSD commands
- **No harness CLI:** GSD's gsd-tools.cjs handles all runtime needs

## Sources

### Primary (HIGH confidence)
- GSD `config.cjs` source at `~/.claude/get-shit-done/bin/lib/config.cjs` -- `VALID_CONFIG_KEYS`, `isValidConfigKey()` dynamic pattern for `agent_skills.<agent-type>`, `buildNewProjectConfig()` defaults
- GSD `init.cjs` source at `~/.claude/get-shit-done/bin/lib/init.cjs` -- `buildAgentSkillsBlock()` implementation, path validation, XML block format
- GSD `profile-output.cjs` source at `~/.claude/get-shit-done/bin/lib/profile-output.cjs` -- `cmdGenerateClaudeMd()`, `MANAGED_SECTIONS` array (5 sections), marker matching logic
- GSD `claude-md.md` template at `~/.claude/get-shit-done/templates/claude-md.md` -- marker format specification, section ordering
- GSD `execute-phase.md` workflow at `~/.claude/get-shit-done/workflows/execute-phase.md` -- subagent dispatch pattern, `${AGENT_SKILLS}` injection, `<files_to_read>` block
- GSD `gsd-executor.md` agent at `~/.claude/agents/gsd-executor.md` -- YAML frontmatter pattern, role/context/files_to_read structure
- Project `.planning/config.json` -- current config state, empty `agent_skills: {}`

### Secondary (MEDIUM confidence)
- `.planning/research/ARCHITECTURE.md` -- route-not-stack pattern, integration seams, component boundaries
- `.planning/research/PITFALLS.md` -- context budget death, governance conflicts, TDD bypass risks
- `.planning/research/SUMMARY.md` -- synthesized findings and phase ordering rationale

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all GSD integration points verified from source code
- Architecture: HIGH -- decisions locked in CONTEXT.md, GSD mechanisms verified
- Pitfalls: HIGH -- agent_skills behavior verified from source; passive discovery tension identified and mitigated

**Research date:** 2026-04-04
**Valid until:** 2026-05-04 (stable -- GSD at 1.30.0, no fast-moving dependencies)
