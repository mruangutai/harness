# Expertise — harness-backend-dev
## Patterns (max 15)
- P-01: WHEN adding a new guard function anywhere `code_grade.py` will grade DO write it from the start as small named module-level helpers, not one combined function — its cognitive/cyclomatic bar (test files grade 3, others 4+) rejects a discover+parse+compare+report body outright.
## Gotchas (max 15)
- G-01: WHEN writing fixtures against the fake-gh test harness DO read its logging and issue-numbering behavior in `.claude/skills/harness/bin/test-gh-sync.py` first — assumptions about counters, log format, or which calls get logged fail loudly but still cost a debug cycle.
- G-02: WHEN `HARNESS_GH_COST_LOG` (or similar always-on instrumentation) is enabled by default DO check whether `factory_config.harness_root()`'s `CLAUDE_PROJECT_DIR` fallback routes pre-existing unit/integration tests into the real `.harness/logs/` — with `CLAUDE_PROJECT_DIR` unset, tests that don't redirect to a tmp root write into the actual checkout.
- G-03: WHEN writing a throwaway fixture outside any tracked path, including the session scratchpad, DO use a `python3 - <<EOF ... open(path,"w")` heredoc rather than a bash `>` redirect — the bash-write-guard blocks `>` redirection there too, not only inside repo paths.
- G-04: WHEN a function under `code_grade.py`'s own gate fails its complexity bar DO refactor it, never add it to an allowlist or exemption list — the gate enforces no exemption escape hatch, including for functions inside its own codebase.
## Outcomes (max 10)
## Open (max 5)
