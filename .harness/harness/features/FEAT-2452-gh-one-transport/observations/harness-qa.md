# Observations — harness-qa — FEAT-2452-gh-one-transport

- 2026-11-23: A fresh pinned checkout lacks node_modules, so integration test-typescript-typecheck.py reds (missing tsc) until `bun install --frozen-lockfile` runs in the pin; check-domain also refuses QA source perturbation inside its own pin (.claude/skills/**), so mutants must be in-memory monkeypatches of in-process test modules.
