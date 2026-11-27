# FEAT-2537 distill-orchestrator — correction to the run digest

**BLUF:** Repository-tier G-17 as recorded in `runs/distill-orchestrator/digest.md` was wrong and has been superseded. The digest is left unedited because `feature.json` binds it by hash (`cycle_evidence.sha256` `3873effa…`).

- **What was wrong.** I inverted log bullet 4. The first G-17 said to commit the observations log before the pull request merges. The log says the opposite: leave one observation uncommitted, because the post-merge sweep keeps a dirty worktree and removes a clean one once the ship record lands, and distill needs the worktree.
- **What is applied now.** Batch `1d68ca90…` supersedes batch `7639f3f2…` and adds the corrected G-17 to `.harness/harness/expertise/harness-orchestrator.md`:
  "WHEN a feature's pull request is about to merge DO leave one orchestrator observation uncommitted in the worktree — the post-merge sweep removes a clean worktree once the ship record lands and keeps a dirty one, and distillation needs the worktree; the distill commit stages the log."
- **Counts.** Repository Gotchas 14→15 (measured from the pre-run base); other sections unchanged. Craft batch `3fa3da86…` (G-06 replace) stands.
- **Receipt.** `notes/expertise-receipt-4ec14a62b36e21f50917992c6895756502c8e590ddb1a9c6e1876eea976f6a6b.json`.
- **Evidence.** The main session's account of the ship mechanic, and `check-state`'s INV-29 text printed at run-end: `remove` declines while the tree is dirty.
