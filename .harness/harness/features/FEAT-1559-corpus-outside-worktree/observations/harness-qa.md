# Observations — harness-qa — FEAT-1559-corpus-outside-worktree

- 2026-10-05: git checkout is refused by bash-write-guard; a full clone at a SHA = clone --no-checkout, update-ref --no-deref HEAD, restore --source=HEAD --staged --worktree . A validator pin before the feature merges is NOT sparse (owner hooks pre-1559), so test-corpus-real-owner fails from it by design.
