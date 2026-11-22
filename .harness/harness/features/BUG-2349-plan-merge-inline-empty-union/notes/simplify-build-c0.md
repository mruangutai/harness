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
