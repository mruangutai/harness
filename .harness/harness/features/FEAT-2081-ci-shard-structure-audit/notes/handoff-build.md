# Handoff — FEAT-2081-ci-shard-structure-audit, build → validate — written at fc942ec4, seq-0

## Next

Validate at the pinned review_sha: run the validator lead's VALIDATE team over e8d868f7..review_sha, then the user's UAT (SC-09, SC-10) from notes/uat.md.

## Trust

- T-01..T-06 built main-session-direct (DEC-174) except T-05 (harness-documentor); each task's red-first receipts are recorded — notes/evidence-T-01.md … evidence-T-04.md, notes/qa-structure-audit-equivalence.md — VERIFIED
- Four-angle simplify pass ran on the code diff; three findings applied in fc942ec4 — VERIFIED
- Live CI on draft PR #2100: run 37324916242 failed closed on a real shard failure (pre-existing copytree/.pyc race, fixed by the precompile step); runs 37325307899 and 37335457819 passed — notes/evidence-T-04.md — VERIFIED

## Dead ends

- No permanent test may read a historical commit; old-vs-new audit equivalence is one-time local QA evidence (panel F1 ruling) — plan.yaml#T-03 — VERIFIED
- GitHub has no per-job cancel; the live shard-cancellation UAT case is dropped (OQ-02 amended) — BRIEF.md#Constraints — VERIFIED

## Working set

- .claude/skills/harness/bin/run-unit-tests.py
- .claude/skills/harness/bin/run_pool.py
- .claude/skills/harness/bin/check-integration-shards.py
- .claude/skills/harness/bin/check-plan-routes.py
- .github/workflows/tests.yml
- tests/integration/integration-durations.json

## Done when

Scope: FEAT-2081 validated at a pinned review_sha and UAT signed
Authority: brief-perspective:.harness/harness/features/FEAT-2081-ci-shard-structure-audit/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/FEAT-2081-ci-shard-structure-audit/BRIEF.md#code maintainer
Authority: approval:.harness/harness/features/FEAT-2081-ci-shard-structure-audit/plan.yaml#approval
