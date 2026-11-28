# OMP provider-neutral port baseline

Issue: #597  
Pinned SHA: `98976844a473c9e853c16ea2a82de8ec75088f1c`  
OMP: `18.0.4`  
Captured: 2026-08-24  
Worktree: dedicated checkout under `.claude/worktrees/harness/597-omp-behavior-baseline`

## Purpose

This is the observed pre-port reference for #589. It separates contracts that the port must preserve from current Claude-compatibility gaps that the OMP-native port is expected to close. Agreement between two post-port providers is insufficient if both regress from a stable contract recorded here.

No credentials, raw transcripts, absolute home paths, or machine-specific session paths are included.

## Starting state

- `AGENTS.md`: absent.
- `.omp/`: absent.
- `.agents/`: absent.
- Harness agents: project files under `.claude/agents/`.
- Harness skills and utilities: project files under `.claude/skills/`.
- Command hooks: `.claude/settings.json`.
- `disabledProviders`: `[]`.
- `modelRoles`: `default=openai-codex/gpt-5.6-sol:medium`; `advisor=google-antigravity/gemini-3.1-pro:high`.
- `task.maxRecursionDepth`: `3`.

## Baseline gates

Command:

```bash
bash .claude/skills/harness/bin/run-unit-tests.sh && \
  bash .claude/skills/harness/bin/check-state.sh
```

Observed result: exit `0`. The complete unit suite reported all checks passed. `check-state.sh` completed and emitted existing informational notes, including pruned run-directory references and historical state-file shape notes; it emitted no blocking exit.

The worktree was clean after all disposable probes were removed.

## Discovered agents

A fresh non-interactive OMP process using `openai-codex/gpt-5.6-sol` exposed these 16 Harness agents:

1. `harness-ai-dev`
2. `harness-backend-dev`
3. `harness-code-reviewer`
4. `harness-data-engineer`
5. `harness-dev-ops`
6. `harness-documentor`
7. `harness-eng-lead`
8. `harness-frontend-dev`
9. `harness-orchestrator`
10. `harness-pm`
11. `harness-product-lead`
12. `harness-qa`
13. `harness-security-reviewer`
14. `harness-ui-reviewer`
15. `harness-validator-lead`
16. `harness-visual-designer`

### Hierarchy contract — PRESERVE

A read-only OMP probe completed both required chains:

```text
harness-orchestrator → harness-eng-lead → harness-backend-dev
harness-orchestrator → harness-validator-lead → harness-code-reviewer
```

Each leaf returned its exact agent name, each lead received and reported the matching leaf, and the orchestrator consolidated both. No failure was reported and no files were touched. Leaf tool abstinence was self-reported rather than independently transcript-verified.

## Discovered skills

OMP exposed the root `harness` skill plus these 22 `harness-*` skills:

- `harness-brief`
- `harness-code-review`
- `harness-codebase-design`
- `harness-curate`
- `harness-digest-dev`
- `harness-distill`
- `harness-expertise`
- `harness-grilling`
- `harness-handoff`
- `harness-init`
- `harness-principles`
- `harness-qa-gate`
- `harness-review`
- `harness-simplify`
- `harness-spec-driven`
- `harness-systematic-debugging`
- `harness-tdd-enforcement`
- `harness-team`
- `harness-uat`
- `harness-verification-rules`
- `harness-wayfinding`
- `harness-zero-micro-management`

The model-visible path for `harness-handoff` was `skill://harness-handoff`.

Skill names, instructions, resources, and autoload intent are stable contracts. Their current `.claude/skills` physical source is not; #593 moves the canonical source to `.agents/skills`.

## Provider-selection observation

The main probe session ran on `openai-codex/gpt-5.6-sol`. When an engineering lead was instructed to pass an explicit OpenAI child-model override, OMP exposed no model parameter on dispatch; the attempted override was ignored and the backend child ran on its agent default, reported as `anthropic/claude-sonnet-5`.

Stable contract: a dispatch selects an agent, not an invocation-specific worker model.  
Current coupling to correct: canonical agent defaults resolve to Anthropic model names instead of provider-neutral role aliases.

## Claude command-hook integration gaps under OMP

The following are observed current gaps, not contracts to preserve. They demonstrate why #594 and #595 are required.

### Expertise and codebase-map delivery — MISSING

A fresh `harness-backend-dev` child reported that its initial context contained neither a `Your Expertise` section nor a `Codebase map` section. It saw only an instruction referencing an Expertise file path and did not read it.

Desired post-port contract: tiered Expertise and the codebase index are injected at OMP agent start without requiring agent obedience or a read tool.

### Domain write guard — NOT DELIVERED

A controlled `harness-backend-dev` write to out-of-domain `docs/omp-baseline-denied.txt` succeeded. The disposable file was verified and removed immediately.

Desired post-port contract: an out-of-domain edit is denied before execution with an actionable reason.

### Reviewer Bash write guard — NOT DELIVERED

A controlled `harness-code-reviewer` Bash redirect to `docs/omp-reviewer-bash-denied.txt` succeeded. The disposable file was verified and removed immediately.

Desired post-port contract: reviewer source writes through Bash are denied before execution.

### Branch creation gate — NOT DELIVERED

A controlled `harness-backend-dev` command created `feat/no-ticket-omp-baseline-probe`; it was not blocked. The disposable branch was deleted immediately.

Desired post-port contract: branch creation without an open issue or Harness flow id is denied when the gate applies.

### Digest stop hook — NOT DELIVERED

A controlled `harness-backend-dev` returned exactly `DONE`. OMP accepted the malformed return and did not continue the child for correction.

Desired post-port contract: malformed Harness digests are rejected at source, with bounded continuation behavior and no inferred fields.

### Dispatch override policy — SCHEMA-SIDE TODAY

OMP exposed no per-dispatch model parameter. The attempted override was ignored rather than reaching the current Claude `dispatch-guard.sh`; the child used its agent default. Provider-neutral aliases must preserve the no-invocation-override contract without relying on a nonexistent field.

## Script-policy baseline

Although Claude command hooks were not delivered in the OMP probes above, the existing script suites passed for:

- Expertise selection and budgets;
- domain and state-shape checks;
- Bash write detection;
- worktree placement;
- branch movement and branch creation policy;
- digest validation;
- dispatch policy;
- state invariants;
- YAML and schema validation.

Therefore the port should reuse the tested policy and replace host delivery, rather than redefine the rules in an OMP extension.

## Stable contract table

| Contract | Pre-port observation | Post-port requirement |
|---|---|---|
| Sixteen named roles | Present | Preserve |
| Orchestrator → leads → leaves | Both required chains completed | Preserve |
| Maximum task depth | `3` | Preserve |
| Harness skill catalog | Root skill + 22 prefixed skills present | Preserve from neutral source |
| Dispatch chooses agent, not child model | No model field exposed | Preserve with role aliases |
| Expertise/context injection | Missing under OMP | Fix in native OMP lifecycle |
| Domain edit denial | Missing under OMP | Fix in native OMP lifecycle |
| Reviewer Bash denial | Missing under OMP | Fix in native OMP lifecycle |
| Invalid branch denial | Missing under OMP | Fix in native OMP lifecycle |
| Digest rejection | Missing under OMP | Fix in native OMP lifecycle |
| Script policy tests | Passing | Preserve |
| State checker | Exit 0 with existing notes | Preserve or explicitly improve |

## Reproduction commands

```bash
# Environment and configuration
omp --version
omp config get disabledProviders
omp config get modelRoles
omp config get task.maxRecursionDepth

# Deterministic gates
bash .claude/skills/harness/bin/run-unit-tests.sh
bash .claude/skills/harness/bin/check-state.sh

# Model-mediated discovery and lifecycle probes
omp -p --no-session --model openai-codex/gpt-5.6-sol --auto-approve '<bounded probe prompt>'
```

The exact bounded prompts were the issue-scoped probes described in the sections above. Post-port #596 must re-run equivalent scenarios with Claude discovery disabled under both OpenAI and Anthropic mappings and compare provider-invariant outcomes against this table.
