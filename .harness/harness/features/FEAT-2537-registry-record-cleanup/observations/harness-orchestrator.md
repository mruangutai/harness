# Observations — harness-orchestrator — FEAT-2537-registry-record-cleanup

- 2026-11-25: A deletion's behavior contract must be enumerated by input SHAPE, not by the instance the ticket names. "Remove the v1 branch" had three unnamed members: `{}` (caught at intake), row-carrying non-v2 envelopes (caught at validate c0), and the CRLF/text-mode gap in the witness (caught at c1). A base-vs-pin probe over a shape table before signature would have surfaced all three at once.
- 2026-11-25: When a ruler grants exactly one fix round, the fix must hit the ruling's literal wording ("raw bytes" means a binary read). Implementing its intent instead forced a completion round (r-3, then r-4) that cost one full validate dispatch.
- 2026-11-25: G-17 slipped once: `run-start` ran in parallel with the commit of the same `feature.json`. Git won the race and both states landed, but that was luck. Run state writers alone, every time.
- 2026-11-25: Forgot to leave the uncommitted observation before the PR merge. The worktree survived because the sweep reaps only after the ship record lands; this observation is that guard.
