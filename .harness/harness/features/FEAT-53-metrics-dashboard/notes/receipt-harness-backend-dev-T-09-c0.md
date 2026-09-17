# T-09 receipt

Attribution now resolves harness task prefixes through owning feature plans and agent front matter into model-tier counts while preserving all named unattributed buckets and total accounting.

- Commit: `ca75e1bfdce5db499858ff3467dd1503e9ca2712` (`[harness:t-09] add attribution tier KPI`).
- RED: before production code, `python3 tests/unit/test-metrics-kpi.py` exited 1 with `ModuleNotFoundError: No module named 'attribution'`.
- GREEN / amended verify (verbatim): `python3 tests/unit/test-metrics-kpi.py` → `Ran 14 tests ... OK`.
- Behavior proof: the new fixture resolves `opus` and `haiku`; tracks no-prefix, human, feature-only, absent-step, missing-model, and comma-list fallback cases; totals 9 commits; and observes 3 `artifact_accessors.load_plan` calls for six task-bearing commits across three feature IDs, proving per-feature memoization.
- Code risk: `attribution.py` functions grade 4–5 (production bar 4); changed test functions grade 3–5 (test bar 3); `kpi._aggregate` grade 4.
- Authorized DEC-229 same-task amendment: files changed from `[.claude/skills/harness/bin/dashboard/attribution.py, .claude/skills/harness/bin/dashboard/kpi.py, .claude/skills/harness/bin/test-metrics-kpi.py]` to `[.claude/skills/harness/bin/dashboard/attribution.py, .claude/skills/harness/bin/dashboard/kpi.py, tests/unit/test-metrics-kpi.py]`; verify changed from `python3 .claude/skills/harness/bin/test-metrics-kpi.py` to `python3 tests/unit/test-metrics-kpi.py`.
