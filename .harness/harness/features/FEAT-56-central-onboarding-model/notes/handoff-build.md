# Handoff — FEAT-56-central-onboarding-model, build → review — written at 6f34e289, seq-2

## Next

Dispatch the `review` team to `harness-validator-lead` at `review_sha` 6f34e289. It grades the
three `verify: inspection` criteria the suites cannot reach — SC-01, SC-03 (six `bin/` files, one
citation each) and SC-04 (fifteen doc/template/instruction files, one citation each). Then pm's
ship goal-check over all ten SCs, then SC-09's operator UAT, then the briefing.

## Trust

- All eight tasks are at station `done` and each landed a `[harness:t-NN]` commit —
  `plan.yaml` `tasks[].status` and `git log 4b5dbb23..HEAD` — verified-at 6f34e289
- The qa gate is green after one FAIL and its fix: unit exit 0, integration exit 0, and unit's
  four `^FAIL ` lines are `test-factory-claim-mutation.py`'s by-design mutant output while that
  file passes — `notes/qa-FEAT-56.md` — verified-at 6f34e289
- qa reproduced T-04's second red-capability proof independently and it agrees with the receipt;
  the first proof is unreproduced by anyone but its author — `notes/qa-FEAT-56.md` — verified-at
  6f34e289
- SIMPLIFY ran before the pin, applied one reuse fix and one prose fold-in, and both suites were
  re-run green after — `runs/2026-09-08-simplify-eng/digest.md` — verified-at 6f34e289
- `check-instruction-paths.py`, `check-omp-port.py` and `check-decision-anchors.py` all exit 0 —
  run directly — verified-at 6f34e289
- The pin is 6f34e289, not the code commit 85a42451: INV-33 went stale when the station write
  touched plan.yaml, and the code diff between the two is empty outside `.harness/` —
  `git diff --stat 85a42451 6f34e289 -- . ':(exclude).harness'` — verified-at 6f34e289

## Dead ends

- Do not treat unit's four `^FAIL ` lines as a red suite: exit status is the only sound signal
  here — `notes/qa-FEAT-56.md` adequacy_notes — verified-at 6f34e289
- Do not route a fix on `.claude|.agents/skills/**` outside `harness/bin/`, `.claude/commands/**`,
  `.omp/agents/**`, `.claude/agents/**` or `.harness/factory/fleet.yaml` to a squad: all resolve
  NOBODY — `check-domain.sh --resolve` per path — verified-at 4b5dbb23
- Do not act on INV-29's standing-worktree violations: every one names another feature's checkout,
  none is FEAT-56's — `check-state.sh` output — verified-at 6f34e289

## Working set

- .harness/harness/features/FEAT-56-central-onboarding-model/BRIEF.md
- .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
- .harness/harness/features/FEAT-56-central-onboarding-model/notes/qa-FEAT-56.md
- .claude/skills/harness-init/SKILL.md
- .claude/skills/harness/bin/factory_config.py

## Done when

Scope: the review panel returns at the pin with must_fix resolved
Authority: brief-sc:SC-03
Authority: brief-sc:SC-04
