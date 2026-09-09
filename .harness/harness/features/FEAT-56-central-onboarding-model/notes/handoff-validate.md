# Handoff — FEAT-56-central-onboarding-model, validate → ship — written at 8ff5197f, seq-5

SUPERSEDES seq-3. That note described the FIRST attempt, which the operator rejected at the UAT gate
and re-scoped. This one describes the revised feature, planned and panelled a second time.

## Next

Ship acceptance is the main session's, not a squad's. It holds two things and only two: the
operator's verdict on the three-walkthrough UAT at `notes/uat-FEAT-56-c2.md`, and their disposition
of backlog rows C-1..C-16 in `notes/ship-review-2026-09-09-ship.md`. On PASS, open the PR, let the
operator merge (`gates.merge` is `user_gated`), then terminalize — `gh-sync.py record-pr`, `ship
--body-file notes/ship-review-2026-09-09-ship.md`, `backlog` for the unstruck rows — and confirm
#206 and every card at done. Nothing is left to build.

## Trust

- All twenty tasks are at station `done` with `[harness:t-NN]` commits —
  `plan.yaml` `tasks[].status` and `git log 4b5dbb23..HEAD` — verified-at 8ff5197f
- Eleven of sixteen criteria MET, each RE-TAKEN at this pin rather than inherited across the five pin
  moves — `notes/research-FEAT-56-goalcheck-ship-c2.md` — verified-at 8ff5197f
- SC-07 is `not_met` on EXACTLY the six D-14 cases in `test-check-plan-routes.py`, one file, one
  cause, no seventh; SC-09 stays struck — orchestrator re-ran both suites — verified-at 8ff5197f
- The review panel returned `must_fix: []` at `severity_max: med` in cycle 2, with all four cycle-1
  findings closed on evidence reviewers took themselves —
  `notes/review-harness-*-c2.md` and the c3 set — verified-at 44351432
- `check-state.sh` reports ZERO FEAT-56 violations — run from this worktree — verified-at 8ff5197f
- `sync-command-adapters.py --check` exits 0 and `check-omp-port.py` prints `OMP port surface: ok` —
  run directly — verified-at 8ff5197f
- Budget has two cycles left: `cycles_used` 20 of `max_total_cycles` 22, the operator's second raise
  — `feature.json` — verified-at 8ff5197f

## Dead ends

- Do not release a cross-worktree persona claim to unblock a squad write: single-flight is by agent
  TYPE across worktrees, a missing checkpoint is the signature of that collision rather than of a
  leak, and the run that cannot write its own record is the one least able to defend itself —
  `notes/ship-review-2026-09-09-ship.md` rows C-1..C-3 — verified-at 8ff5197f
- Do not treat the six red `test-check-plan-routes.py` cases as a defect: the operator accepted them
  as D-14 and they expire at merge — `plan.yaml` `decisions:` D-14 — verified-at 8ff5197f
- Do not re-open the CLI floor, the `cli_min_version` removal, `harness-add-repo` as a skill, or
  revision-in-place: all operator rulings — `notes/answers-rescope-2026-09-08.md` and D-12/D-13 —
  verified-at 8ff5197f

## Working set

- .harness/harness/features/FEAT-56-central-onboarding-model/notes/ship-review-2026-09-09-ship.md
- .harness/harness/features/FEAT-56-central-onboarding-model/notes/uat-FEAT-56-c2.md
- .harness/harness/features/FEAT-56-central-onboarding-model/notes/research-FEAT-56-goalcheck-ship-c2.md
- .harness/harness/features/FEAT-56-central-onboarding-model/feature.json
- .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml

## Done when

Scope: the operator's UAT verdict and backlog disposition are in hand
Authority: brief-sc:SC-15
Authority: brief-sc:SC-04
