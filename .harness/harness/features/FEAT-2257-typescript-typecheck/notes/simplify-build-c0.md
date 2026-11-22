# Simplify pass — FEAT-2257 build diff — 2026-11-22

Scope: `git diff bda50269 4cc44d64 -- . ':!.harness/harness/features'`. Four parallel read-only `reviewer` dispatches, one angle each (harness-simplify, code surface).

| Angle | Reader | Result |
|---|---|---|
| reuse | S2257Reuse | 1 finding (P3): `tests/unit/test-suite-layout.py` `_running_kinds` restated the running-status / default-true `classifies_tests` predicate already in `code_grade._classifies_tests`. **Applied** (main-session-direct, the build side): `_running_kinds` now filters with `code_grade._classifies_tests(cfg)`, so hygiene and complexity classification cannot drift. |
| simplification | S2257Simplify | no findings: every added predicate, helper, config key and CI step carries required behavior or settled scope |
| efficiency | S2257Efficiency | no findings: the regression's checks are measured in seconds; the repeated frozen installs are settled scope |
| altitude | S2257Altitude | no findings: the toolchain sits at repository/CI level; the exception is a shared config property consumed at the existing classification boundaries |

After the apply: `python3 tests/unit/test-suite-layout.py` rc 0; `python3 tests/unit/test-code-grade.py` PASS. No assertion was weakened or removed.
