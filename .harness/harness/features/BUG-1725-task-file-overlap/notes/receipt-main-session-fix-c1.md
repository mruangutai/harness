# Main fix receipt — validate c2

- Q3 / unit matrix: the worktree was cut from local `main` carrying an unpushed BUG-1563 landing whose test failed; rebased onto `origin/main` (BUG-1563 shipped as #1730/#1731). `test-check-state-inv35.py` passes.
- Q2 / SC-03, SC-04, T-01 `files:`, lanes: `.agents/skills` is a gitignored symlink to `.claude/skills`, so no git object exists at those paths. Amended T-01 `files:` and `verify:` (CAS via `plan-merge.py amend`), rewrote the lanes rows (`set-lanes`), and repointed both SC inspection paths to `.claude/skills/...`. Task set unchanged; approval stands.
- Q1 / SC-02 fail-first: the exit-0-on-overlap half preserves pre-fix behaviour and cannot redden. Reworded SC-02 so fail-first attaches to the overlap-beside-failure assertion, which is in the red set; receipt at `notes/receipt-main-session-T-01-fail-first.md`.
- Q5 / cycles_used: no main-session route writes it (same gap as #1683); left for the orchestrator's regate accounting.
