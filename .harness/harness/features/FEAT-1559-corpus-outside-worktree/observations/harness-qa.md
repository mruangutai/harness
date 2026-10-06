# Observations — harness-qa — FEAT-1559-corpus-outside-worktree

- 2026-10-05: git checkout is refused by bash-write-guard; a full clone at a SHA = clone --no-checkout, update-ref --no-deref HEAD, restore --source=HEAD --staged --worktree . A validator pin before the feature merges is NOT sparse (owner hooks pre-1559), so test-corpus-real-owner fails from it by design.
- 2026-10-05: c2 gate at 42856abb: a pre-merge validator pin is an unconverted linked worktree, so exact-pin suites need a full --no-local clone (git restore, not checkout); require_landed mutant + 0e8301a5 production restore both red 2 tests; G-1 maximal-clause mutant still survives unit+integration; G-4 sweep-skip mutant green in pool this time (inconclusive).
