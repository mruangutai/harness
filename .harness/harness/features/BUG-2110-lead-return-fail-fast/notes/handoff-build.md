# Handoff — BUG-2110-lead-return-fail-fast, build → validate — written at a83198b1, seq-1

## Next

Validate at review_sha a83198b1 with the validator lead under its registered run.

## Trust

- T-01..T-03 built main-session-direct (DEC-174); focused suites 34/34 and 71/71 (with --check-producers); full unit and integration exit 0 — plan.yaml stations done — VERIFIED
- Fail-first receipt at 63cac11a: 30 unit and 17 integration startup cases red for the intended reason, controls green — notes/evidence-T-01.md — VERIFIED

## Dead ends

- validate-digest.py, digest_destination.py and harness-hooks.ts are deliberately unchanged; return-time checks remain authoritative — plan.yaml#T-02 — VERIFIED

## Working set

- .claude/skills/harness/bin/dispatch-guard.py
- tests/unit/test-lead-start-preflight.py
- tests/integration/test-lead-start-return.py
- .claude/skills/harness-zero-micro-management/SKILL.md
- .harness/harness/features/BUG-2110-lead-return-fail-fast/notes/evidence-T-01.md

## Done when

Scope: BUG-2110 validated at a pinned review_sha
Authority: brief-perspective:.harness/harness/features/BUG-2110-lead-return-fail-fast/BRIEF.md#orchestrator
Authority: brief-perspective:.harness/harness/features/BUG-2110-lead-return-fail-fast/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-2110-lead-return-fail-fast/BRIEF.md#code maintainer
Authority: approval:.harness/harness/features/BUG-2110-lead-return-fail-fast/plan.yaml#approval
