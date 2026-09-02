# Expertise — harness-eng-lead
## Patterns (max 15)
## Gotchas (max 15)
- G-01: `.claude/skills/harness/bin/**` sits in both backend-dev's and dev-ops's domain in team-config.yaml, so the domain hook cannot keep their writes disjoint there — serialize any two tasks touching one file under it and attribute each write.
- G-02: WHEN assessing a test-matrix claim here DO read whether the test sits under `tests/unit/` or `tests/integration/`, not only `harness.json` detect globs — the directory decides which script executes; the globs only decide which kind the gate believes is required.
- G-10: WHEN dispatching a distillation whose ops include replace or drop DO state that expertise-merge.py is additive-union — same-id-different-text is exit 7 and there is no drop verb — so the member finishes with a targeted single-line Edit instead of spending a cycle rediscovering it.
## Outcomes (max 10)
## Open (max 5)
