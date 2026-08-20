# Expertise — harness-backend-dev

## Patterns (max 15)

## Gotchas (max 15)
- G-01: WHEN writing fixtures against the fake-gh test harness DO read its logging and
  issue-numbering behavior in `.claude/skills/harness/bin/test-gh-sync.py` first — assumptions
  about counters, log format, or which calls get logged fail loudly but still cost a debug cycle.
- G-02: WHEN `HARNESS_GH_COST_LOG` (or similar always-on instrumentation) is enabled by default DO
  check whether `factory_config.harness_root()`'s `CLAUDE_PROJECT_DIR` fallback routes pre-existing
  unit/integration tests into the real `.harness/logs/` — with `CLAUDE_PROJECT_DIR` unset, tests
  that don't redirect to a tmp root write into the actual checkout.

## Outcomes (max 10)

## Open (max 5)
