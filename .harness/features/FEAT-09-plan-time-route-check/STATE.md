# STATE

## Current

- feature: FEAT-09-plan-time-route-check
- phase: build
- worktree: /Users/molchairuangutai/GitHub/harness-FEAT-09 (branch feat/FEAT-09-plan-time-route-check)
- run: none open — no lead has been dispatched this phase
- status: awaiting-user

Plan phase CLOSED. Both artifacts carry `status: approved`, `approved-by: Mike Ruangutai`,
`date: 2026-08-05` — read by me in the worktree, not inherited. The approval gate passes.

Build is blocked on the user, not on the harness. Three of four tasks are layer-0 and cannot be
dispatched to any agent: T-01 is the DEC-174 carve-out on `check-domain.sh`, and T-03/T-04 write
`templates/**` and `harness-*/SKILL.md`, which nothing in `team-config.yaml` grants (verified —
only `bin/**` is granted anywhere under `.claude/skills/`). They are returned as ONE consolidated
segment with each `verify:` verbatim.

T-02 is HELD by user ruling until FEAT-08 merges to `main` and this worktree is rebased onto it.
Consequence, stated rather than hidden: every `verify:` in segment 1 rides `run-unit-tests.sh`,
which will report **13 PASS, not 14** — SC-10's registered-test clause is DEFERRED to T-02.

Pre-flight, run by me in the worktree at `ae2443d`: unit 13/13 exit 0, `check-docs.sh` exit 0,
`check-state.sh` exit 0. `--resolve` reproduces both measured hazards — open pipe HANGS past 10s,
stdin closed exits 0 with EMPTY stdout. T-01's three verify assertions are correct against
`team-config.yaml` (`:196` dev-ops sole grant on `harness.json`; `:155`/`:197` for `bin/**`).
`check-docs.sh` keys on stale STRINGS, not `file:line` anchors, so T-03/T-04 insertions rot
nothing. SC-11 pinned: `git diff ae2443d -- .claude/agents/harness-pm.md` is 0 bytes today.

Validate remains bound to the FOUR-WIDE panel by user ruling (`feature.yaml validate_panel`).

## Open Questions

- Q-A BLOCKING — execute the consolidated main-session segment (T-01, T-03, T-04) and report
  each `verify:` result. Nothing proceeds without it; the three tasks are unroutable to any agent.
- Q-B BLOCKING — has FEAT-08 merged to `main` and has this worktree been rebased onto it? T-02
  and the `DECISIONS.md` entry both wait on that, and the rebase must happen AFTER I commit
  segment 1, or the rebase collides with three uncommitted files.
- Q3 NON-BLOCKING — promote `check-plan-routes.py` to a `check-state.sh` invariant once FEAT-08
  releases that file? D-01 chose a pm-invoked script only because `check-state.sh` was unavailable.
- Q4 NON-BLOCKING — D-08 copies `check-state.sh`'s task-block regex rather than sharing it.
  Consolidate later, or accept two copies?
- Q5 NON-BLOCKING — FEAT-06 and FEAT-07 use the token `squad-dispatched`, which D-07 retires for
  `team`. Leave historical plans as-is (the current assumption), or normalise them?
