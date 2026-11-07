# BUG-2141 T-01 — fail-first evidence

Baseline pin: origin/main = `0b17e9bbf7ef4baafa0eb0844ec0edbb753dd86f` (fetched 2026-10-10).

Method: a disposable runner (deleted after use, not committed) extracted
`git archive 0b17e9bb` into a private temp tree (historical `dispatch-guard.py` and every
sibling module it imports — `digest_destination`, `handoff_policy`, `inflight_registry`,
`isolated_bin`, ...), copied the CURRENT test files over it, and ran:

    python3 tests/unit/test-lead-start-preflight.py
    python3 tests/integration/test-dispatch-guard.py

Subject files: `.claude/skills/harness/bin/dispatch-guard.py` (historical, unmodified).

## Baseline (origin/main) — unit: exit 1, 46 of 50 passed

| Case | Baseline | Failed assertion |
|---|---|---|
| BUG-2141/main-eng/single-direct | exit=0 claim=yes receipt=yes stderr='' | refused before claim, registry unchanged |
| BUG-2141/main-eng/single-direct/diagnostic | exit=0, stderr empty | stderr names DEC-174 + build directly |
| BUG-2141/main-eng/multi-direct | exit=0 claim=yes receipt=yes stderr='' | refused before claim, registry unchanged |
| BUG-2141/main-eng/multi-direct/diagnostic | exit=0, stderr empty | stderr names DEC-174 + build directly |

The failures are the baseline ACCEPTING the detour (exit 0, claim recorded, receipt printed):
imports, mission, run registration and fixtures all succeeded. Positive controls passed at
baseline: Main→eng-lead on mixed/team/missing-mode/empty/invalid/absent plans (exit 0, claim),
Main→product-lead plan/patch, Main→validator-lead validate/fix, orchestrator→eng-lead, and
product-lead→eng-lead (existing spawns-allowlist refusal), plus all 32 pre-existing cases.

## Baseline (origin/main) — integration: exit 1, 114 of 117 passed

| Case | Baseline | Failed assertion |
|---|---|---|
| case 15c all-direct: refused (exit 2) | exit 0 | returncode == 2 |
| case 15c: names DEC-174, build directly | stderr empty | DEC-174 / directly in stderr |
| case 15c: registry unchanged | claim `harness-eng-lead` dispatcher `Main` recorded | registry before == after |

Control `case 15c: mixed plan still claims` PASSED at baseline.

## Final (HEAD with fix)

- unit: exit 0, 50 of 50 passed
- integration: exit 0, 117 of 117 passed
