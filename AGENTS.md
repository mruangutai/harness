# Harness

Harness is a provider-neutral agent-team framework for AI-assisted software development. It enables a CTO to take a software idea from product validation through architecture, disciplined implementation, and QA without context drift, scope creep, quality shortcuts, or unchallenged assumptions.

## Constraints

- Keep context selective; never load everything at once. TDD scope lives in `.harness/harness.json` and the applicable enforcement skill, not here.
- Harness is self-hosted with one carve-out: under DEC-174 it may plan its own enforcement-layer work but must not execute changes to its own hooks, validators, gate scripts, or their tests through the enforcement path being changed.
- Work on Harness code only in a worktree under `.claude/worktrees/`. `main` is stale by construction while feature work is active.
- There is no GSD dependency: no `.planning/` root, `agent_skills`, or `<files_to_read>` blocks.

## Project map

| What | Where |
| --- | --- |
| Project state and artifact ownership | `.harness/README.md` |
| Gates, test matrix, test kinds, and limits | `.harness/harness.json` |
| Organization, routing, and writable domains | `.harness/team-config.yaml` |
| Constitution | `docs/PRINCIPLES.md` |
| Specification | `.harness/harness/docs/SPEC.md` |
| Decision index | `.harness/harness/docs/DECISIONS-INDEX.md` |
| Decision authority | `.harness/harness/docs/DECISIONS.md` |
| Remaining build ledger | `.harness/harness/docs/BUILD.md` |

## Organization

The organization has 16 agents in four tiers:

```text
main session (layer 0, only user channel)
  → harness-orchestrator (layer 1, one per in-flight feature)
      → product, engineering, and validation leads (layer 2)
          → specialist members (layer 3, always leaves)
```

Host-specific agent discovery, skill delivery, model routing, and lifecycle hooks must preserve this organization without putting those mechanics into shared guidance.

## Decision discipline

Before changing a Harness document, search `.harness/harness/docs/DECISIONS-INDEX.md` for the affected surface and open the relevant entries in `DECISIONS.md`. Never read the authority in full when the index can scope the question. Cited entries are a floor; follow their references when they expose another governing decision.

A decision the tree flatly contradicts is **STRUCK, never marked stale** (DEC-188): remove it from every gate while retaining a strike record so citations continue to resolve.

## Conventions

- Check every command-verifiable prose claim before writing it.
- Run the canonical Harness state checker before committing, never after.
- Never write a shell wait loop. Use the host's supervised background-job mechanism; a foreground shell timeout can detach rather than terminate descendants.
