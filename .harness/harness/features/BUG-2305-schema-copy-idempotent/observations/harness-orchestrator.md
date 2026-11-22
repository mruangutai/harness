# Observations — harness-orchestrator — BUG-2305-schema-copy-idempotent

- 2026-11-22: Patch intake dispatch sent with no outputSchema/schemaMode; the host returned the call carrying the hook's injected pair plus the #2240 note, so the ticket's persistence mechanism was observed first-hand in this run. check-state INV-37 (no build-entry receipt) is the expected pre-signature state; gh-sync open is main's at build entry.
- 2026-11-22: handoff shape gate: brief-sc:SC-NN resolves only a line starting `SC-NN:`; a by-perspective BRIEF writes `SC-NN (perspective):`, so brief-sc pointers never resolve there — cite brief-perspective and plan-task instead. brief-perspective paths must be root-relative, never absolute.
- 2026-11-22: run-start --succession refused when no handoff note preceded the run (all tasks main-session-direct, INV-17 exempt); the ledger records decisions that happened, so a successor with no seam owes none.
- 2026-11-22: check-state.py --feature from a worktree (any cwd, with or without --checkout) discovers only the main checkout corpus; the per-write --changed audit from feature-record/plan-merge is the only in-worktree check that ran.
