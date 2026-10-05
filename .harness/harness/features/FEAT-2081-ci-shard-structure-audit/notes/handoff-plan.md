# Handoff — FEAT-2081-ci-shard-structure-audit, plan → build — written at 7ea60c88

## Next

Build main-session-direct in this worktree (DEC-174). Start T-01 (weighted `--shard i/n` + completed-file manifests) and T-03 (single-pass AST index for the feat62 / consolidation / broad-catch audits) in parallel; both are `depends_on: []`. Then T-02 (independent shard validator), T-04 (workflow), T-05 (SPEC §9, harness-documentor), T-06 (uat.md). Every automated SC needs its red-first receipt before the fix lands.

## Trust

- BRIEF and plan signed by the operator 2026-10-04; plan re-signed the same day for the F1 amendment to T-03 — .harness/harness/features/FEAT-2081-ci-shard-structure-audit/plan.yaml#approval — VERIFIED
- Plan panel recorded; its one high finding (F1, PF-5bfc6ea843dcdddb994445126b398fb1) is resolved by that amendment and INV-32 is green — .harness/harness/features/FEAT-2081-ci-shard-structure-audit/runs/2026-10-05-01-validator/digest.md — VERIFIED
- GitHub mirror open: milestone #98, parent #2081, sub-issues T-01 #2082, T-02 #2083, T-03 #2084, T-04 #2085, T-05 #2087, T-06 #2090; build_entry opened; station building — .harness/harness/features/FEAT-2081-ci-shard-structure-audit/feature.json — VERIFIED
- Duration weights come from CI run 37264903064's log, committed as tests/integration/integration-durations.json; unknown files take the median — plan.yaml#T-01 — UNVERIFIED

## Dead ends

- Do not add any permanent test that reads a historical commit from git; CI checks out one commit. Old-vs-new audit equivalence is one-time local QA evidence (operator ruling on F1) — plan.yaml#T-03 — VERIFIED
- Do not wire the structure audits into check-state.py; out of scope (OQ-03) — BRIEF.md#Out of scope — VERIFIED
- Do not route runner, pool, check-plan-routes.py, tests.yml or their tests through governed teams (DEC-174) — plan.yaml#lanes — VERIFIED
- validate-digest.py refuses a `plan:<path>` reader return once approval is not pending (lines 978-988), so a retrospective plan panel cannot hand back natively; the scope review is on disk in notes/review-harness-code-reviewer-plan-c2.md — UNVERIFIED

## Working set

- .harness/harness/features/FEAT-2081-ci-shard-structure-audit/BRIEF.md
- .harness/harness/features/FEAT-2081-ci-shard-structure-audit/plan.yaml
- .harness/harness/features/FEAT-2081-ci-shard-structure-audit/feature.json
- .harness/harness/features/FEAT-2081-ci-shard-structure-audit/runs/2026-10-05-01-validator/digest.md
- .agents/skills/harness/bin/run-unit-tests.py
- .agents/skills/harness/bin/run_pool.py
- .agents/skills/harness/bin/check-plan-routes.py
- .github/workflows/tests.yml
- tests/integration/test-checker-structure-locks.py

## Done when

Scope: FEAT-2081 build of T-01 through T-06 to the signed plan
Authority: brief-perspective:.harness/harness/features/FEAT-2081-ci-shard-structure-audit/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/FEAT-2081-ci-shard-structure-audit/BRIEF.md#code maintainer
Authority: approval:.harness/harness/features/FEAT-2081-ci-shard-structure-audit/plan.yaml#approval
