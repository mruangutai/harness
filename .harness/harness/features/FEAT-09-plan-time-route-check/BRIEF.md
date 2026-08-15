# BRIEF — FEAT-09 Plan-time route check

## Problem

For three features running, a PLAN reached the build phase carrying tasks whose target paths no
agent's domain grants write on. The build spine stalls, a lead re-derives a denial `team-config.yaml`
could have answered before dispatch, and at FEAT-04 run 10 it cost a real ESCALATE — $16 — with the
lead attributing the failure to its own dispatch (issue #20). `FEAT-05/feature.yaml:78-81` names it
"ROUTING WALL, third recurrence"; qa hit a fourth at `team-config.yaml:216-223`. FEAT-06 and FEAT-07
each pre-computed the routes by hand, unprompted — proof the check works and proof it is currently a
discipline that decays.

## Goal

Every PLAN task's route is resolved at plan time, mechanically, against `.harness/team-config.yaml`.
A task either names the agent whose domain grants write on its `files:`, or it declares itself a
main-session step. A plan carrying an unrouteable, undeclared task does not reach signature. The
build phase never discovers routing again.

## Requirements

- REQ-01: Every task in a PLAN declares its execution route — the agent that may write its target
  paths, or an explicit main-session step.
- REQ-02: A PLAN carrying a task whose target paths no agent may write, and which does not declare
  itself a main-session step, is rejected mechanically rather than by someone noticing.
- REQ-03: The rejection names the offending task and the offending path, so the planner can fix it
  without re-deriving the grants.
- REQ-04: Plan-time route resolution and write-time enforcement give the same answer, because they
  are the same matcher. A second path-matching implementation is a defect.
- REQ-05: The plan-time query is safe to run from a script and from a terminal: it cannot hang, and
  it cannot report a clean or empty answer when it did not actually resolve anything.
- REQ-06: The routing declaration is part of the PLAN template's shape and the planning rule, not
  per-feature house style reinvented each time.

## Success Criteria

- SC-01: `check-domain.sh --resolve <path>` prints the complete, sorted set of agents whose domain
  grants write on that path — one name for a singly granted path, both names for
  `.claude/skills/harness/bin/**` which `team-config.yaml:155` and `:197` grant twice.
  verify: automated      evidence: unit
- SC-02: A path no domain grants prints the explicit token `NOBODY` and exits 0. Empty stdout is
  never a valid answer.
  verify: automated      evidence: unit
- SC-03: `--resolve` never reads stdin. With stdin an open pipe nobody writes to it answers within
  10s instead of blocking, and with stdin closed it gives that same answer instead of exiting 0
  silently.
  verify: automated      evidence: unit
- SC-04: The `PreToolUse` hook path is unchanged: with a Write payload on stdin and no `--resolve`
  in argv, an out-of-domain write still exits 2 and an in-domain write still exits 0.
  verify: automated      evidence: unit
- SC-05: `check-plan-routes.py` exits non-zero on a PLAN whose task has ungranted `files:` and no
  main-session `execution_mode:`, and its output names both the task id and the offending path.
  verify: automated      evidence: unit
- SC-06: `check-plan-routes.py` exits 0 on a PLAN whose every task either resolves to a granting
  agent or declares `execution_mode: main-session-direct`. Both shapes pass.
  verify: automated      evidence: unit
- SC-07: A `files:` entry containing a wildcard is reported on its own explicit unresolved line and
  does not silently pass; the reported plan's exit status is unchanged by the deferral.
  verify: automated      evidence: unit
- SC-08: Exactly one path matcher exists, and `check-plan-routes.py` implements none of it. Four
  clauses, each separately fixtured: (1) it invokes `check-domain.sh` for every path decision;
  (2) its source contains no `fnmatch`; (3) its source contains no glob-to-regex translation of its
  own; (4) it does no `startswith`/prefix comparison — proved behaviourally, not by grep: a path
  granted only through a mid-pattern wildcard (`.harness/features/*/runs/*-eng/**`,
  `team-config.yaml:278`) still resolves to its granting agent, where a prefix comparison on the
  text before `/**` reports it ungranted. That is the exact bug `check-domain.sh:193` records.
  verify: automated      evidence: unit
- SC-09: `templates/PLAN.md` carries a `## Lanes` section, an `execution_mode:` field on the task
  stanza, and both legal tokens named — so a planner reading only the template writes a routable
  plan.
  verify: automated      evidence: unit
- SC-10: The whole unit suite passes with the new test file registered in `run-unit-tests.sh`, and
  the runner's drift detector accepts it rather than exiting 2 on an unlisted test.
  verify: automated      evidence: unit
- SC-11: The plan-time route rule has exactly one home in the rule layer —
  `.claude/skills/harness-spec-driven/SKILL.md`, citable at a `file:line` — and
  `.claude/agents/harness-pm.md` is unchanged by this feature, its diff over the feature branch
  empty, so the two cannot drift apart.
  verify: inspection
- SC-12: A task that declares `execution_mode: main-session-direct` on paths an agent's domain DOES
  grant is reported as an explicit deviation line, and that report does not fail the plan — a
  DEC-174 carve-out is disclosed, not blocked.
  verify: automated      evidence: unit

## Verification gaps

- `functional`, `integration`, `component`, `ui`, `eval` and `typecheck` all carry `cmd: null` in
  `.harness/harness.json`. Every SC above rests on `unit`, whose runner exists
  (`run-unit-tests.sh`) and whose `detect` glob `.claude/skills/harness/bin/test-*.py` matches the
  surface this feature changes — so no SC rests on a null kind.
- What no runner proves: that a planning agent, given the new rule, actually runs the checker before
  handing a plan back. That is behaviour, not code. It rests on SC-11's inspection and on the next
  feature's plan being observably route-resolved.

## Constraints

- **One matcher only.** `check-domain.sh`'s inline `matches()` (`:215`) has deliberately custom
  semantics — its `:193` comment records that `fnmatch` is wrong here because `fnmatch`'s `*`
  matches `/`. A second implementation is the DEC-126 drift shape and is out.
- **No agent's domain grants change.** This feature makes the existing grants legible at plan time;
  re-drawing them is a separate feature (grilling `## Out of scope`).
- **DEC-174 carve-out applies to `check-domain.sh`.** It is a gate script: direct edit, tests run
  explicitly, a human reading the diff — never dispatched through a team run whose gates are the
  thing being changed.
- **FEAT-08 (issue #58) is in flight and owns a disjoint file set.** No task here may write
  `harness/SKILL.md`, `harness-team/SKILL.md`, `harness-orchestrator.md`, `teams/*.yaml`,
  `harness.json`, `check-state.sh`, `validate-digest.py`, `cost-report.py`, or anything under
  `docs/harness/`. Consequences: the checker cannot become a `check-state.sh` invariant in this
  feature, and this feature ships without its `DECISIONS.md` entry (both raised as open questions).
- Prose-only enforcement was rejected in grilling, for the DEC-125 "relied on being pointed at"
  reason. The rule text is necessary but is not the mechanism.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-05
