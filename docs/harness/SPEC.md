# Harness — Specification

> **What this is.** The harness as designed: what it is, present tense. No history, no rejected
> alternatives, no build steps. Rationale lives in [DECISIONS.md](DECISIONS.md); sequencing,
> migration and spikes live in [BUILD.md](BUILD.md).
>
> **Provenance.** Extracted 2026-07-26 from the design plan
> `~/.claude/plans/i-want-to-remove-tingly-dongarra.md` (1007 lines). That file is retained
> unmodified as the historical record. **This file is authoritative.**
>
> **How to use this file: load a section, not the file.** At ~28k tokens whole, and ~1.2k per section
> on average, reading it end-to-end to change one thing is waste. Use the index below.
>
> An earlier header claimed the property that mattered was being "short enough to re-read entirely
> after each change." **That was retracted** (DEC-104): the target was arbitrary, and a discipline
> built on it failed — ten statements went stale before an audit caught them. Propagation is now
> enforced by `bin/check-docs.sh`, not by anyone's memory.

---

## Index — load only what you need

Line numbers drift; section numbers do not. Grep for `## <n>.` to jump.

| Looking for | § | Cost |
|---|---|---|
| `.harness/` file layout, the question round-trip, state-consistency matrix, writer ownership, commit policy | **2** | 1.3k |
| The 15-agent org, `team-config.yaml` manifest, `consult-when` routing, team conventions (Supabase/Astryx), deploy-vs-init, the roster table | **3** | 2.5k |
| Agent frontmatter (what Claude Code parses, and what to avoid), tool grants per tier, the domain hook, reviewer verdict mapping, autonomy | **4** | 2.0k |
| Expertise — injection hook, entry IDs, update ops, curation, CEO feedback, project vs global tiers | **5** | 2.0k |
| Rules vs Expertise — which is which, who writes each | **6** | 0.3k |
| Rule delivery via native `skills:` preload | **7** | 0.4k |
| **The handoff contract** — three-part return, normative DIGEST schemas, conditional routing, malformed returns, git/PR lifecycle | **8** | 1.1k |
| **Test guardrails** — the change-type matrix, `test_matrix`/`test_kinds`, the four resolution states, AI evals | **9** | 1.1k |
| The orchestrator — loop, hierarchy and spawn depth, canonical flow, CEO briefing, consolidated DIGEST, escalation, `max_cycles` exhaustion | **10** | 2.7k |
| **Execution state** — `feature.yaml`, `state.yaml`, REQ/FEAT/D/T levels, checkpoint-before-dispatch, success criteria and UAT | **11** | 2.3k |
| Crew YAML schema and the runner algorithm | **12** | 0.7k |
| The v1 crew catalog and the prototype gate | **13** | 0.8k |
| Composability — v1 scope and the post-v1 flattening plan | **14** | 0.2k |
| **Operating constraints** — single operator, one feature per worktree, your own hand edits, unmodelled costs | **15** | 0.9k |

**Schemas are inline, deliberately.** Extracting them to a separate file was measured and rejected
(DEC-104): it saves 378 lines but creates a second file for a decision to fail to land in, which is the
defect this project has already hit once.

**Runtime agents never load this file.** Rule skills, injected Expertise, and `BRIEF`/`PLAN`/`STATE` are
what the 15 agents read at spawn. SPEC is a build-time artifact, so its size costs harness *development*,
never harness *operation*.

---

## 1. Overview

The harness is a standalone Claude Code workflow system. It owns four things end to end:

| Concern | Mechanism |
|---|---|
| **State** | harness-owned files under `.harness/` (§2) |
| **Org** | 15 agents in 3 squads under 3 domain leads (§3) |
| **Execution** | an orchestrator loop plus declarative crews (§10, §12) |
| **Discipline delivery** | each agent self-injects its own rule files (§7) |

**You are the CEO.** You define the goal, approve `BRIEF.md` and `PLAN.md`, and own the merge.
There is no CEO agent.

The system has no dependency on GSD (Get Shit Done): no `.planning/` root, no `agent_skills`
injection, no `gsd-*` agents, no `gsd-tools.cjs`. It is files-only with one deliberate exception —
`bin/check-domain.sh` (§4).

---

## 2. State model — root `.harness/`

Four files plus `harness.json` and one directory:

| File | Purpose | Read by | Written by |
|---|---|---|---|
| `.harness/BRIEF.md` | North star: Goal, Requirements (REQ-NN), Constraints, **Success Criteria (SC-NN)**, `## Approval`. Stable across the project. **The goal of record** — every goal-check anchors here. | all personas | `harness-pm` (drafts) · **user approves** |
| `.harness/PLAN.md` | Active plan: `## Decisions` (D-NN), `## Approval` (user marker + date), `## Features` (FEAT-NN: name, `traces:` REQs, its tasks — §11), `## Tasks` (T-NN: paths, intent, `verify:`, `traces:`, `feature:`, `change_type:`, `status:`). | all personas | `harness-pm` (except `## Approval` → orchestrator) |
| `.harness/STATE.md` | Live handoff digest — `## Current` (a *pointer* to the in-flight run's `state.yaml`, not a copy) + `## Open Questions`. Nothing else. **Bounded by construction** — no rotation rule needed. | all personas at spawn | **orchestrator only** |
| `.harness/logs/<YYYY-MM-DD>.md` | Append-only activity stream, one file per day. Each entry is a rolled-up DIGEST: `time · run · crew · agent · verdict · files · headline`. **Not loaded at spawn** — read only when a task explicitly calls for history. Pruned on a recurring schedule. | on request only | **orchestrator only** |
| `.harness/DESIGN.md` | Visual design contract: palette, type scale, spacing, component direction, light/dark. Established during `/harness-init`'s design pass; the authority UI work implements against. | frontend-dev, documentor, ui-reviewer | `harness-visual-designer` |
| `.harness/notes/` | Durable artifacts, **feature-scoped where they belong to a feature**: `research-<topic>.md`, `mockups/*.html`, `prototypes/<FEAT>/`, `review-<persona>-<runid>.md`, `uat-<FEAT>.md`, `ship-review-<FEAT>-<runid>.md`, `answers-<FEAT>-<runid>.md`, `feedback.md` (leads-only read), `history/`. | pm, documentor, reviewers, leads | pm, visual-designer, reviewers, orchestrator (`feedback.md`, `answers-*`, `ship-review-*`) |

Also present: `.harness/harness.json` (config — gates, `test_matrix`, `test_kinds`,
`log_retention_days`), `.harness/team-config.yaml` (the team manifest, §3),
`.harness/expertise/` (§5), `.harness/features/` (§11).

### 2.1 The question round-trip

Subagents have no channel to the user; the orchestrator does. Questions flow *up* and answers flow
back *down*:

1. **Orchestrator takes the user's prompt** and delegates it to the corresponding team member(s).
2. **Members return questions** — the `open_questions` field in every DIGEST (§8) is the channel.
   Any persona may raise them; a member never blocks waiting on a human.
3. **Orchestrator asks the user** (`AskUserQuestion` — the main session is the only tier with a user
   channel).
4. **Orchestrator re-delegates with the answers** written to disk and passed as an input path.

`open_questions` is an **active routing signal, not a passive count**: non-empty → the orchestrator
asks and re-delegates. This is the one mechanism for *every* human-in-the-loop moment after
onboarding — plan approval, the pm hitting ambiguity, a dev needing a decision, a lead needing
another lead's input. **There is no `interview` step type in the DAG**, and no persona needs a
special "ask the user" mode.

Under hierarchy it needs no new machinery: the consolidated DIGEST already rolls up
`open_questions` from members (§10), so a lead surfaces its team's questions the same way it
surfaces everything else. The orchestrator asks, then re-delegates with answers via the existing
`resume_from` + `state.yaml` path — the same mechanism that handles context resets. Human pauses
and crash recovery share one code path.

**Answers are durable, not ephemeral.** The orchestrator writes user answers to
`.harness/notes/answers-<FEAT>-<runid>.md`, never only into a run dir — run dirs are pruned, and
durable artifacts may be written from these answers. Lateral lead→lead routing uses the same file,
since two leads share no run dir.

**Feature-scoped artifacts name their feature.** `answers-`, `ship-review-`, `uat-` and
`prototypes/` all carry the `FEAT-NN` id, and each file's header repeats the feature and run. A
feature accumulates several runs across several squads (§11), so a bare `<runid>` leaves you
grepping `state.yaml` files to find out which feature an artifact belongs to. The id is in the
filename so `ls` answers it.

Onboarding is handled by `/harness-init`, not a crew (§3): it interviews you directly, writes
`BRIEF.md` + `harness.json` + the manifest, and takes your approval. The round-trip above is the
mechanism for every *subsequent* human-in-the-loop moment.

### 2.2 State-consistency check

Run at every `/harness` entry. The real state is a matrix, not a binary:

| Condition | Action |
|---|---|
| no `BRIEF.md` | project not onboarded — tell the user to run `/harness-init` |
| BRIEF, no `PLAN.md` | delegate to pm (normal planning) |
| **BRIEF with no `## Approval`** | **halt — surface to user. Nothing downstream may run against an unapproved goal** |
| PLAN re-planned after approval | pm must **reset** `## Approval` to pending; a stale approval must never carry onto a changed task set |
| PLAN with no `## Approval` | halt — surface to user for approval |
| STATE points at a task absent from PLAN | halt — report inconsistency, offer repair |
| PLAN task missing `change_type` | pm must fill it before the qa gate can apply |
| template `schema_version` gap | tell the user to run `/harness-init --upgrade` |
| logs older than `log_retention_days` | prune opportunistically |

### 2.3 Writer ownership (concurrency safety)

- **Single-owner paths**, disjoint and therefore safe under parallel fan-out: source code → the eng
  specialist owning that domain (frontend / backend / ai / data, routed by eng-lead so two devs
  never share a file); test files → qa; `BRIEF.md` + `PLAN.md` → pm; docs → documentor;
  `DESIGN.md` → visual-designer; `notes/research-*.md` → pm. **Reviewer reports are namespaced**
  `notes/review-<persona>-<runid>.md` so a parallel reviewer panel cannot collide.
- **`## Approval` blocks are orchestrator-written** — the one carve-out to single-owner.
  `BRIEF.md` / `PLAN.md` are pm-owned *except* their `## Approval` section, which only the
  orchestrator writes (it alone has the user channel). **pm never self-approves.**
- **`STATE.md` is orchestrator-owned (single writer).** In **flat** mode workers return their DIGEST
  to the orchestrator, which appends it. In **hierarchical** mode workers return to the lead; the
  lead's consolidated DIGEST carries a **per-member log block**, and the orchestrator appends those
  — so per-worker granularity survives without a second writer.
- **Persistent files are written in place; the run dir is for *transient* step outputs.** A persona
  whose deliverable is a canonical file (pm → `PLAN.md`) writes **directly** to `.harness/PLAN.md`.
  Run-dir artifacts (`.harness/features/<feat>/runs/<run>/`) hold reports and intermediates only.
  Where a step *does* stage a canonical file in its run dir, the **promotion step (copy → overwrite
  persistent path) must complete before any consumer step dispatches** — otherwise the consumer
  reads the previous version silently.
- **Destructive operations are blocked by a real mechanism, not a flag.** An earlier draft claimed
  `delete: false` "everywhere" as a blanket safety rail; **no such field exists and nothing implemented
  it** — it was a sentence, not a guard. Deletion is restrained the same way out-of-domain writes are:
  `check-domain.sh` matches `Bash` as well as `Write|Edit` and rejects destructive patterns (`rm -rf`,
  `git clean`, `> ` onto a tracked path outside domain) with `exit 2`. See §4.2 — this is the same
  script and the same limitation.

### 2.4 Growth is handled by separation, not rotation

`STATE.md` is read by every agent at spawn, so history must not live there.

- **`STATE.md` holds no history at all** — only `## Current` + `## Open Questions`, both
  self-clearing. No trimming rule to enforce.
- **The activity stream lives in `.harness/logs/<YYYY-MM-DD>.md`** — one file per day,
  orchestrator-written, appended as each DIGEST arrives. Never loaded at spawn; an agent reads a
  day's log only when its task explicitly requires history.
- **Pruning:** the orchestrator deletes logs older than `log_retention_days` (default **30**, set in
  `harness.json`) opportunistically at `/harness` entry, where the state check already runs — no
  scheduler. Because `logs/` is committed, pruning clears only the working tree; git history
  retains everything.
- **`PLAN.md`:** tasks with `status: done` are archived to `notes/history/plan-<milestone>.md` once
  merged; `PLAN.md` holds active + pending only. A fully-done `PLAN.md` is archived wholesale and a
  fresh one drafted. `BRIEF.md` persists across milestones (the north star); `PLAN.md` is
  per-milestone. Archiving is a **pm** task the orchestrator requests (pm owns the file).

### 2.5 Pause, resume, and commit policy

**Cross-session pause/resume needs no separate mechanism:** `STATE.md` (`## Current` +
`## Open Questions`) *is* the handoff artifact, re-read at every `/harness` entry. A mid-crew stop
leaves its run dir behind; the state check surfaces it and offers resume or discard.

**Commit policy:** `BRIEF.md` / `PLAN.md` / `STATE.md` / `notes/` / `logs/` / `expertise/` are
**committed**, so reviewers auditing the PR diff see plan and state changes.
`features/*/feature.yaml` is **committed** — it is the record of what shipped.
`features/*/runs/**` is **git-ignored** (ephemeral scratch that would pollute the diff) and pruned
on the `log_retention_days` schedule.

---

## 3. The org — 15 agents in 3 squads

**You (CEO)** — sovereign. Define the goal, approve `BRIEF.md` and `PLAN.md`, own the merge.

**Orchestrator** (the main session — not an agent) — two jobs:

1. **Works directly with you** — asks questions, surfaces escalations, takes approvals.
2. **Delegates to and coordinates the three leads** — and routes an escalated question either **up
   to you** or **laterally to another lead** (eng-lead hits a product ambiguity → orchestrator
   routes it to product-lead, not to you). Lateral routing keeps you out of decisions your own team
   can answer.

| Lead | Squad | Owns |
|---|---|---|
| **`harness-product-lead`** | pm, visual-designer, documentor | *What* to build, how it looks, how it's explained |
| **`harness-eng-lead`** | frontend-dev, backend-dev, ai-dev, data-engineer, dev-ops | *How* it's built — plus **architecture review** for its own squad |
| **`harness-validator-lead`** | qa, code-reviewer, security-reviewer, ui-reviewer | *Is it right* — runs the review panel and **assesses the feedback** |

**Goal-checking is distributed, not centralized in one role:**

- **Feature-level goal** → `pm` (owns the "what"; checks delivery against BRIEF: REQ coverage + SC
  outcomes)
- **Architecture goals** → `eng-lead` · **Coverage goals** → `qa` · **Security goals** →
  `security-reviewer`
- Each domain validates its own goals; the leads assess their squad's output; **you** hold final
  authority via BRIEF/PLAN approval and merge.

**Two properties of the system a builder must know — the author audits its own domain in exactly
two places:**

1. `pm` authors `PLAN.md` *and* checks the feature goal. This is self-review, unlike the other
   gates.
2. `eng-lead` routes the build *and* owns architecture review for its own squad.

Everywhere else authorship is separated from audit: `visual-designer` authors `DESIGN.md` /
`ui-reviewer` grades it · eng devs build / `code-reviewer` grades · `qa` writes tests /
`validator-lead` assesses adequacy. (Why the two exceptions are tolerated: DEC-34.)

### 3.1 The team manifest — `.harness/team-config.yaml`

The org is **data, not prose**. The manifest makes team membership and routing a lookup.

```yaml
orchestrator:
  name: Orchestrator
  skill: .claude/skills/harness/SKILL.md   # the playbook it runs (it is not an agent)
  color: blue                              # NAMED colors only (§4.0) — hex is invalid

paths:
  agents: .claude/agents/
  crews:  .claude/skills/harness/crews/
  features: .harness/features/

universal_rules:                            # preloaded by all 15 via `skills:` (§7)
  - harness-handoff
  - harness-expertise

teams:
  - team-name: Product
    team-color: purple
    lead: { name: harness-product-lead }
    conventions:                            # BINDING for this team (§3.2)
      - id: astryx-design-system
        rule: >
          All UI work implements against the Astryx design system
          (`@astryxdesign/core`, pinned). Do not introduce a second component substrate.
        provision: npm dependency — dev-ops verifies/installs at init
        reference: https://astryx.atmeta.com/
    members:
      - name: harness-pm
        consult-when: Requirements, feature scoping, planning, task breakdown, codebase research, acceptance criteria, goal verification
        domain:
          - { path: .harness/BRIEF.md,  upsert: true }   # except ## Approval (orchestrator-only)
          - { path: .harness/PLAN.md,   upsert: true }   # except ## Approval
          - { path: .harness/notes/,    upsert: true }
          - { path: .harness/expertise/harness-pm.md, upsert: true }   # REQUIRED for §5.3 self-apply
          - { path: ".",                read: true }     # read anything, write nothing else
      - name: harness-visual-designer
        consult-when: Visual identity, palette, typography, spacing, component direction, mockups — plus UX research, personas, journey mapping, usability friction
      - name: harness-documentor
        consult-when: READMEs, guides, reference docs, user-facing explanation

  - team-name: Engineering
    team-color: cyan
    lead: { name: harness-eng-lead }
    conventions:
      - id: supabase
        rule: >
          Use the Supabase plugin for database, auth, storage and edge functions.
          Do not hand-roll what Supabase provides; do not add a second backend substrate.
        provision: Claude Code plugin — available; dev-ops confirms project linkage at init
    members:
      - name: harness-frontend-dev
        consult-when: UI components, styling, client state, accessibility, browser behavior
        domain:
          - { path: <project UI paths>, upsert: true }   # per-project, seeded at init
          - { path: .harness/expertise/harness-frontend-dev.md, upsert: true }
          - { path: ".",                read: true }
      - name: harness-backend-dev
        consult-when: APIs, services, business logic, auth, server-side integration
      - name: harness-ai-dev
        consult-when: LLM/agent features, prompts, model integration, evals, non-deterministic behavior
      - name: harness-data-engineer
        consult-when: Schemas, migrations, pipelines, data models, queries
      - name: harness-dev-ops
        consult-when: Infra, CI/CD, config, build tooling, deployment, scaffolding, test-runner detection

  - team-name: Validation
    team-color: orange
    lead: { name: harness-validator-lead }
    members:
      - name: harness-qa
        consult-when: Test coverage, writing and running tests, regression, E2E, test-matrix enforcement
      - name: harness-code-reviewer
        consult-when: Spec compliance, code quality, maintainability
      - name: harness-security-reviewer
        consult-when: Auth, secrets, input validation, injection, OWASP, threat modeling
      - name: harness-ui-reviewer
        consult-when: Visual fidelity against DESIGN.md, design-contract soundness, UI regressions
```

**`consult-when` IS the routing mechanism.** Each member declares what it's for; the lead matches
the request semantically at delegation time. There is no `domain:` field on a task —
`change_type` is *only* a test-obligation axis (§9), never an ownership axis.

**Routing edge cases:**

- **Two or more members match** → the lead delegates to each in turn (serial), then consolidates. If
  the work genuinely needs splitting into separate tasks, that is a plan-level change → escalate to
  `pm`.
- **No member matches** → the lead does **not** guess. It returns `open_questions` ("no specialist
  owns X") and the orchestrator surfaces it to you. A silently mis-routed task is worse than a halt.
- **Cross-team match** → the lead cannot reach outside its squad; it escalates and the orchestrator
  routes to the other lead.

**The manifest/frontmatter split is POLICY vs CAPABILITY** — nothing is declared twice:

| Manifest (org policy — what the org decides *about* an agent) | Frontmatter (agent capability) |
|---|---|
| team membership, lead | `name`, `description` |
| `consult-when` — what it's consulted for | `tools` |
| `domain` — what paths it may write | `model`, `color`, `hooks` |

**Not in the manifest:** agent `description` or `tools` (frontmatter owns those), and no file `path`
— Claude Code resolves agents by name.

**`universal_rules` stays minimal** — just `handoff` and `expertise`. Every entry is preloaded in
full into all 15 agents at every spawn (§7), so a long list reintroduces exactly the context bloat
the compact-return design exists to prevent.

### 3.2 Team conventions — binding technology choices

A team may declare **conventions**: standing technology decisions that hold for every task that team
touches, so they are never re-litigated per feature and never re-derived from prose.

| Team | Convention | How it is provisioned |
|---|---|---|
| **Engineering** | Use the **Supabase plugin** for database, auth, storage, edge functions | A Claude Code plugin, already available. `dev-ops` confirms project linkage at init |
| **Product** | All UI implements against the **Astryx design system** (`@astryxdesign/core`, pinned) | An **npm dependency**, not a Claude capability — `dev-ops` verifies or installs it at init |

**Astryx is not globally available as a Claude Code capability.** It is an npm package (`@astryxdesign/core`,
React ≥19 peer, StyleX internal, runtime `defineTheme` with `[light, dark]` tuples) plus a reference
clone. "Ensure it's available" therefore means a real provisioning step per project, not an
assumption — `/harness-init` delegates the check to `dev-ops`, and a missing dependency is reported,
not silently worked around.

**How conventions bind:**

- They are **read by that team's lead and members** at spawn, from the manifest.
- A convention is **not** a rule skill (§6): rules are behavioral and identical everywhere;
  conventions are *technology choices* and vary by project and team. Keeping them in the manifest is
  what lets a project override one without forking the constitution.
- **Version pinning is the default.** A convention names a pinned version; an upgrade is a decision
  (`PLAN.md ## Decisions`), not a silent drift.
- **Deviating from a convention requires a `## Decisions` entry** and therefore your approval. An
  agent may not quietly choose a different substrate because it found one more convenient.
- Templates ship the default conventions, so a new project inherits them without configuration
  (§3.3).

### 3.3 Distribution — `/harness-deploy` vs `/harness-init`

| Operation | Does | Touches project state? |
|---|---|---|
| **`/harness-deploy`** | distributes the tool — skills, agents, **templates** — to global + enrolled projects | **never** |
| **`/harness-init`** | **THE onboarding interview** — run inside a project; asks project type, frameworks, and what you're building; writes every project artifact | yes, once |

**Enroll = deploy + init.**

**Distributed templates** live at `.claude/skills/harness/templates/`: `team-config.yaml`,
`harness.json`, `BRIEF.md`, `PLAN.md`, `STATE.md`, `DESIGN.md`, `gitignore.snippet`. They carry the
canonical schema plus the generic org, with **placeholders** where a project differs.

**`/harness-init` is an interview:**

1. **Technical** — project type (web app / API / CLI / library / data pipeline), frontend framework,
   backend framework.
2. **Product** — what you're building: goal, requirements, constraints, success criteria.
3. **Writes** — `harness.json` (`test_kinds` commands, `domain` globs, gates), `team-config.yaml`
   (from template), and a **draft `BRIEF.md`**.
4. **You approve the BRIEF** — the goal of record is signed before anything downstream runs (§2.2).
5. **Offers a design pass** — if the project has a UI, chain `visual-designer` → `ui-reviewer(A)` to
   establish `DESIGN.md`.

Mechanical detection (test-runner discovery, source layout → `domain` globs) is delegated to
**`dev-ops`**; the interview itself runs in the **main session**, because only it can call
`AskUserQuestion`.

**The roster is NOT pruned per project.** All 15 agents are present everywhere; irrelevant ones
**self-scope** to "not in scope" at the cost of one cheap spawn. Crew configs may still omit an
obviously-irrelevant reviewer from a specific panel.

**Template versioning handles org changes.** Templates carry a `schema_version`. When the harness
adds an agent, deploy pushes the new template but leaves the project's manifest alone; the state
check notices the version gap and tells you to run `/harness-init --upgrade`, which merges new
entries while preserving your `domain` values.

### 3.4 The roster

| Agent | Squad | Type | Role | Tools |
|---|---|---|---|---|
| `harness-product-lead` | — | **lead** | Conducts product crews; routes work across pm / visual-designer / documentor by `consult-when`; assesses and consolidates their DIGESTs | Read, Glob, Grep, **Agent** (no Edit/Bash) |
| `harness-eng-lead` | — | **lead** | Conducts build crews; **routes each task to one of five specialists** by `consult-when`; **owns architecture review**; consolidates DIGESTs | Read, Glob, Grep, **Agent** (no Edit/Bash) |
| `harness-validator-lead` | — | **lead** | Runs the review panel (`review-team`); **assesses and synthesizes** the feedback into one actionable set; the independence layer over `qa` | Read, Glob, Grep, **Agent** (no Edit/Bash) |
| `harness-pm` | product | doer | **Product manager — research + plan in one context.** (1) Research: explore code, resolve unknowns, web-research; (2) Plan: BRIEF + findings → `## Decisions` + specified `## Tasks` (with `change_type`). Greenfield mode drafts BRIEF. Checks the **feature goal**. Raises `open_questions` | Read, Glob, Grep, Edit, Write, Bash, Web |
| `harness-visual-designer` | product | doer | **Visual identity + design contract:** (1) `DESIGN.md` — palette, type scale, spacing, component direction, light/dark; (2) throwaway mockups for exploration; (3) **decides whether a feature requires end-user interaction, and if so builds the high-fidelity prototype you must approve** (§13.1) | Read, Glob, Grep, Edit, Write, Bash, Skill |
| `harness-documentor` | product | doer | Docs as user-facing communication — READMEs, guides, reference. Owns `.harness/README.md` | Read, Glob, Grep, Edit, Write, Bash |
| `harness-frontend-dev` | eng | doer | UI implementation against `DESIGN.md` | Read, Glob, Grep, Edit, Write, Bash |
| `harness-backend-dev` | eng | doer | APIs, services, business logic | Read, Glob, Grep, Edit, Write, Bash |
| `harness-ai-dev` | eng | doer | LLM/agent features, prompts, model integration. **Authors the eval** for any `ai_behavior` change — failure modes, rubric, reference dataset, threshold (§9.1). Does not gate it | Read, Glob, Grep, Edit, Write, Bash, Web |
| `harness-data-engineer` | eng | doer | Schemas, migrations, pipelines, data models | Read, Glob, Grep, Edit, Write, Bash |
| `harness-dev-ops` | eng | doer | Infra, CI/CD, config, build tooling, deployment, scaffolding. Catches the work that isn't feature code. Maps onto the TDD-exempt `config` / `scaffolding` change types (§9) | Read, Glob, Grep, Edit, Write, Bash |
| `harness-qa` | validator | doer | **Writes AND runs tests + assesses coverage.** Two phases: **(1)** derive expected coverage from BRIEF/PLAN with **no source access** (anti-bias); **(2)** read code, write/run tests incl. Playwright E2E, **run `ai-dev`'s evals**, enforce the `test_matrix` hard gate (§9.1), report gaps. Supplies the evidence pm's SC goal-check consumes (§11.6) | Read, Glob, Grep, Edit, Write, Bash, Skill |
| `harness-code-reviewer` | validator | reviewer | Two-stage: spec compliance, then code quality | Read, Glob, Grep, **Bash** (needs `git diff` — its own ground truth) |
| `harness-security-reviewer` | validator | reviewer | Self-scoping OWASP Top 10 + STRIDE; owns security goals | Read, Glob, Grep, Bash |
| `harness-ui-reviewer` | validator | reviewer | **(A)** pre-build: is `DESIGN.md` sound? **(B)** post-build: adversarial scored audit of built UI vs `DESIGN.md`. Self-scopes out on non-UI diffs | Read, Glob, Grep, Bash |

**Five eng domains, no catch-all.** `dev-ops` is a peer specialist, not a dumping ground: it owns
infra / CI / config / tooling / deploy, which is genuinely different work from feature code and
largely TDD-exempt. eng-lead routes each task to exactly one of the five.

**Discipline coverage:** `tdd-enforcement` → the 4 feature-code devs (dev-ops largely exempt via
`config` / `scaffolding` change types) · `systematic-debugging` → eng devs in debug mode ·
`spec-driven` → pm · `verification-rules` → qa · `code-review` → code-reviewer · `expertise` and
`handoff` → all 15 · `zero-micro-management` → the 3 leads.

---

## 4. Agent definition schema

### 4.0 Supported frontmatter

Claude Code parses a fixed set of frontmatter fields in an agent `.md` file. Only `name` and
`description` are required; everything else is optional. The harness uses seven of them:

```yaml
---
name: harness-eng-lead
description: "Engineering lead — routes work to specialists, owns architecture review"
tools: [Read, Glob, Grep, Agent]     # leads: NO Edit/Bash (§4.1)
model: opus                          # sonnet|opus|haiku|fable|<full id>|inherit
color: teal                          # NAMED color only — see below
skills:                              # rule delivery — FULL content preloaded at spawn (§7)
  - harness-handoff
  - harness-zero-micro-management
  - harness-expertise
hooks:                               # domain enforcement (§4.2)
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: .claude/skills/harness/bin/check-domain.sh harness-eng-lead
---
```

**`color` accepts a named color only** — `red`, `blue`, `green`, `yellow`, `purple`, `orange`,
`pink`, `cyan`. Hex values are not valid. Team colors are therefore expressed as names.

**Fields the harness deliberately does not use:**

| Field | Why not |
|---|---|
| `memory: user\|project\|local` | Native per-agent persistent memory — a close match for Expertise (§5), but it **auto-enables Read/Write/Edit** for that agent. That silently breaks the no-`Edit` guarantee for the 3 leads and the read-only guarantee for the 3 reviewers, which are load-bearing (§4.1). Expertise is hand-rolled instead, and injected by hook (§5.1). |
| `isolation: worktree` | Available, and the fallback if domain enforcement fails (BUILD.md § 0a). Not used by default — it costs a worktree per agent. |
| `disallowedTools`, `permissionMode`, `maxTurns`, `mcpServers`, `effort`, `background`, `initialPrompt` | Available; no current need. `mcpServers` is the likely home for per-team tool conventions (§3.2) if declaring them in the manifest proves insufficient. |

**Body sections** — `## Expertise` and `## Domain` are declarative *in form* but live in the
**body**: Claude Code's loader ignores unknown frontmatter keys, whereas the body becomes the system
prompt. They are **pointers**, not mechanisms — the authoritative `domain` list is in
`team-config.yaml`, and Expertise is delivered by hook.

**`## Skills` prose is gone.** Rules are now delivered by the native `skills:` field, which injects
full content at spawn (§7). There is no longer a prose section asking an agent to go read its rules.

Body template (indented to keep the outline parseable):

```markdown
  # Harness: Engineering Lead
  <one-line spawn summary>

  ## Expertise            ← POINTER; content is injected by the SubagentStart hook (§5.1)
  Your expertise file is `.harness/expertise/harness-eng-lead.md`. It is already in your
  context — you do not need to read it. Track architecture decisions, technical debt, risk
  patterns, and which implementation approaches hold up in this codebase.
  You have no Write tool: propose changes as `expertise_update` ops in your DIGEST (§5.3).

  ## Domain               ← POINTER; the authoritative list is in team-config.yaml
  Your writable paths are declared in `.harness/team-config.yaml` under your entry and
  enforced by your PreToolUse hook. You may read anything; you may write only your domain.

  ## Role · ## Protocol · ## Inputs · ## Output Format
```

### 4.1 Tool grants per tier

| | tools | mutates repo |
|---|---|---|
| **doers** | Read, Glob, Grep, Edit, Write, Bash | yes — only within its `## Domain` |
| **reviewers** | Read, Glob, Grep (+ Bash where it needs `git diff`) | never |
| **leads** | Read, Glob, Grep, **Agent**, and `Write` scoped to `features/*/runs/*-<its-squad>/**` | never — no `Edit`, no `Bash` |

**Leads delegate, never execute — enforced by capability where possible.** No `Edit` and no `Bash`;
`Write` **scoped by the domain hook to its own run dir only**. The `zero-micro-management` skill is
the behavioral layer on top.

- **Why leads need `Write` at all:** each lead owns its squad's run bookkeeping (§11). Writing your
  own state file is not "executing"; writing deliverables is.
- **Consequence to accept:** a lead cannot run `git diff` to assess its squad's work. It reads
  members' **artifacts and DIGESTs** instead — the handoff contract working as designed.

> **Verified (DEC-101):** a `PreToolUse` hook blocks a subagent's `Write` with `exit 2`, and the stderr
> reason reaches the agent — tested 5/5 cases including a lead's own run dir. Scoped lead `Write` holds.
> Residual: the *agent-frontmatter* declaration site is asserted by the docs but untested, because agent
> definitions are not live-reloaded (DEC-100a). On the restart checklist, not the risk register.

### 4.2 Domain enforcement — the hook

`## Domain` declares single-owner paths. An earlier draft called this "the entire justification for
running agents in parallel" — that overstated it twice over, and both corrections matter.

**First, disjoint domains are not achievable for shared files.** A codebase does not partition cleanly
into frontend / backend / ai / data write globs: `package.json`, lockfiles, shared type and schema
files, route registries and env config are *legitimately* written by several specialists. So either the
globs overlap — and the disjointness claim is void even with a perfect hook — or they don't, and routine
tasks BLOCK on files nobody may touch. "Eng-lead routing guarantees two specialists never own the same
file" holds at the roster level and is false at the file level.

**Shared-paths policy (required):** the manifest declares a `shared:` path set — `package.json`,
lockfiles, schema and type barrels, route registries, CI config. Writes to a shared path are **always
serialized** and attributed to whichever specialist the lead routed, regardless of domain. No agent
"owns" them.

**Second, the enforcement is a guardrail, not a guarantee** — see the `Bash` limitation below.
Serialization (§8.5) is what actually makes fan-out safe. Claude Code's `tools:` grant is
all-or-nothing — an agent with `Write` can write anywhere — so prose alone would let two parallel
doers clobber each other with **no error**: one write silently wins, and the lost change surfaces
later with nothing pointing at the cause.

The mechanism is a `PreToolUse` hook in each agent's frontmatter. Frontmatter hooks are supported and
fire when the agent is spawned as a subagent — but **two details are non-negotiable, and getting
either wrong makes the hook fail open**:

```yaml
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          # NO $FILE — the tool input arrives as JSON on stdin
          command: .claude/skills/harness/bin/check-domain.sh harness-frontend-dev
```

1. **Only `exit 2` blocks.** Any other non-zero exit is treated as a *non-blocking* error and **the
   write proceeds**. A script that exits 1 on violation silently permits every out-of-domain write
   while appearing to enforce — the exact silent corruption this hook exists to prevent.
2. **There is no `$FILE` variable.** The tool input arrives as **JSON on stdin**; the target path
   must be parsed from it. Only `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}` and
   `${CLAUDE_PLUGIN_DATA}` are interpolated into the `command` string.

`check-domain.sh` is therefore **generic and stateless**: read the JSON from stdin, extract the
target path, look the named agent up in `.harness/team-config.yaml`, test the path against that
agent's globs, and on violation write the reason to stderr and `exit 2`. Otherwise `exit 0`. It
contains no project-specific globs and is identical in every project; the *manifest* is what varies.

```bash
# shape only — the two things that must be right
path=$(jq -r '.tool_input.file_path' <&0)
if ! in_domain "$1" "$path"; then
  echo "harness: $1 may not write $path (see .harness/team-config.yaml)" >&2
  exit 2                     # 2, not 1 — anything else lets the write through
fi
exit 0
```

Because the hook is declared in that agent's frontmatter, it fires only for that agent's calls — no
caller-identity detection needed. One canonical list, one identical hook line per agent, differing
only in the name. This is the only mechanism that is both per-agent and path-scoped:
`settings.json` rules are global and `tools:` is too coarse.

**The `Bash` bypass is the hook's real limitation, and it is not confined to `dev-ops`.** All **9
doers** hold `Bash`. A `matcher: "Write|Edit"` hook sees none of `sed -i`, `cat > f`, `tee`, or a build
script that writes files — and models reach for shell redirection constantly, so this is ordinary
drift, not malice. **A hook that guards `Write|Edit` alone does not make the parallel-safety claim
true.**

Matching `Bash` properly is unwinnable in general: you cannot reliably extract write targets from an
arbitrary shell command. So the honest position is:

| | |
|---|---|
| **The real mechanism for write safety** | **serialization** — §8.5 already forces repo-mutators strictly serial on one branch — plus `isolation: worktree` for the rare genuinely-parallel mutate |
| **What the domain hook is** | a **guardrail** that catches the common `Write`/`Edit` case and obvious destructive `Bash` patterns. Useful; not a guarantee |
| **What must therefore be dropped** | the claim that the hook is "the entire justification for running agents in parallel." Serialization is |

This inverts an earlier framing that treated the hook as load-bearing and serialization as a fallback.

> **Verified (DEC-101):** `exit 2` blocks; `exit 1` does not. `check-domain.sh` is built and tested —
> in-domain allowed, out-of-domain blocked, own Expertise allowed, shared paths allowed with a warning.
> It also prints the agent's **permitted globs** on rejection, because a probe confirmed that naming only
> the rejected path leaves an agent no basis for choosing a valid alternative (DEC-100b).
>
> This does **not** rescue the parallel-safety claim — the `Bash` bypass above is unaffected by any hook.
> Serialization remains the mechanism.

### 4.3 Reviewer verdict mapping

Reviewers are **advisory-only; no hard blocks on style or opinion.** Only substantive findings gate:

- `must_fix` non-empty **or** `severity_max ≥ high` → `FAIL` (gates, loops back)
- "Concerns Noted" / `severity_max ≤ med` with empty `must_fix` → **`PASS` (with notes)** — logged,
  surfaced, does not block

This prevents the non-convergence trap where a permanent minor nit loops forever to `max_cycles`.

### 4.4 Autonomy is scoped by reversibility

Stated once in `rules/handoff.md` and shared by all agents:

| Decision | Behavior |
|---|---|
| cheap and reversible (naming, local structure, test shape) | **decide autonomously**, record it in the DIGEST |
| expensive or hard to reverse (schema, API contract, new dependency) | **ask** via `open_questions` |
| changes scope, goal, or a `## Decisions` entry | **always ask** — yours by definition |

The tier that owns the human relationship (the orchestrator) is never itself "autonomous" — it
asks; the workers below it mostly don't need to.

---

## 5. Expertise — per-agent durable knowledge

Each agent keeps an **Expertise** file: durable knowledge it starts every task with and refines on
completion. This recovers what a stateless-subagent design otherwise discards at every spawn —
eng-lead's sense of what works in *this* codebase, qa's knowledge of which tests are flaky, pm's feel
for where scope creeps.

> **One name.** This is called **Expertise** throughout: the file is `.harness/expertise/<agent>.md`
> and the governing rule is the `harness-expertise` skill. The terms "mental model" and
> "institutional memory" are not used — they described the same artifact and the drift was a defect.

**Location:** `.harness/expertise/<agent>.md` — **per-project** (because `.harness/` is) and
committed, so learned knowledge is versioned and visible in PRs.

### 5.1 Delivery — injected, not read

Expertise reaches an agent through a **`SubagentStart` hook** declared in `settings.json`. The hook
receives `agent_type` and returns that agent's file as `hookSpecificOutput.additionalContext`, which
is injected into the starting subagent's context.

```
SubagentStart(agent_type: harness-eng-lead)
  → cat .harness/expertise/harness-eng-lead.md
  → { "hookSpecificOutput": { "additionalContext": "<file contents>" } }
```

Two properties follow, and both matter:

- **No obedience dependency.** The agent does not have to remember to read its file — it starts with
  it. This is the same class of mechanism that makes `skills:` reliable (§7).
- **No tool grant required.** A reviewer holding only `Read`/`Grep` still starts with its Expertise
  loaded. This is precisely why native `memory:` was rejected (§4.0): it would deliver the same
  content but silently add `Write`/`Edit` to all 15 agents.

An agent reads **only its own** file. One bounded exception: a lead may read a member's file during a
curation pass (§5.4).

### 5.2 Structure — capped sections, stable entry IDs

Entries carry **stable IDs** so an update can name the exact entry it supersedes (§5.3). Without IDs,
reconciliation can only append.

```markdown
  ## Patterns (max 15)        durable truths about this codebase
  - P-01: Migrations fail if run before the seed script.        (2026-07-12)
  - P-02: Auth middleware is JWT at `auth/mw.ts:42`.            (2026-07-19)

  ## Gotchas (max 15)         traps that cost time before
  - G-01: The dev server caches env vars until fully restarted. (2026-07-20)

  ## Outcomes (max 10)        we tried X → result (so don't re-litigate)
  - O-01: Tried bundling with esbuild → broke source maps; reverted. (2026-07-15)

  ## Open (max 5)             unresolved uncertainties in my domain
  - Q-01: Unclear whether the queue guarantees ordering under retry.
```

IDs are assigned per section and never reused after a drop, so a dropped `P-11` stays gone rather
than being silently replaced by a different fact under the same name.

**Decision vs observation — a hard boundary:**

- **A choice** → `PLAN.md ## Decisions` (approval-gated). *"We decided on Postgres."*
- **An observation about how the codebase behaves** → Expertise. *"Migrations fail if run
  before the seed script."*

Without this boundary, Expertise becomes a shadow decision log that bypasses your approval.

**Content quality is ADVISORY, in three layers** — a hook can block a path, but cannot judge an
insight:

| Layer | Where |
|---|---|
| The rule | the `harness-expertise` skill — preloaded by all 15 agents via `skills:` (§7): *"Update ONLY if you learned something that would change how you'd act next time."* Most tasks teach nothing durable and should produce **no** update. |
| Visibility | every update rides the DIGEST as an explicit op with a `why` — so it is observable before it lands, not discovered later |
| Correction | curation (§5.4) catches what slipped through |

### 5.3 Updating — reconcile at propose time, then apply

Appending is not enough: a **contradicting or stale entry can land while well under the cap**, and a
cap-triggered pass would never catch it. So reconciliation happens **when the update is proposed**, by
the agent that already has the file in context from the injection hook.

Updates are therefore **ops, not appends**, and every op names its target:

```yaml
expertise_update:
  - op: replace                 # add | replace | merge | drop
    target: P-01
    section: Patterns
    entry: "Seed script no longer required before migrations (removed in #418)."
    why: "observed migrations passing on a clean DB this run"
```

An op naming a nonexistent target is a **contract violation**: the applier rejects it and re-prompts
once, then records `BLOCKED (contract violation)` — reusing §8.3 rather than guessing.

**Who applies, by capability.** Read is uniform for all 15; writing splits:

| Agent tier | Reconciles | Applies |
|---|---|---|
| **9 doers** (have `Write`) | itself, at propose time | **itself**, in place — the domain hook scopes it to its own file, which **must therefore appear in that agent's `domain`** (see below). The op is still reported upward in the DIGEST for logging |
| **3 leads + 3 reviewers** (no `Write`/`Edit`) | itself, at propose time | **the orchestrator**, which validates the op and applies it verbatim — it is a scribe, not an editor |

> **Roster arithmetic, stated once because it was previously wrong:** 15 = **3 leads + 9 doers + 3
> reviewers**. `qa` is a **doer** (it writes tests), so the doers are pm, visual-designer, documentor,
> frontend-dev, backend-dev, ai-dev, data-engineer, dev-ops, qa. The reviewers are code, security, ui.
> Six agents are write-less, not seven.

No file ever has two writers: for the write-less tiers the orchestrator is the single writer;
ownership stays logical rather than mechanical.

**It composes with hierarchy for free.** Under hierarchical mode a worker's DIGEST goes to its lead,
not the orchestrator — but `expertise_update` rides the **per-member block** the consolidated DIGEST
already carries for `STATE.md` granularity (§2.3). No new channel. And because the DIGEST is
persisted via `digest_ref` before the orchestrator acts (§11.4), an interrupted run can replay the
update rather than lose it.

### 5.4 Overflow and curation

**On overflow the rule is condense, not truncate** — keep durable patterns, drop incidents;
per-section, so one bad prune cannot gut the file. A section at its cap sets `expertise_full: true`;
**no agent self-prunes on overflow.**

The rule is: **recommendation comes from the tier above; application comes from whoever holds the
pen.**

| File | Overflow recommender | Applier |
|---|---|---|
| **doer** | its lead — reads the member's file + recent DIGESTs, giving it the cross-run view the member lacks; emits a `KEEP`/`DROP`/`MERGE` note | the **doer**, which applies the note verbatim **immediately** — recommendations are binding, since the lead saw the outcomes |
| **reviewer** | its lead (same as above) | the **orchestrator** |
| **lead** | the **orchestrator** — at the CEO briefing it holds all three leads' consolidated DIGESTs at once, so it has the cross-lead view leads have over members, at no extra spawn cost | the **orchestrator** — but it does **not** prune unilaterally: it spawns the lead **immediately** with its recommendation, the lead returns the actual condense ops, and the orchestrator applies them. Judgment stays with the only agent that knows what its entries mean; the pen stays with the writer |

**Curation happens IMMEDIATELY, not at the next natural spawn.** If the member is no longer running,
the lead **spawns it solely to apply the curation note** — a single-purpose spawn that does nothing
else.

The reason is that the recommendation is only as good as the context that produced it. The lead holds
the cross-run view *now* — the member's file, its recent DIGESTs, what actually happened this run.
Deferring to "the member's next delegation" means that context is gone by the time the note is
applied, and either the note has to carry its own justification forward or the lead has to reconstruct
it. A cheap extra spawn is strictly better than a stale or re-derived recommendation. The same applies
one tier up: the orchestrator spawns a lead immediately for its condense ops rather than waiting.

**Curation triggers:** (a) an `expertise_full` flag → curate immediately; (b) a light pass at each CEO
briefing, where the relevant parties are already spawned and reading output.

**Curation of leads is surfaced to you.** Because the three leads are your direct reports, the
briefing carries a compact curation block that **applies unless you object** — you can veto or edit
any line. It is written in **plain English with light technical detail**, not ID shorthand, so it
stays skimmable rather than becoming a review task (§10.3). Curation of *members* does not reach your
briefing; it goes to that member's next spawn.

### 5.5 CEO feedback from the briefing

The briefing is two-way: you give instructions *and* feedback. Feedback is classified, because the
three kinds persist differently:

| You say | Really is | Destination |
|---|---|---|
| *"we also need SSO"* | requirement change | `BRIEF` / `PLAN` via `pm` — **approval-gated** |
| *"eng keeps over-engineering the API"* | craft / behavioral | that **lead's** Expertise |
| *"redo the API step"* | course-correction | orchestrator's next instruction — no persistence |

Mechanism for the behavioral kind (you are not an agent, so you cannot write a lead's Expertise
directly). **This is the case that makes a lead write structurally necessary** — without it,
feedback either never becomes durable or `feedback.md` grows into the archive it is specified not to
be:

1. Orchestrator writes to **`.harness/notes/feedback.md`**, addressed:
   `@eng-lead: prefer the simplest thing that passes`. **Read by the 3 leads at spawn, not by the 12
   workers.**
2. The addressed lead reads it at its next spawn and **acts on it immediately**, in how it delegates
   that run.
3. It returns the durable part as an `expertise_update` op plus `feedback_absorbed: [<entry>]`; the
   orchestrator applies the op (§5.3) and **clears the absorbed entry** — `feedback.md` holds only
   unabsorbed items.

**Feedback addresses LEADS only**, never a member directly — the same rule as delegation. You say
*"frontend work keeps missing accessibility"*; `eng-lead` records it and enforces it in how it
delegates.

### 5.6 Two tiers of Expertise — project and global

| | `.harness/expertise/<agent>.md` | `~/.harness/expertise/<agent>.md` |
|---|---|---|
| Holds | *this codebase* — "migrations fail before the seed script" | **craft that generalizes** — "vague specs cause loop-backs" |
| Scope | one project | all your repos |
| Committed | yes, versioned with the project | no, local to your machine |

Both are read at task start and written by the agent that owns them.

- **Promotion is deliberate, not automatic.** An observation earns a place in the global file only
  after it has held in **more than one project**.
- **Project wins on conflict.** A concrete local observation beats a general heuristic.
- **Global entries stay short.** They are heuristics about *how to work*, never facts about a
  codebase, and they load on every spawn in every repo — so the global cap is tighter than the
  project one.
- **Risk to accept:** a wrong global entry silently misleads every project at once.

---

## 6. Two knowledge tiers — rules vs expertise

| | rule skills (`.claude/skills/harness-<name>/SKILL.md`) | `.harness/expertise/<agent>.md` |
|---|---|---|
| Nature | the **constitution** — how agents must behave | **learned observations** about this codebase |
| Scope | generic, identical in **every** project | per-project |
| Writer | **you**, in the harness repo | the agent itself (or the orchestrator on its behalf, §5.3) |
| Delivery | `skills:` frontmatter — preloaded at spawn (§7) | `SubagentStart` hook injection (§5.1) |
| Deploy | distributed and **overwritten** on every push | never touched |
| Changes | deliberately, human-authored | continuously, self-maintained |

**Rule skills are static — agents never write them.** This is structural: they are distributed, so
an agent's edit would survive until the next `harness-deploy` and then vanish silently. Rules
therefore *cannot* be agent-writable without breaking distribution.

**The eight rules**, each a **flat** skill at `.claude/skills/harness-<name>/SKILL.md` and referenced as
`harness-<name>`:

| Rule | Loaded by | Why |
|---|---|---|
| `handoff` | **all 15** | the return contract and output discipline |
| `expertise` | **all 15** | when and how to update durable knowledge |
| `tdd-enforcement` | 4 feature devs (+dev-ops, exempt on config/scaffolding) | test-first |
| `systematic-debugging` | eng devs in debug mode | root cause before fix |
| `spec-driven` | pm | requirements and decisions discipline |
| `verification-rules` | qa | the test-matrix gate |
| `code-review` | code-reviewer | two-stage review |
| `zero-micro-management` | the 3 leads | delegate, never execute |

Two are universal, so **they load on all 15 agents at every spawn — keep those two shortest.** An
earlier count said "seven" and omitted `systematic-debugging`, which §3.4 has always listed.

**Rules are uniform across all projects — there is no per-project rule overlay.** Project-specific
*values* still vary (`domain` globs, `test_kinds`, §3); project-specific *behavior* does not.

**How a rule improves:** an agent notices a recurring problem → records it in its Expertise →
surfaces at a CEO briefing → **you** decide → you edit the rule in the harness repo → deploy pushes
it everywhere.

---

## 7. Rule delivery — native `skills:` preload

Each rule is a **skill**, and each agent declares the rules it is bound by in its `skills:`
frontmatter field. Claude Code injects the **full skill content** into the subagent's context at
spawn — not just the description.

```yaml
---
name: harness-backend-dev
skills:
  - harness-handoff              # universal — all 15
  - harness-expertise            # universal — all 15
  - harness-tdd-enforcement      # role-specific
---
```

**This makes rule delivery a runtime guarantee rather than an act of obedience.** There is no
`## Discipline` step-0 instruction to skip, and no `<files_to_read>` belt-and-suspenders is needed — <!-- ok-stale -->
the rule is in context before the agent takes its first action.

Consequences of the mechanism, stated plainly:

- **Rules load unconditionally.** `skills:` has no "use-when" laziness — every listed rule costs its
  full length on every spawn of that agent. Rules must therefore stay short, and an agent lists only
  the rules that genuinely bind it.
- **Each rule needs a skill directory** with a `SKILL.md`, rather than being a bare `.md` file.
- **Agents can still reach unlisted skills** through the `Skill` tool; `skills:` governs what is
  *preloaded*, not what is *reachable*.
- **`Skill` does not belong in `tools:`** for preloading purposes — the `skills:` field is the
  mechanism.

Rules remain single-sourced and distributed (§6), so an agent's rule set is a declaration, not a
copy.

---

## 8. Handoff contract

**Handoff is by file path, never by conversation** — fresh-context subagents cannot inherit history
and should not. Each persona *writes* a durable artifact and *returns* a compact signal.

**The three-part return (all 15 personas, leads included):**

```
VERDICT: PASS | FAIL | BLOCKED | ESCALATE   # control — drives DAG transitions
                                    #   PASS    = done (may carry advisory notes)
                                    #   FAIL    = gate failed → retry/loop_back is meaningful
                                    #   BLOCKED = cannot proceed → loop-back is futile, escalate
                                    #   ESCALATE= surface to the tier above (lead→orchestrator→user)
DIGEST:                             # routing — orchestrator reads THIS, not the artifact
  headline: <one-line BLUF>
  <persona-specific routing fields>
  open_questions:                   # a LIST of structured items, never a count
    - { id: Q1, question: "<text>", blocking: true, options: [...] }
  files_touched: [<paths>]          # doers only
artifact: <path>                    # the focal, high-SNR handoff doc — read by the CONSUMER persona
```

- The artifact is the focal point, high signal-to-noise — full content stays on disk, read only by
  the downstream persona that needs it. **Never pasted into a return.**
- **The orchestrator never opens member artifacts** — it routes on VERDICT + DIGEST only. A **lead
  may** read its members' artifacts, and must, in order to assess.

### 8.1 DIGEST schemas are NORMATIVE

The runner routes on these exact field names and enum values, so they are a contract. Field names
and enums may not drift per persona.

- **pm** (both phases): `feasibility: clear|risky|blocked`, `surface: S|M|L`,
  `flags: [security, migration, external-api, …]`, `recommend: proceed|spike|reframe|halt`,
  `tasks: <n>`, `decisions: <n>`, `needs_approval: bool`, `risk: low|med|high`
- **eng devs** (frontend / backend / ai / data): `tests_added: <n>`, `suite: pass|fail`,
  `blocked_on: <text|none>`
- **qa:** `suite: pass|fail`, `failures: <n>`, `coverage_gaps: [<area>]`, `matrix_ok: bool`
- **reviewers** (code / security / ui): `severity_max: info|low|med|high|critical`, `findings: <n>`,
  `must_fix: [<item>]`
- **visual-designer:** `contract: written|updated`, `mockups: [<paths>]`,
  `direction_choices: [<…>]`
- **documentor:** `docs_updated: [<paths>]`, `gaps: [<…>]`
- **dev-ops:** `change_type: config|scaffolding|infra|ci`, `applied: [<paths>]`,
  `suite: pass|fail|n/a` (TDD-exempt work reports `n/a`)
- **leads:** the **consolidated DIGEST** schema in §10.4 is their persona schema — they are not
  exempt from the three-part return

All personas additionally carry `expertise_updated` and, when applicable, `expertise_full` (§5).

### 8.2 Conditional routing

- pm `flags: [security]` → orchestrator inserts `security-reviewer` before build
- pm `recommend: spike` → halt to user, don't build yet
- pm `feasibility: blocked` → halt
- qa `suite: fail` → loop back to the dev

### 8.3 Malformed or missing return

If a member returns no `VERDICT`, an unparseable `DIGEST`, or nothing at all, the host
**re-prompts that step once**, asking only for the contract block. On a second failure it records
`VERDICT: BLOCKED (contract violation)` and escalates. **The host never guesses a verdict** —
silent misrouting is worse than a halt.

### 8.4 Artifact output discipline — `rules/handoff.md`

A **universal preamble read by every agent** (all 15), *in addition to* any role-specific rule:

- **BLUF** — lead with the conclusion or recommendation, not the process. No "I explored X then Y."
- **Claims + pointers, not payloads** — "Auth is JWT (`auth/mw.ts:42`)", never pasted code.
- **Explicit "Open Questions / Decisions Needed"** — the consumer's to-do, called out.
- **Bounded length** (≈ one screen) — the cap forces prioritization; length is the enemy of signal.

It also carries the autonomy-by-reversibility rule (§4.4).

### 8.5 Output classes

Two classes of doer output:

- **Document-producers** (pm): the artifact **is** the deliverable — consumed directly. They declare
  run-dir `outputs:`.
- **Repo-mutators** (eng devs, qa, documentor, visual-designer): the deliverable is
  code / tests / docs / `DESIGN.md` **on disk**. They declare `output_class: repo`, and their DIGEST
  carries `branch` + `files_touched` instead of run-dir files (the crew `outputs:` field is
  meaningless for them).

Repo-mutators hand off via a pull request. One branch per feature; devs → code commits, qa → test
commits, documentor → doc commits, all to the same branch, **strictly serial** (a schema constraint,
not a convention — parallel writers on one branch would collide). Eng-lead routing guarantees two
specialists never own the same file.

### 8.6 Git and PR lifecycle

- **Branch creation:** the **orchestrator/host** creates `harness/<slug>` *before* the first
  mutating step. Not a worker's job.
- **Ground-truth diff for reviewers:** `git diff <base>...<review_sha>` **locally** — no `gh`, no
  network, no auth dependency. Reviewers do **not** require a live PR to review.
- **PR creation:** a single **orchestrator step at the end of a passing crew** (`gh pr create`), not
  per-worker. If `gh` is unavailable or unauthenticated → the crew still succeeds; report the branch
  and skip PR creation (soft skip, not a halt).
- **Merge is USER-GATED by default.** The orchestrator never auto-merges `main`. `harness.json` may
  opt into autonomous merge per-project, but the default is: gates pass → surface for approval.
- **Git failure modes** (dirty tree, no remote, branch exists, merge conflict, detached HEAD): the
  host halts the crew with `VERDICT: BLOCKED` and reports the git state. **Never force, never
  auto-resolve conflicts.** The dirty-tree check uses a **whitelist**: harness-owned paths and
  in-progress staged work do not count as dirty.

---

## 9. Test guardrails

Owned by **`harness-qa`**, enforced against the PR diff. Discipline lives in
`rules/verification-rules.md`; the matrix data lives in `.harness/harness.json`.

**The matrix is a floor, not a ceiling.** The static change-type → required-test-kinds table sets
the baseline; qa may *add* requirements it infers from the diff. It never drops below the matrix.

| Change type | Unit (TDD) | Functional | Integration | UI / Playwright |
|---|:---:|:---:|:---:|:---:|
| logic / util / algorithm | ✅ | — | — | — |
| api (endpoint / service) | ✅ | ✅ | if touches DB/external | — |
| cross-module / data-flow | ✅ | ✅ | ✅ | — |
| frontend component | ✅ | component | — | if interaction flow |
| feature (UI + API) | ✅ | ✅ | ✅ | ✅ |
| bugfix | ✅ (regression reproducing bug) | if functional | if integration | if UI |
| config / scaffolding / docs | exempt | exempt | exempt | exempt |

`harness.json` schema. **Conditionals are structured predicates, not prose** — otherwise the
table's "if touches DB/external" cells silently vanish and high-risk changes ship untested:

```json
"test_matrix": {
  "logic":        { "always": ["unit"] },
  "api":          { "always": ["unit","functional"],
                    "when": [{ "kind":"integration", "if":"touches_db_or_external" }] },
  "cross_module": { "always": ["unit","functional","integration"] },
  "frontend":     { "always": ["unit","component"],
                    "when": [{ "kind":"ui", "if":"has_interaction_flow" }] },
  "feature":      { "always": ["unit","functional","integration","ui"] },
  "bugfix":       { "always": ["unit"],
                    "when": [{ "kind":"__bug_class__", "if":"match_bug_class" }] },
  "config": { "always": [] }, "scaffolding": { "always": [] }, "docs": { "always": [] }
},
"test_kinds": {
  "unit":        { "detect": "tests/unit/**|*.test.*|*_test.*", "cmd": "<project test cmd>" },
  "functional":  { "detect": "tests/functional/**",             "cmd": "..." },
  "integration": { "detect": "tests/integration/**",            "cmd": "..." },
  "component":   { "detect": "**/*.spec.tsx",                   "cmd": "..." },
  "ui":          { "detect": "tests/e2e/**|*.spec.ts",          "cmd": "playwright test" }
}
```

- **Predicate evaluation** is qa's judgment against the diff, but the *predicate names are fixed
  data* so behavior is auditable (`touches_db_or_external`, `has_interaction_flow`,
  `match_bug_class`).
- **`test_kinds` supplies two things** without which "missing required kind → FAIL" is not
  computable: how to *detect* a kind's presence in a diff (`detect` globs), and *what command runs
  it* (`cmd`, per project).
- **Owner: `dev-ops`.** During `/harness-init`, dev-ops detects the project's test runner and writes
  `test_kinds` into `.harness/harness.json`. **An unresolvable or missing `cmd` is a distinct LOUD
  third state** (`VERDICT: BLOCKED — test command unresolved`), never folded into the
  not-applicable soft skip: a silently no-op'd hard gate is worse than a halt.
- **Bug-class mapping:** a bugfix's regression test must match the bug's class — a functional bug
  needs a functional regression, a UI bug a Playwright one.
- **Change type per task:** pm tags each PLAN task with `change_type:` (§2); qa reads it and applies
  the matrix. A task missing `change_type` blocks the gate (§2.2).
- **Not-applicable tooling is a soft skip, not a failure:** no web project / no dev server /
  Playwright absent → qa records `ui: skipped (no browser target)` and does **not** FAIL.
- **Hard gate:** a missing required test kind → `VERDICT: FAIL`, loop back to the dev. Enforced
  against the PR diff, not a self-report.
- **TDD-coverage audit:** beyond running the suite, qa verifies every behavioral change in the diff
  has a test that covers it, written test-first.
- **UI/Playwright is in scope:** qa runs real browser-driven E2E for UI features.
### 9.1 AI/LLM behavior — `ai-dev` authors the eval, `qa` owns the gate

Prompt, model and agent changes are not covered by the ordinary change types — a prompt edit is not
logic, api, frontend or config. They get their own row and their own required kind, so an AI change
with no eval fails the qa gate exactly as a missing unit test does:

| Change type | Required | Notes |
|---|:---:|---|
| `ai_behavior` (prompt / model / agent / tool-definition change) | `eval` | plus `unit` for any deterministic scaffolding around it |

```json
"ai_behavior": { "always": ["eval"],
                 "when": [{ "kind":"unit", "if":"has_deterministic_wrapper" }] },
"test_kinds": {
  "eval": { "detect": "evals/**|*.eval.*", "cmd": "<project eval runner>" }
}
```

**The division of labour mirrors every other change type** — the specialist authors, the validator
gates:

| Who | Owns |
|---|---|
| **`ai-dev`** | **Authors** the eval: the failure modes that matter, the rubric, the reference dataset, the pass threshold. This is domain work — only the agent that wrote the prompt knows what "wrong" looks like for it. |
| **`qa`** | **Owns the gate.** Runs the eval, enforces its presence via the matrix, and reports the result in `suite` / `matrix_ok` like any other kind. qa does **not** author rubrics — it enforces that one exists and that it passed. |
| **`validator-lead`** | Assesses eval *adequacy* in its panel synthesis — "this eval passes but only covers the happy path" is a finding, not a gate. |

This keeps authorship separate from audit (§3) and makes the eval a hard gate rather than a
qualitative opinion.

**Honest limits, since a passing eval is weaker evidence than a passing unit test:**

- **Non-determinism means a threshold, not a boolean.** An eval passes at a rate against a dataset;
  `pass_threshold` lives with the eval, and qa reports the measured rate, not just pass/fail.
- **A green eval bounds only what the dataset covers.** Coverage gaps go in qa's `coverage_gaps` the
  same as untested code paths.
- **Production monitoring and guardrails are still out of scope for v1.** The gate proves a change did
  not regress the reference set; it does not watch live behavior.
- **The reflexive case remains awkward:** the harness building *itself* is an LLM-behavior system, and
  its own agents are now gated by evals its own `ai-dev` writes. That is an improvement over passing
  on judgment alone, not a resolution.

---

## 10. The orchestrator

**Definition:** the orchestrator holds the project's context, delegates to individual agents and to
agent teams, receives their feedback, makes priority adjustments, and repeats. It plays a
project-management *function*, but it is **not** named "PM" — that belongs to the `harness-pm`
persona. The orchestrator is not a persona at all.

**There is one orchestrator, at two delegation granularities:**

- **The orchestrator = the main session** following the `/harness` playbook. It is *not* a subagent
  and *not* a persona `.md` — it is a skill the main session runs (it must hold the spawn tool to
  delegate).
- **"The runner" is not a separate actor** — it is the orchestrator's *delegate-to-a-team*
  subroutine (`crew/SKILL.md`). Delegating to one persona = spawn directly; delegating to a team =
  run that crew's DAG.

### 10.1 The loop

1. **Read context** — `BRIEF` + `PLAN` + `STATE`, held **on disk, re-read each cycle** (thin,
   resumable — recovers after a context reset).
2. **Decide next** — next task / persona / team per PLAN order + any pending adjustments.
3. **Delegate** — hand a whole crew to its named lead, or a single task to the lead that owns the
   relevant persona. Never to a worker directly (§10.2).
4. **Receive feedback** — collect each `VERDICT` + `DIGEST`.
5. **Adjust** — log to `STATE`; route (loop-back, insert a gate, escalate, or send **pm** to
   re-plan).
6. **Loop** — until PLAN is done, blocked, or awaiting the user.

**Authority boundary:** the orchestrator makes *execution-time* adjustments (loop-back, insert a
review, reorder, escalate); *plan-level* changes (new tasks, changed decisions) are delegated to
**pm**. The orchestrator conducts; it does not re-plan. "Who owns `PLAN.md`" stays unambiguous.

### 10.2 Org shape — hierarchical, one nesting level

> **Verified (DEC-100, DEC-102): hierarchical works. The flat fallback is not needed.** A subagent
> spawned three subagents in one turn and all three returned.
>
> **`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "2"` encodes this org exactly** — depth counts layers *below*
> the main conversation:
>
> ```
> main session (orchestrator)   layer 0 — not counted
>   └─ leads                    layer 1   ✓ can spawn
>       └─ team members         layer 2   ✓ run, but cannot spawn
>           └─ anything         layer 3   ✗ unreachable
> ```
>
> **"Workers are always leaves" is therefore enforced by the platform, not by our agent files.** At the
> depth limit Claude Code *withholds* the `Agent` tool — stripped from the loaded list and the deferred
> pool alike — so a worker cannot delegate even if `Agent` were granted in its frontmatter. The failure
> mode is benign: it finds no tool and does the work itself rather than erroring.
>
> The setting must be present. Absent it, the current default of **3** lets workers delegate — the
> opposite of the guarantee (DEC-83). `check-state.sh` INV-9 verifies it, and omitting `Agent` from worker
> `tools:` is retained as redundant-but-explicit belt-and-suspenders.

- **orchestrator** (main session): delegates a *whole crew* to that crew's named lead, or a *single
  task* to **the lead that owns the persona for that task** — never to a worker directly.
  **There is no orchestrator→worker path.** Even a one-task request enters through the relevant lead,
  which matches the task to a member by `consult-when` and delegates. This keeps one rule with no
  exception: the orchestrator talks to leads; leads run their squads.
  - *Why no shortcut:* a direct-to-worker path would bypass the lead's routing, its assessment of
    the result, and its Expertise — the three things a lead exists for. It would also give the same
    work two possible shapes depending on how it was requested.
  - *Cost accepted:* one extra spawn for trivial single-task work. In exchange, `STATE.md` sees a
    uniform stream of consolidated DIGESTs, and no work is ever unassessed.
- **Three domain leads** — `product-lead`, `eng-lead`, `validator-lead`. Each is granted the spawn
  tool. **The crew's `lead:` field selects which one hosts that crew's DAG** — there is no generic
  lead parametrized per crew. The host reads `crew/SKILL.md`, spawns its squad members, runs the DAG
  (gating and loop-backs within the crew), and returns a **consolidated DIGEST** up.
- **Workers** (doer and reviewer personas): spawned by the host lead. **Always leaves.**

**What the leads are FOR: they MANAGE.** A lead receives a request in its domain, identifies which
specialist should do the work, **spawns that member and delegates the task**, then assesses the
result and reports up. The canonical flow:

```
You: "change the UI so X"
  → orchestrator: recognizes this is engineering → delegates to eng-lead
      → eng-lead: identifies this as a UI task
          → SPAWNS harness-frontend-dev, delegates the task
          ← frontend-dev returns VERDICT + DIGEST + artifact
      ← eng-lead assesses the work, reports one consolidated DIGEST up
  ← orchestrator logs to STATE, decides next step (or briefs you)
```

The orchestrator **monitors** the leads; the leads **run their squads**. The orchestrator does not
reach past a lead into its squad.

**Each lead also reports out** — progress, assessment in its domain, its squad's `open_questions`,
risks and proposed next steps. That reporting feeds the CEO briefing.

**Constraints on the shape:**

- **Exactly one host per crew.** The `lead:` field names it, and that host solely owns the run dir,
  `state.yaml`, cycle counters and the consolidated DIGEST. A crew is never conducted by two leads.
- **A lead may appear as a DAG step in another lead's crew — as a reviewer only.** E.g.
  `plan-feature` (hosted by `product-lead`) has `eng-lead` as an architecture-review step. **In that
  role a lead never routes or spawns** — it behaves as an ordinary leaf reviewer. This preserves one
  nesting level: only the *host* lead spawns.
- **All three leads exist as spawnable personas in BOTH hosting modes.** The spike decides only
  *who hosts the DAG*, never whether leads exist. In flat mode the orchestrator hosts, and
  `eng-lead` (architecture review) and `validator-lead` (panel assessment) are still spawned as leaf
  steps.
- **Keep user-approval steps at crew boundaries, not mid-DAG inside a lead.** A subagent cannot call
  `AskUserQuestion`, so a lead can never pause to ask you. Questions ride up via `open_questions`
  and the *orchestrator* asks.
- **Parallel fan-out from inside a lead is VERIFIED** (DEC-100) — a subagent issued three `Agent` calls
  in a single turn and all three returned. `validator-lead` runs its reviewer panel in parallel; the
  serial fallback and the hand-the-panel-to-the-orchestrator workaround are both unnecessary. Size panels
  against the real limits: **20** concurrent subagents per session, **200** per session in total, with
  nested and background spawns both counting.

**Where the crew-runner logic lives.** The algorithm is single-sourced in `crew/SKILL.md` and hosted
by whoever conducts the crew: the crew's named lead (hierarchical), or the main-session orchestrator
(flat). Same algorithm; only the host differs. In hierarchical mode the orchestrator's context stays
tiny — member spawns and DIGESTs live in the lead's context, and the orchestrator sees one
consolidated DIGEST per crew.

### 10.3 The CEO briefing

Three things trigger it — deliberately *not* every crew completion:

| Trigger | Why |
|---|---|
| **`ship-feature` completes** | the natural ship decision |
| **A lead returns `BLOCKED`** | work cannot proceed without you |
| **On demand** — you ask "where are we?" | the orchestrator is your only interface; you never address a lead directly |

`plan-feature` completing is **not** a briefing — it is the PLAN approval gate. The three
user-facing moments stay distinct: an **approval** signs an artifact, a **question round-trip**
answers one thing, a **briefing** is the consolidated cross-team view plus an instruction request.

How it runs:

1. Orchestrator spawns **all three leads in parallel**: "report on your domain."
2. Each returns progress · assessment · its squad's `open_questions` · risks and proposed next
   steps. **All three always report** — a lead with nothing to say returns "no activity this run,"
   which guarantees a complete cross-team picture with a consistent shape every time.
3. Orchestrator assembles one briefing: each lead's summary, all open questions across teams,
   resolved escalations, proposed next steps, the goal-check result (REQ coverage + SC outcomes), the
   **UAT** if one is required, and the **Expertise curation** block.
4. Writes it to `.harness/notes/ship-review-<FEAT>-<runid>.md`.
5. **Presents it to you and requests instructions.** You decide: ship, fix first, re-scope, or stop
   — and give feedback (§5.5).

**Write it in plain English with light technical detail.** This is the one artifact addressed to a
human rather than to another agent, and the `handoff.md` bounded-length rule applies to it as much as
to a DIGEST. IDs and paths are available as supporting detail; they are not the summary. A briefing
that reads as ID shorthand has failed at its only job.

```
FEAT-01 · SSO login with Google                         branch harness/sso

Product     Plan delivered as scoped. One open question resolved with eng:
            Google-only for v1 (recorded as D-07, needs your sign-off).
Engineering Built across backend and frontend. Two fix cycles — both from
            the qa gate, both closed. No architecture concerns.
Validation  Tests pass, coverage complete. Security clean. One advisory
            note on the UI: focus ring is faint in dark mode. Not blocking.

Goal check  REQ-02 covered. SC-02 met (sign-in flow test passes).
            SC-07 met (no credentials in logs — checked).
            SC-05 needs you: it's a judgement about how the screen feels.

UAT         Ready — 1 step, ~2 minutes.                      << BLOCKING
            Sign in with Google from a signed-out browser and tell me
            whether the screen feels consistent with the rest of the product.

Expertise   Applies unless you object:
            eng-lead — merging two overlapping notes about migrations needing
              the seed script on a cold database; dropping one about a folder
              that no longer exists.
            validator-lead — dropping an old note that a newer one replaced.
            product-lead — nothing to change.

Next        Ship, fix the focus ring first, re-scope, or stop.
```

**Merge is never automatic**; it follows your instruction here. And a feature with an unrun required
UAT cannot be shipped, whatever else is green.

### 10.4 The consolidated DIGEST (the up-channel contract)

```
VERDICT: <roll-up>                  # worst member verdict: BLOCKED > ESCALATE > FAIL > PASS
                                    #   ESCALATE outranks FAIL so a needed user
                                    #   decision is never masked by a fixable failure
DIGEST:
  crew: <name>            steps_run: <n>   cycles_used: <n>
  members:                            # per-member roll-up → orchestrator appends these to STATE.md
    - { step: build, persona: backend-dev, verdict: PASS, headline: "...", files_touched: [...] }
    - { step: qa,    persona: qa,          verdict: FAIL, severity_max: high, must_fix: [...] }
  must_fix: [<union of blocking findings>]
  branch: <branch>                    # if the crew mutated the repo
  open_questions: [<structured items, unioned from members>]
  escalations:                        # §10.5 — routing AND resolution are both recorded
    - { id: E1, raised_by: harness-eng-lead, question: "is partial SSO acceptable for v1?",
        domain: product, routed_to: harness-product-lead,
        resolution: "yes, Google only for v1", decided_by: harness-product-lead,
        recorded_as: D-07 }
  expertise_update: [<ops from this lead, §5.3>]
  sc_status:                          # §11.2 — carried once the goal-check has run
    - { id: SC-02, verdict: met, method: automated, evidence: "e2e/login.spec.ts:14 pass" }
artifact: <run_dir>/SYNTHESIS.md      # the lead's merged report
```

The per-member block is what preserves `STATE.md` granularity under hierarchy.

**Escalations are recorded, not just routed.** An `escalations` entry captures the question, the lead
that raised it, where it was routed, **and how it was resolved** — so a lateral lead-to-lead decision
leaves a durable trace instead of living only in one lead's context. Two rules follow:

- **A resolution that changes the plan must be promoted.** If the answer is a real architectural or
  scope choice, `recorded_as` names the resulting `D-NN` in `PLAN.md ## Decisions`, and it is
  approval-gated like any other decision. An escalation resolution is **not** a back door around your
  approval.
- **Resolutions are logged.** The orchestrator appends each to `.harness/logs/<date>.md`, so "who
  decided this, and when" is answerable later without replaying a run.

### 10.5 Escalation terminus

`lead → orchestrator → user`.

- A member returns `BLOCKED` / `ESCALATE`, or `max_cycles` is exhausted → the lead stops that branch
  and rolls it up.
- The orchestrator's rules on receiving an escalation:
  - **`BLOCKED`** → surface to the user (a blocked worker cannot be fixed by retrying)
  - **`FAIL` with `must_fix`** → delegate a fix cycle
  - **plan-level defect** (wrong tasks or decisions) → delegate to **pm** to re-plan
  - **ambiguity or a needed decision** → surface to the user
- The orchestrator never silently retries past the crew's `max_cycles`.

**When `max_cycles` is exhausted — exactly what happens.** Two counters exist and they bound
different things: a step's `cycles` in run `state.yaml` (per-step retries) and the feature's
`cycles_used` / `max_total_cycles` in `feature.yaml`, which bounds the fix loop **across runs**
(§11.5). Exhausting either terminates the loop, and the sequence is:

1. **Stop that branch.** No further retry of the failing step. Other independent branches of the DAG
   are allowed to finish — exhaustion fails a branch, not necessarily the whole crew.
2. **Preserve everything.** The run's `state.yaml` keeps the per-step history; the branch and all
   commits stay; nothing is reverted or abandoned. The feature's `status` stays `in_progress` — it is
   **not** set to `abandoned`, because that is your call, not the orchestrator's.
3. **Roll up `VERDICT: BLOCKED`** with the accumulated `must_fix`, the number of cycles spent, and
   **what was tried each cycle** — an exhausted loop is only actionable if you can see why it did not
   converge.
4. **Trigger the CEO briefing** (§10.3) — `BLOCKED` from a lead is one of its three triggers.
5. **You decide:** raise `max_total_cycles` and continue, re-scope the feature via `pm`, take the
   partial work, or abandon it.

**A `BLOCKED` feature is reported, not forgotten** — the state-consistency check surfaces it at every
`/harness` entry until you resolve it.

> ⚠️ **It does not, however, mean you can work another feature in parallel.** An earlier draft promised
> "independent features remain workable," which the state model cannot currently support:
> `STATE.md ## Current` is **singular by construction** (§2), mutator serialization is per-crew rather
> than cross-feature, and two features in flight means two branches diverging from `main` with
> committed Expertise files, daily logs and `PLAN.md` task statuses that are guaranteed to conflict at
> merge. **One feature in flight at a time** until cross-feature merge semantics exist (§15). A
> `BLOCKED` feature is therefore a stop-and-decide, not a switch-tasks.

### 10.6 Two orchestration modes, one contract

- **Crew mode (declarative):** the crew YAML fixes the step order; the host executes the DAG.
  DIGEST-predicate routing applies here too — the host may *insert* a gate (pm `flags:[security]` →
  add `security-reviewer`) or halt, but may **never** reassign step ownership or invent steps
  outside the crew's personas.
- **Ad-hoc `/harness` mode:** the orchestrator reads STATE, then routes the *next* persona using
  VERDICT + DIGEST.

In both, **the orchestrator routes; workers never pick who runs next.**

---

## 11. Features and runs — the execution state model

Three tiers, each with exactly one writer. This exists because an LLM host cannot carry state across
turns: every counter, status and SHA is read from and written to disk, never held in memory.

```
.harness/
  BRIEF.md  PLAN.md              ← project: what & how (pm-owned, approval-gated)
  features/
    FEAT-01-sso/
      feature.yaml               ← feature: live execution state (orchestrator-owned)
      runs/
        2026-07-26-01-product/state.yaml    ← product-lead owned
        2026-07-26-02-eng/state.yaml        ← eng-lead owned
        2026-07-26-03-eng/state.yaml        ← eng-lead owned
        2026-07-27-01-validator/state.yaml  ← validator-lead owned
        2026-07-27-02-eng/state.yaml        ← eng-lead owned (fix cycle)
```

**A feature has N runs, and runs are per-squad.** `ls features/FEAT-01-sso/runs/` is the complete
history of that feature, in order, with the squad visible in each name. This also makes every
`state.yaml` **single-writer** — a run belongs to one squad, so one lead owns its file.

**ONE branch and ONE PR per feature** — not per run. All runs for a feature commit to
`harness/<slug>`.

### 11.1 Declaration vs live state

| | `PLAN.md ## Features` | `feature.yaml` |
|---|---|---|
| Nature | **declaration** (intent) | **live state** (reality) |
| Owner | `pm` | **orchestrator** |
| Approval-gated | yes — part of what you sign | no — it is tracking |
| Holds | FEAT-01 is SSO, serves REQ-02, comprises T-04/T-05 | branch, PR, status, runs so far |

`feature.yaml` never restates the declaration; it references `FEAT-01`.

**Feature status lives ONLY in `feature.yaml`.** Tasks keep their own `status:` (they are part of the
plan), but a *feature's* progress is execution reality, so the orchestrator owns it.

### 11.2 Four levels

| Level | Where | Question | Example |
|---|---|---|---|
| **REQ-NN** | `BRIEF.md` | what must the product do? | "Users can sign in with their Google account" |
| **FEAT-NN** | `PLAN.md ## Features` | what unit of work delivers it? | "SSO login with Google" |
| **D-NN** | `PLAN.md ## Decisions` | how, architecturally? | "Use Supabase social login" |
| **T-NN** | `PLAN.md ## Tasks` | what concrete steps? | "Configure Supabase Google provider" |

**The test: a REQ survives changing your mind about implementation.** Swap Supabase for Auth0 and
REQ-02 is unchanged, FEAT-01 is unchanged, but D-03 and several tasks change. A technical dependency
is therefore a **decision**, never a requirement. This matters because `pm` goal-checks **REQ
coverage** against the approved BRIEF (§13): if implementation choices were logged as REQs, the
goal-check would "verify" that you delivered your own technical decisions rather than the outcomes
you committed to — passing green while missing the point.

**FEAT ↔ REQ is many-to-many.** One feature can satisfy several requirements; one requirement may
need several features. So **REQ coverage is computed, never tracked**: REQ-02 is covered when every
FEAT tracing to it has shipped and its Success Criteria pass. No status field on a REQ that can
drift.

```markdown
  # PLAN.md — pm-owned, approval-gated (the DECLARATION)
  ## Features
  - FEAT-01: SSO login with Google
    traces: [REQ-02, REQ-07]        # 1..n requirements
    tasks:  [T-04, T-05, T-09]
                                    # NO status here — see 11.1

  ## Decisions
  - D-03: Use Supabase social login rather than hand-rolled OAuth
    rationale: auth is not our differentiator; Supabase is already our DB
    tradeoffs: ties us to Supabase's provider roadmap

  ## Tasks
  - T-04: Configure Supabase Google provider
    feature: FEAT-01   traces: REQ-02, D-03   change_type: config
    verify: <cmd>      status: done
```

### 11.3 `feature.yaml` — orchestrator-owned, execution facts only

```yaml
feature_id: FEAT-01            # join key ONLY — no name, no traces, no task list.
                               # Those live in PLAN.md, which is what you approve;
                               # duplicating them here would let an agent redefine
                               # what FEAT-01 means without your signature.
branch: harness/sso
pr: 214
status: in_progress | in_review | shipped | abandoned
review_sha: def5678            # pinned per review cycle; branch is feature-level, so this is too
cycles_used: 2                 # fix-loop budget SPANS runs
max_total_cycles: 10
runs:
  - { id: 2026-07-27-01-validator, squad: validator, verdict: FAIL }
  - { id: 2026-07-27-02-eng,       squad: eng,       verdict: PASS }
```

### 11.4 `state.yaml` — that squad's lead owns it

```yaml
schema_version: 1
run_id: 2026-07-27-02-eng
feature: FEAT-01
squad: eng
host: harness-eng-lead
status: running | awaiting_user | blocked | complete | failed
steps:
  - id: build
    persona: harness-backend-dev
    status: pending | dispatched | complete | failed | blocked | skipped
    mutates_repo: true                    # copied from crew YAML
    dispatched_at: 2026-07-27T09:41:02Z   # written BEFORE the spawn
    completed_at:  2026-07-27T09:48:19Z   # written AFTER the return
    cycles: 1                             # per-step retries; the cross-run budget is feature-level
    verdict: PASS
    outputs: [reports/build-notes.md]
    digest_ref: steps/build/digest.yaml   # referenced, never inlined
    commits: [a1b2c3d]                    # attribution for resume
promoted:
  - { file: .harness/PLAN.md, sha: 9f8e7d6, at: <ts> }
open_questions:
  - { id: Q1, step: build, question: "...", blocking: true }
```

### 11.5 Properties this model guarantees

- **Checkpoint-before-dispatch is the core discipline.** `dispatched_at` is written *before*
  spawning a step, `completed_at` *after* it returns. A step with the first and not the second is
  provably **in flight** — which is what makes every recovery case decidable.
- **Dead or malformed host → resume, do not re-prompt** (re-prompting re-runs the whole DAG and
  risks double-commits). Re-spawn the host with `resume_from: <in-flight step>`; it reads
  `state.yaml` for what was dispatched and **`git log` for what actually landed** (`commits:` plus a
  mandatory `[harness:<step-id>]` commit prefix gives per-step attribution). Side effects become
  derivable, not guessed. Honest scope: crews are resumable **at step boundaries**, not mid-step.
- **Retry budget is feature-level, not run-level.** A fix cycle spawns a *new eng run* plus a *new
  validator run*, so the loop spans runs; a counter inside one run's file cannot bound it.
  Exhaustion → `BLOCKED` → CEO briefing.
- **The diff target cannot move.** `review_sha` is pinned at review dispatch; reviewers diff
  `base…review_sha`, never `…HEAD`, so a later commit cannot shift what they are reviewing.
- **Parallel mutators are forcibly serialized.** `mutates_repo` is read during ready-set computation
  — mechanical, not aspirational.
- **Leads write their own run file and nothing else.** `check-domain.sh` grants each lead exactly
  `features/*/runs/*-<its-squad>/**`.

**Retention:** `features/*/runs/**` is git-ignored scratch and prunes on the same schedule as
`logs/` (`log_retention_days`, default 30). `feature.yaml` is **committed**, so the durable record
of what shipped — branch, PR, runs, verdicts — survives pruning.

**Runner invocation contract:** the host is invoked with `(crew, goal)` and optionally
`resume_from: <step-id>` + `answers: <path>`. The latter pair is how the orchestrator re-delegates
after asking the user a member's `open_questions`, and how it restarts an interrupted run — the same
parameters serve both.

### 11.6 Success criteria — the goal of record, and how it is verified

**`goal` resolves to a success-criteria set, not a sentence.** When a host is invoked with
`(crew, goal)`, `goal` is the FEAT plus the `SC-NN` entries its REQs trace to. A crew is **not done
when its steps complete — it is done when its success criteria are met.** A step DAG that ran to
completion with `SC-05: not_met` is a `FAIL` that loops back, not a pass.

This is what makes "keep working until the goal is met" mechanical rather than aspirational, and it is
bounded by exactly one thing: `max_total_cycles` (§10.5). Unmet SC + remaining budget → another fix
cycle. Unmet SC + exhausted budget → `BLOCKED` → your call.

**Every SC declares its verification method when it is authored.** `pm` writes SC into `BRIEF.md`
with a `verify:` field, the same way tasks already carry `verify:`. An SC with no method is not
verifiable and blocks the goal-check — the state-consistency check (§2.2) treats it like a task
missing `change_type`.

```markdown
  ## Success Criteria
  - SC-02: A returning user signs in with Google in under 3 clicks.
    verify: automated        # qa owns the evidence
    evidence: e2e            # which test kind proves it
  - SC-05: The sign-in screen feels consistent with the rest of the product.
    verify: uat              # only you can judge this — goes in the UAT script
  - SC-07: No credentials are written to logs.
    verify: inspection       # security-reviewer owns the evidence
```

| `verify:` | Evidence comes from | Who supplies it |
|---|---|---|
| `automated` | a named test kind's result — unit / functional / integration / component / ui(Playwright) / eval | **qa** |
| `inspection` | a reviewer's finding, cited by file and line | **code-** / **security-** / **ui-reviewer** |
| `uat` | **you**, executing a step in the UAT script | **you**, via pm's script |

**pm validates SC by collecting evidence, not by re-testing.** This is the mechanism that was
previously undefined: `pm` does **not** run tests or form its own opinion of quality. It assembles the
goal-check from what the validators already produced —

1. Read each `SC-NN` and its `verify:` method from the approved `BRIEF.md`.
2. For `automated`: read qa's DIGEST (`suite`, `matrix_ok`, `coverage_gaps`) and the named test
   result. **A passing suite is not automatically a met SC** — pm must find the specific test that
   exercises that criterion. If none exists, the SC is `not_met` and the gap goes back to qa, not to
   you.
3. For `inspection`: read the relevant reviewer's report and cite the finding.
4. For `uat`: write a step into the UAT script (below). It stays `not_met` until you run it.
5. Emit `sc_status` with `met | not_met | partial` **plus the evidence pointer** for each.

Because pm authors the plan *and* runs this check, it is one of the two acknowledged self-review
points (§3) — but note it is the *weakest* form of self-review available here: pm cannot manufacture
evidence, only report what qa and the reviewers produced.

**The UAT — `.harness/notes/uat-<FEAT>.md`, pm-owned.** Any SC marked `verify: uat` produces a step in
a UAT script for that feature:

```markdown
  # UAT — FEAT-01 SSO login with Google
  status: ready          # draft | ready | passed | failed  (pm sets ready; YOU set passed/failed)
  branch: harness/sso    # where to run it
  setup: `pnpm dev`, then open http://localhost:5173

  ## Steps
  - U-01 (SC-05): Sign in with Google from a signed-out browser.
    expect: you land on the dashboard, and the screen looks like the rest of the product.
    result:              # you fill this in
```

- **pm decides when the UAT is ready** — that is pm's call, not the orchestrator's and not a lead's.
  A UAT is `ready` only when every `automated` and `inspection` SC has already passed, so you are
  never asked to hand-test a feature whose tests are red.
- **It is a blocking gate inside the CEO briefing** (§10.3): a feature with any `verify: uat` SC
  cannot ship on an unrun UAT. Your pass/fail *is* the ship instruction — one user-facing moment, not
  two.
- **A failed UAT step is a `FAIL`, not a discussion.** It loops back through the orchestrator to the
  responsible squad with your `result:` text attached, and consumes a cycle from
  `max_total_cycles`.
- The file is committed, so what you accepted and when is part of the record.

---

## 12. Crew schema and runner

**Config format: YAML, one file per crew**, at `.claude/skills/harness/crews/<name>.yaml` — which
rides the existing skill distribution. Crews are DAG-shaped data, support comments, and are
LLM-parsed at runtime with no build step.

```yaml
name: ship-feature
purpose: One-line description (shown in listings).
lead: eng-lead                     # REQUIRED — which domain lead hosts this DAG (§10)
inputs: [goal]                     # crew-level args, injected as {{goal}}
steps:
  - id: plan
    persona: pm                    # -> subagent_type harness-pm
    depends_on: []                 # empty = root; DAG drives ordering + parallelism
    inputs: []                     # prior outputs, referenced as <step_id>.<filename>
    outputs: [notes.md]            # transient step outputs, written to the step dir
                                   # (canonical files like PLAN.md/BRIEF.md/DESIGN.md are
                                   #  written IN PLACE by their owner — never staged here)
    mutates_repo: false            # true forces serialization (§11.5)
    prompt: Produce a plan for {{goal}}. Write PLAN.md.
    on_fail: { action: halt|loop_back|continue, to: <step>, feed: [self], max_cycles: 3, then: escalate|halt }
```

- **`inputs: [goal]` resolves to a success-criteria set** (§11.6), not a sentence. The crew is done
  when its SC are met, not when its steps complete: a DAG that finished with an unmet SC is a `FAIL`
  that loops back, bounded only by `max_total_cycles`.
- **Parallelism is implicit:** steps whose deps are all satisfied and that do not depend on each
  other are dispatched in one assistant turn. The default concurrent-subagent limit is **20** per
  session (tunable via `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`), and a session may spawn **200**
  subagents in total by default (`CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`) — nested and background
  spawns both count.
- **State passing by file path only:** the runner resolves `plan.PLAN.md` →
  `<run_dir>/plan/PLAN.md` and injects the *path*; the persona reads it. Returns are control-flow
  only.
- **Gating loop-back:** a failed reviewer re-runs **the step that produced the failing
  `files_touched`** (with five specialists there is no single `build` step) with the review report
  injected (`feed: [self]`); the cycle counter lives in run `state.yaml`; on `max_cycles` →
  `escalate` / `halt`.

### 12.1 The runner

The runner is a **skill** at `.claude/skills/harness/crew/SKILL.md` with the algorithm inline —
**not a command**, because commands do not distribute. Its host is the crew's named `lead:`
subagent (hierarchical) or the main session (flat); the algorithm is identical either way.

1. Resolve crew YAML.
2. Create the run workspace `.harness/features/<feat>/runs/<date>-<seq>-<squad>/` + per-step dirs +
   `state.yaml` (§11).
3. **Checkpoint-before-dispatch:** write `step X dispatched` to `state.yaml` *before* spawning, and
   `step X complete` after. Cycle counters are **read from and written to `state.yaml` on every
   iteration** — never held in the host's memory.
4. Loop: compute ready set → dispatch the whole ready set in one turn (one spawn per step,
   `subagent_type: harness-<persona>`, prompt = goal + resolved input paths + required output paths
   + discipline rule path) → collect returns → **evaluate `on_fail` against VERDICT *and* DIGEST
   predicates** → repeat until done or halt.
5. **Promotion is not needed for canonical files** — their owners write them in place (§2.3). Only
   if a crew deliberately stages a canonical file in a run dir must it be promoted *before* any
   consumer step dispatches.
6. Report per-step verdicts + run dir.

**Invocation UX:** the primary entry is the crew skill (triggers on "run the X crew" / "assemble a
crew to…", taking crew name + goal). No crew name → the runner scans `crews/*.yaml` and lists
`name` + `purpose` — the filesystem is the registry. **Crew resolution precedence:** project-local
`crews/` overrides global.

---

## 13. Crew catalog

Crews are the lifecycle. **Flat and standalone in v1** — no sub-crew composition. Each crew names
the lead that conducts it. Panel membership is crew config; reviewers self-scope. ★ = v1 core.

| Crew | Conducted by | DAG | Gates / notes |
|---|---|---|---|
| ★ **plan-feature** | product-lead → eng-lead | `pm → eng-lead(architecture review) → visual-designer(design pass) → ui-reviewer(A)` | pm researches *and* plans in one context. eng-lead reviews architecture. **visual-designer runs the design pass and decides whether the feature requires end-user interaction** — if so it builds a **high-fidelity prototype** (§13.1). ui-reviewer(A) checks the contract is sound. Terminates in **one approval: you sign PLAN *and* prototype together** |
| ★ **ship-feature** | orchestrator monitors; **eng-lead** and **validator-lead** each run their own squad | `{specialist devs, matched by consult-when} → qa → {code ∥ security ∥ ui} → validator-lead assesses → pm(goal-check) → documentor → ⟨CEO briefing⟩` | **Multi-squad, so the orchestrator sequences the squad segments** and each lead runs its own. No lead ever spawns outside its squad; the orchestrator owns the **branch and the feature-level cycle budget** across segments, while **each squad segment gets its own run dir owned by that squad's lead** (§11.4) — there is no shared run dir, which is what keeps every `state.yaml` single-writer. **Precondition: BRIEF *and* PLAN both approved.** eng-lead routes each task to a specialist by `consult-when`, then spawns and delegates. qa gates (writes + runs tests, `test_matrix` hard gate) → `loop_back` → dev. validator-lead assesses the panel into one actionable set. **pm goal-checks delivery** (REQ coverage + SC outcomes) — kept out of the quality panel so "did we deliver?" is not averaged with code nits. Terminates in the **CEO briefing** (§10.3); PR and merge follow your call, never automatically |
| ★ **debug** | eng-lead | `pm(research) → specialist(debug mode) → qa → {code}` | pm reproduces and localizes; eng-lead routes the fix to the right specialist under `systematic-debugging`; qa loops back to the dev |
| ★ **review-team** | validator-lead | `{code ∥ qa ∥ security ∥ ui} → validator-lead assesses` | Panel from crew config; reviewers self-scope; **validator-lead assesses and synthesizes** one feedback set. **Advisory: does NOT fix or merge** — it returns `must_fix`; the caller owns remediation (`ship-feature` loops its dev; standalone, the orchestrator delegates a fix) |
| understand-codebase | product-lead | `{pm×N by disjoint area} → documentor` | fan-in (deferred). N pm instances scoped to disjoint areas writing separate `notes/research-<area>.md`; none may write `PLAN.md` |
| docs-refresh | product-lead | `pm(research) → documentor → code-reviewer` | deferred |

### 13.1 The high-fidelity prototype gate

**Any feature requiring end-user interaction must have a high-fidelity prototype you have approved
before it can be built.** This is a hard precondition on `ship-feature`, not a suggestion.

| | |
|---|---|
| **Who decides it's needed** | `harness-visual-designer`, during the design pass in `plan-feature`. The design pass sits at the end of the product planning cycle, so the call lands *before* any build and *inside* what you approve |
| **What "high fidelity" means** | Interactive and real enough to judge the experience — built on the team's design-system convention (§3.2), not a static image and not a wireframe. Throwaway mockups remain a separate, ungated exploration tool |
| **Where it lives** | `.harness/notes/prototypes/<FEAT>/` — committed, so what you approved is on the record |
| **How you review it** | Published as an Artifact where the project supports a single-file build, otherwise run locally with instructions in the crew's report |
| **Approval** | Bundled with PLAN approval — one signature covers plan and prototype |

**Why one approval rather than two:** the prototype and the plan answer the same question from two
angles — *are we building the right thing?* Splitting them would interrupt you twice for one decision,
and would let a plan lock while its own user experience was still unsettled.

**Consequences to accept:**

- `plan-feature` gets materially longer for user-facing features. Non-interactive features
  (`needs_prototype: false`) skip the design pass entirely and are unaffected.
- **The trigger is a judgment call, made by one agent.** visual-designer decides, which means it can
  be wrong in both directions. Mitigation: the decision and its reason are in the crew's DIGEST and
  therefore in front of you at the approval gate, so you can demand a prototype it did not think
  necessary — or waive one it did.
- A rejected prototype loops back inside `plan-feature` and consumes a cycle; it does not reopen the
  whole plan unless the rejection is about scope rather than execution.

**`validator-lead` assessment is the synthesis step.** Panels need no `harness-synthesizer` and no
generic lead to consolidate — running the panel and assessing its feedback is the validator lead's
defining job. This holds in flat mode too, so synthesis has a named owner by construction.

**Lead-to-lead escalation.** A lead that hits a question outside its domain returns it via
`open_questions`; the orchestrator routes it **laterally to the right lead** rather than to you:
eng-lead hits a product ambiguity → product-lead; validator-lead finds a spec gap → product-lead;
product-lead needs feasibility input → eng-lead. Only genuinely user-level decisions (goal, scope,
approval, merge) reach you.

**Domain responsibility:**

- **You (CEO)** → the goal. Define it, approve BRIEF/PLAN, own the merge.
- **product squad** → *what* to build (pm), how it looks (visual-designer), how it's explained
  (documentor).
- **eng squad** → *how* it's built (5 specialists) + architecture review (eng-lead).
- **validator squad** → *is it right* — coverage (qa), spec + quality (code), threats (security),
  visual fidelity (ui).

**Goal-checking uses two units**, because prose "achieves the goal" is unfalsifiable:

- **REQ coverage** — every `REQ-NN` traceable to shipped code via the PLAN's `traces:` field. Proves
  nothing was dropped.
- **SC outcomes** — each `SC-NN` verified `met | not_met | partial` **with evidence**. Proves the
  outcome landed.

Feature goal → `pm` · architecture → `eng-lead` · coverage → `qa` · security →
`security-reviewer`. All anchor to the **user-approved** BRIEF; an unapproved BRIEF blocks the check.

**The review panel is listed in both `ship-feature` and `review-team`.** That duplication is
accepted in v1 (see DEC-54).

---

## 14. Composability

**v1:** personas are stateless and name-referenced, therefore reusable across crews and repeatable
within a crew — e.g. `ui-reviewer` runs twice, mode A pre-build and mode B post-build. This is the
whole of composability in v1.

**Post-v1 (out of scope for v1, specified here so it is not re-litigated):** sub-crews resolve by
**flattening** the child DAG into the parent at load time — ids namespaced, edges rewired — never a
nested runner. That is what would remove the accepted panel duplication (§13). It is not built in
v1; the runner algorithm (§12.1) has no flattening step.

**Hard limit:** a crew is launched by the orchestrator (main session) or conducted by a lead —
**never from inside a worker persona.** Workers are leaves; one nesting level.

---

## 15. Operating constraints

Every guarantee in this document assumes an operating envelope that was previously implicit. Stating it
is not a limitation admitted late — it is the difference between a constraint and a latent bug.

### 15.1 Single operator, single session

**The harness is single-operator by design.** Every "single writer" guarantee means *one agent in one
session on one machine*. Two terminals means two orchestrators, and therefore two writers for
`STATE.md`, `feature.yaml`, `logs/` and committed Expertise files. There is no lock file anywhere.

Two developers is out of scope for v1. If it is ever needed, the minimum is an advisory lock on
`.harness/` plus per-operator run-dir namespacing — not a small change.

### 15.2 One feature per worktree

An earlier draft said "one feature at a time." **That is wrong, and the pilot host already disproves
it** — `kaya-ai` runs three concurrent `git worktree`s on three feature branches, which is how its
operator actually works.

The resolution is that **a git worktree is the unit of concurrency**, because each worktree has its own
working tree and therefore **its own `.harness/`**:

| | |
|---|---|
| **Within a worktree** | `STATE.md ## Current` being singular is *correct* — one feature, one in-flight run, no ambiguity |
| **Across worktrees** | Features are genuinely independent. Mutator serialization is per-crew, which is sufficient because the crews are operating on different checkouts |
| **At merge** | Ordinary git conflict resolution, no special machinery |

So: **one feature per worktree, as many worktrees as you like.** `.harness/` is per-worktree state, not
per-repository state.

**What this does NOT solve — the honest residue:**

- **Committed Expertise files diverge and will conflict.** Two worktrees whose agents both learn things
  produce competing edits to `.harness/expertise/<agent>.md`. Resolvable by hand, but it is real
  friction, and merging Expertise is not like merging code — the "right" merge is usually the union,
  which no tool will pick for you.
- **The global Expertise tier is shared across every worktree simultaneously** (`~/.harness/`), with no
  locking. Two concurrent sessions can both write it.
- **`logs/` diverge** per worktree. Harmless, but the daily log stops being a single timeline.

A `BLOCKED` feature therefore blocks *its worktree*, and you may work another (§10.5).

### 15.3 Your own hands on the code — the day-one case

**You will edit a file directly, mid-feature.** Nothing in the design accounted for this, and two
mechanisms actively punish it:

- §8.6 halts a crew with `VERDICT: BLOCKED` on a dirty tree — so **your uncommitted edit deadlocks the
  system**.
- A manual commit to the feature branch lands **unreviewed and unattributed** between pinned
  `review_sha` values, invisible to the reviewers and to the qa matrix gate, both of which work from
  the diff.

Human edits therefore get a **legal path** rather than being treated as corruption:

| Rule | |
|---|---|
| **Commit them, attributed** | `[harness:human]` prefix, mirroring `[harness:<step-id>]`. This makes hand edits visible to the same `git log` attribution that recovery already depends on (§11.5) |
| **The state check reconciles them** | at `/harness` entry, any `[harness:human]` commit on the feature branch since the last pinned `review_sha` is reported, and `review_sha` is re-pinned so the next review actually covers your change |
| **Never silently in-scope** | your edit does not inherit a passing review. It re-opens the reviewer and qa gates for the affected paths |
| **The dirty-tree whitelist is defined** | `.harness/**` plus any path you have staged. Unstaged edits outside `.harness/` still halt — that is the signal that something is mid-flight, and it is correct |

The one thing that must never happen is a hand edit being *ignored*: shipping on a green review that
never saw your change is worse than halting.

### 15.4 The claim, restated honestly

The design's value claim is "Claude executes reliably at each stage without constant supervision."
Given 4–8 blocking touchpoints per feature (§10.3, §11.6, §13.1, and the question round-trip in §2.1),
the accurate claim is **"without *mid-stage* supervision"** — supervision is batched at decision
boundaries rather than removed. That is a real improvement over continuous oversight, and it is not the
same as absence of oversight.

### 15.5 Costs that are not yet modelled

Recorded as known-absent rather than left to be discovered:

- **No token, dollar or latency budget exists anywhere.** Every "budget" in this document is a retry
  counter. Expertise caps are *entry counts*, not token counts, and entries have no length limit.
- Every spawn loads the **full CLAUDE.md hierarchy** (measured: ~19KB ≈ 5k tokens) plus all preloaded
  rule content plus injected Expertise plus `BRIEF`/`PLAN`/`STATE`, before doing any work.
- **A feature costs 19–45 spawns**, largely serialized. Nothing in the system logs or bounds this, and
  nothing would tell you it had become uneconomic.

**This is the open question that gates whether the org in §3 should exist at all** — see BUILD.md
§ "Pilot before building the org."
