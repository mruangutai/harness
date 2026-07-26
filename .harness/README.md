# `.harness/` — Harness State Model

The harness-native backbone. Replaces GSD's `.planning/` artifact chain with a lightweight,
self-owned set of files that personas read and write. No orchestrator engine, no build step —
these are plain markdown/JSON files read by personas and the crew runner at spawn time.

## Files

| Path | Purpose | Read by | Written by |
|------|---------|---------|-----------|
| `BRIEF.md` | North star. Goal, Requirements (REQ-NN), Constraints, Success Criteria. Stable across the project. | all personas | planner (greenfield bootstrap) |
| `PLAN.md` | Active plan. `## Decisions` (D-NN + rationale/tradeoffs), `## Approval` (explicit user-approval marker + date), `## Tasks` (T-NN). | all personas | planner |
| `STATE.md` | Living handoff digest. `## Current` (active task + persona), append-only `## Log`, `## Open Questions`. | all personas at spawn | **coordinator only** |
| `notes/` | Durable artifacts: `scout-<topic>.md` research, persisted reviewer reports, `history/` (archived prior planning). | planner, documentor, reviewers | scout, reviewers |
| `crews/` | Crew configs (`*.yaml`) and ephemeral run workspaces (`runs/<ts>-<crew>/`). | crew runner | crew runner |
| `harness.json` | Gate toggles + role triggers + `tdd_exempt_plan_types`. | personas, crew runner | maintainer |

## Writer ownership (concurrency safety)

- **Single-owner paths** (disjoint — safe under parallel fan-out): source code → builder;
  test files → tester (builder owns only the unit tests it writes TDD-style during implementation;
  tester and builder run sequentially, so no write conflict); `PLAN.md` → planner;
  doc files → documentor; `notes/scout-*.md` → scout.
- **`STATE.md` is coordinator-owned.** Subagents *return* a Completion Block; the main session
  appends it to the log. Shared mutable state stays single-writer.
- **Crew-run artifacts** live under `crews/runs/<ts>-<crew>/<step-id>/` and are ephemeral.
  Canonical outputs (e.g. a finalized `PLAN.md`) are *promoted* into the persistent files by the coordinator.

## Handoff contract (how personas pass work)

Handoff is **by file path, never by conversation**. Each persona writes a durable artifact and
returns a compact three-part signal:

```
VERDICT: PASS | FAIL | ESCALATE     # control — drives fixed DAG transitions
DIGEST:                             # routing — the orchestrator reads THIS, not the artifact
  headline: <one-line BLUF>
  <persona-specific routing fields> # e.g. scout: feasibility, surface, flags, recommend
  open_questions: <count>
  files_touched: [<paths>]          # doers only
artifact: <path>                    # the focal, high-SNR doc — read by the CONSUMER persona
```

The orchestrator routes on `VERDICT` + `DIGEST` (small, structured) and only the downstream
*consumer* persona opens the artifact. This keeps the coordinator's context small while letting
it route conditionally (e.g. scout `flags: [security]` → insert security-reviewer).

**Artifact output discipline** (shared rule `rules/handoff.md`, loaded via each persona's Discipline):
- **BLUF** — conclusion/recommendation first, never a process log.
- **Claims + pointers, not payloads** — cite `file.ts:line`, don't paste code.
- **Explicit "Open Questions / Decisions Needed."**
- **Bounded length** (≈ one screen) — the cap forces signal over volume.

## Repo-mutator handoff & test guardrails

Repo-mutating doers (builder, tester, documentor) hand off via a **pull request** — one PR per
crew run (one feature = one branch). Builder commits code, tester commits tests, documentor commits
docs, all to the same branch. Reviewers and the tester work against the **PR diff** (ground truth),
not a self-reported file list. The PR merges when gates pass.

**Test guardrails** (owned by the tester, enforced against the PR diff; matrix in `harness.json`):

| Change type | Unit (TDD) | Functional | Integration | UI / Playwright |
|---|:---:|:---:|:---:|:---:|
| logic / util | ✅ | — | — | — |
| api | ✅ | ✅ | if DB/external | — |
| cross-module | ✅ | ✅ | ✅ | — |
| frontend | ✅ | component | — | if interaction flow |
| feature (UI+API) | ✅ | ✅ | ✅ | ✅ |
| bugfix | ✅ regression | if functional | if integration | if UI |
| config / scaffolding / docs | exempt | exempt | exempt | exempt |

- The matrix is a **floor** — the tester may add requirements it infers from the diff, never drop below.
- **Hard gate:** a missing required test kind → tester `VERDICT: FAIL`, loop back to builder.
- The tester runs real **Playwright** E2E for UI features (`webapp-testing` capability). The advisory
  `qa-reviewer` does not execute automation — E2E execution belongs to the tester.

## Bootstrap (greenfield entry point)

When `BRIEF.md` is absent, the harness is un-bootstrapped. The `harness-planner` persona in
**greenfield mode** (or a `bootstrap` crew of `ceo → planner`) gathers Goal / Requirements /
Constraints / Success Criteria from the user and writes the first `BRIEF.md` plus an empty
`PLAN.md` and `STATE.md`. Every downstream persona and crew depends on `BRIEF.md` existing.

## Schema templates

### BRIEF.md
```markdown
# Brief: <project name>

## Goal
<one paragraph: what this project delivers and why>

## Requirements
- REQ-01: <requirement>
- REQ-02: <requirement>

## Constraints
- <constraint>

## Success Criteria
- SC-1: <observable, checkable outcome>
```

### PLAN.md
```markdown
# Plan

## Decisions
- D-01: <choice> — rationale: <why>; tradeoffs: <what was given up>

## Approval
- Status: <pending | approved>
- Approved by: <user> on <YYYY-MM-DD>

## Tasks
- T-01: <title>
  - files: <exact paths>
  - intent: <complete description of the change>
  - verify: <command that returns PASS/FAIL in <60s>
  - traces: REQ-01, D-01
  - status: <pending | in_progress | done | blocked>
```

### STATE.md
```markdown
# State

## Current
- task: <T-NN or "none">
- persona: <name or "none">

## Log
- <YYYY-MM-DD> │ T-NN │ <persona> │ <status> │ files: <paths> │ <notes>

## Open Questions
- <question needing user or downstream resolution>
```
