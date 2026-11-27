# Observations — harness-qa — FEAT-2542-dispatcher-placement

- 2026-11-26: An ordering mutant (move a module-level refusal call later) stayed fully green because the later call path invoked the memoized function lazily on every tested route; only a route where the earlier preflight refuses first (lead → code-reviewer with mission plan, non-pending plan) exposes the delta. When a memoized check is also called lazily, ordering mutants need a row whose earlier step refuses.
- 2026-11-26: bash-write-guard refuses `git checkout` even inside a /tmp clone; `git -C <tree> archive <sha> | tar -x` gives a source-identical tree for base/mutant runs without moving HEAD.
