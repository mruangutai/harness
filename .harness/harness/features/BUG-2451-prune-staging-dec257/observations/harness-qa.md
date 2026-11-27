# Observations — harness-qa — BUG-2451-prune-staging-dec257

- 2026-11-26: An audit-hook subprocess trap masks index-identity legs run under it — the defective git add is blocked before the index changes, so the hooked index check passes on the defect; natural index RED needed an unhooked case. Conditionally-printed summary PASS lines (emitted only when all legs pass) never print FAIL.
- 2026-11-26: c2 — an "names EVERY offender" refusal whose fixture holds exactly one offender per grouping unit (per run) cannot redden a per-group first-only truncation; mutant `return unreadable[:1]` inside the per-run walker stayed 52/52 green while a global [:1] reddened. Seed at least two offenders inside one group.
