# Operator signature — FEAT-2389 — 2026-11-22

Signed by **fable-advisor** under the operator's delegated authority. Rework: 1 round / 30 min. Overrules: none.

> The plan matches the settled grilling exactly: the sole pin is `packageManager: bun@1.3.14`, plus one workflow comment and one README sentence, main-session-direct under DEC-174. Verified at worktree baseline 9eb07b4f: `package.json` has no `packageManager` and no `engines`, so the red-first equality check will genuinely fail. Both `setup-bun@v2` steps are input-free, `@types/bun` is 1.4.5, and the README's dependency-update guidance must stay distinct from the new sentence. SC-04's CI-log requirement (`bun-v1.3.14` in both Install Bun steps) proves setup-bun's resolution order empirically before merge.

Deleted checkpoint (notes/intake-record-2026-11-22.md): no further action. The registered digest is the run's record. Do not reconstruct the checkpoint files.
