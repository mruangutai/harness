# Simplify pass — BUG-2349 build diff — 2026-11-22

Scope: `git diff 71f9aa45 4cf45dd3 -- .claude/skills/harness/bin/plan_merge/union.py tests/integration/test-plan-merge.py`.
Four parallel read-only `reviewer` dispatches, one angle each (harness-simplify, code surface).

| Angle | Reader | Result |
|---|---|---|
| reuse | S2349Reuse | no findings: extends `_union_key_head` and keeps reusing `_key_head`; the test helper composes the suite's existing fixture, I/O and apply helpers |
| simplification | S2349Simplify | no findings: a minimal conditional; the helper removes repeated fixture/apply/reload code across the three cases |
| efficiency | S2349Efficiency | no findings: constant-time emptiness checks on the existing merge path |
| altitude | S2349Altitude | no findings: the behavior lives at the authoritative shared union-head selector |

Nothing to apply. No deviation from the signed T-01 intent.

## Rework round 1 — `git diff 2a476ca0 a0e8dd0d -- tests/unit/test-plan-merge-union-head.py`

| Angle | Reader | Result |
|---|---|---|
| reuse | S2349c1Reuse | no findings: no importable helper or fixture is re-implemented |
| simplification | S2349c1Simplify | no findings: the dynamic load is required by the red receipt path; the helper removes repetition |
| efficiency | S2349c1Efficiency | no findings: one module load and three small in-process merges |
| altitude | S2349c1Altitude | no findings: the head rule is bound at the in-process unit boundary; CLI behavior stays in integration |

Nothing to apply.
