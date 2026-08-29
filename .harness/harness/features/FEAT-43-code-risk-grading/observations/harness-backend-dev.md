# Observations - harness-backend-dev

- 2026-08-29: FEAT-43 c22 — code-grade.py's cognitive-complexity bar (3 for test files) rejected a single-function guard doing discover+parse+compare+report (cognitive 38); splitting into 5 small helpers (expected-set, path-discovery, line-parse, per-file-report, orchestrator) got every qualname to grade 3-5 with no behavior change. Worth defaulting new guards in this file to that shape from the start rather than writing one big function and splitting after code-grade.py fails it.
