# Observations - harness-documentor

- 2026-09-07: G-18 has a guard now, at least for harness-owned paths under a worktree claim: my first
  Edit used a relative DECISIONS.md section header and check-domain BLOCKED it, naming both the wrong
  destination and the bound worktree. So a relative harness-owned path fails loudly rather than
  silently editing the main checkout — but the fix is still "always spell the absolute worktree path
  in the section header", since the guard only covers claimed-worktree/proper-checkout pairs.
- 2026-09-07: proving a regenerated DECISIONS-INDEX.md changed only its @NNNN anchors is one pipeline:
  `git diff -U0 -- <index> | sed -n 's/^[-+]//p' | sed 's/@[0-9]\{1,\}/@N/' | sort | uniq -c` and then
  assert every count is 2. Cheaper and stronger than eyeballing 84 diff lines for a reworded ruling.
