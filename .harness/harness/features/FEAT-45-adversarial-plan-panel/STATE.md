# STATE

## Current

- feature: FEAT-45-adversarial-plan-panel
- run: .harness/harness/features/FEAT-45-adversarial-plan-panel/runs/2026-08-31-1-validator/state.yaml
- squad: none
- status: Building

BUILD COMPLETE, stopped at the validate seam. All TWELVE tasks are `done` and committed. The
orchestrator re-ran the `verify:` block of every task it dispatched verbatim from plan.yaml itself —
T-01, T-09, T-10, T-11, T-12 — each exit 0, rather than accepting a digest's claim. The seven
main-session-direct tasks T-02..T-08 landed at 7ee3f65.

The QA gate PASSED at fc42462 with `matrix_ok: true`: full suite runner exit 0 and zero `^FAIL `
lines over 56 discovered scripts, unit-only the same over 29. QA re-verified 7 of the eng lead's 16
claimed mutants independently and recorded that the other 9 remain author-reported rather than
restating them as established.

SIMPLIFY ran as the last build step, before any pin. All four angles ran and NOTHING was applied —
an empty pass, recorded as the real outcome it is. The reuse angle confirmed `panel_findings.py` is
genuinely the single place a finding's identity is computed, with no second normalization or hashing
anywhere in the tree. Because nothing was applied, no post-apply suite re-run was owed and the tree
was byte-unchanged.

One task was added mid-build. T-10's verify could not go green because
`test-harness-yaml-corpus.py` asserted `TEAMS_EXPECTED = 2` while FEAT-45 legitimately adds a third
team definition — a designed tripwire whose own comment forbids widening the number silently. No
task owned that file, so it went to harness-pm, which ruled it inside FEAT-45's existing signature
(the third team is T-02's signed product) and added T-12 plus decision D-15. Not a re-signature, and
the count was made to match reality rather than reality made to match the count.

`review_sha` is still 1d3e5db and is deliberately NOT re-pinned here: it predates every build commit,
and pinning is validate's first act. Nothing may dispatch a validator until it moves.

Cycles 5 of 10 — one added this segment, a send-back inside the eng run after a member reported
`task_verify: pass` alongside `RC=1` in the same digest. Runs 10 of 20, informational.

## Open Questions

- Harness defect: INV-26 is structurally red for the whole Building phase and both shapes are
  produced by the mirror's own writers. A signed feature's `pending` cards sit at Ready because
  `gh-sync.py` writes Ready to every sub-issue at signature, but INV-26's `_EXPECT` maps
  pending->backlog with no `ready` accepted (check-state.sh:1429). A `done` task's card can only sit
  at Building until ship, yet INV-26 expects Done and widens its accept set only when feature.json
  reads `Review` (check-state.sh:1524-1527). The mirror never gates, so nothing is stuck.
  — harness-orchestrator
- The `plan-panel.yaml` closing comment restating the validator lead's transcription contract has now
  been flagged by TWO separate simplify passes and returned flag-only both times, because both files
  resolve to NOBODY. The build side structurally cannot ever apply it. It needs a manifest grant or a
  main-session-direct edit, or a third pass will rediscover it. — harness-eng-lead
- DEC number allocation has no cross-branch check. `main` landed DEC-205 via PR #1032 after this
  branch was cut, so "the next free number" read from inside a branch is wrong by construction.
  Caught by hand; FEAT-45's entries are DEC-206/DEC-207 with the 205 gap left open.
  — harness-orchestrator
- Five pre-existing plan-phase artifacts fail their own contracts and predate this build: four
  `runs/*/state.yaml` carry non-checkpoint keys against DEC-154, and two `digest.md` fail the lead
  digest contract under DEC-156. Not corrected here — rewriting another run's record to look better
  would falsify it. — harness-orchestrator
- SC-03's second direction ("a second run overwriting the first's record") is graded only by a
  `{{cycle}}` token-presence proxy, with no behavioural test across two runs. Non-gating, ranked
  first among QA's residuals by irreversibility. — harness-qa
- 40+ of 43 `bin/test-*.py` files define their own `check()` in five mutually incompatible shapes.
  Not a FEAT-45 defect and correctly out of scope, but a standing repo-wide reuse cost.
  — harness-eng-lead
