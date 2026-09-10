# STATE

## Current

- feature: FEAT-58-corpus-outside-worktree
- run: THIRD BATCHED FIX APPLIED, cycle 0, 2026-09-10. The operator's cycle-6 answers (`notes/answers-operator-c6.md`) landed whole and the panel verified all four cycle-6 findings RESOLVED at source. On disk: BRIEF.md at 10 REQ / 15 criteria, plan.yaml at 12 tasks (N-01..N-10, N-12, N-13; N-11 retired, its id a deliberate gap) and 17 decisions, ledger 45 rows with nothing removed since the single named Q6 strike, `status: plan`, both approvals `pending`. Handoff: notes/handoff-plan.md
- squad: none — awaiting the operator's fourth batched signature review
- status: awaiting_user
- gate: the panel (`planpanelc6-validator`) returned FAIL, `severity_max: high`. Both readers RAN, neither skipped. SIX new findings — four high (PP-01..PP-04) and two med (PP-05, PP-06) — and ALL of them land on N-13, the surface no panel had previously read. Everything else in the plan graded clean and PL-01..PL-04 are carried forward RESOLVED with `resolved_by`. DEC-207 forbids a pre-signature fix dispatch and no agent may risk-accept a high.
- budget: **cycles_used 8 of 10 — this is the constraint that now governs.** One more fix-and-re-panel round fits. A second would exhaust `max_total_cycles`, which is a HARD bound: on exhaustion I stop the branch, preserve everything and return BLOCKED with the unmet criteria named. runs 47 of a 20-run informational budget.

## Open Questions

- ALL SIX FINDINGS LAND ON N-13, and the panel's own read of why is worth keeping: N-13 was added *because* a control had been found blind three times, and as drafted it is the fourth instance. Its intent is right and all three of the operator's constraints are honoured — it is the execution environment that was never specified, which is one editing pass and not a redesign.
- PP-01 (high) — N-13 PART 1 says to run `check-state.sh` "with cwd at the owner root", but **cwd is inert**: `check-state.sh:22-49` resolves its root from `_selfdir` through `harness_boundary.resolve_root`, whose own comment reads "never from the environment and never from the caller's cwd (FEAT-42 T-12)". As written the worktree's copy audits the worktree and PART 1's clauses pass vacuously. Verified by me at source.
- PP-02 (high) — PART 2 assumes `post-checkout` fired at a fresh probe, but **`core.hooksPath` does not travel with a clone**: it is `--local` config, and no tracked gitconfig exists (`git ls-files | grep gitconfig` → 0). Verified by me. **This contradicts the DoD note's own claim** that `core.hooksPath` is "tracked in the repository so it travels with a clone" — the note conflates the tracked hook SCRIPTS with the untracked config that points at them. Remedy: a fourth announced-skip condition.
- PP-03 (high) — PART 1 clause 1 asserts the mismatch message is ABSENT, but N-06 PART 1 prints it whenever either side is non-empty, including on the non-gating path. Remedy: loosen to SC-16's own "no REFUSAL".
- PP-04 (high) — PART 1 carries no red-proof or discrimination step, which every other consequential assertion in this plan does. PP-01 proves the concern is not hypothetical: a PART 1 that audits the wrong tree passes clauses 1 and 2 vacuously.
- PP-05 (med) — PART 1 and SC-16 both say the owner root is read "at the reviewed commit", but `grep -c HARNESS_REVIEW_SHA check-state.sh` returns **0** (verified by me) and honouring it literally would require checking the owner root out to that ref, which N-13's own read-only rule forbids. **The honest remedy edits SC-16, which is approval-gated — the operator's, not a fix cycle's.**
- PP-06 (med) — GC6-02's non-emptiness floor exists in N-06 PART 1's prose and is **graded by nothing**. I under-read the panel digest and named only PP-01..PP-05 in my transcription dispatch; pm transcribed all six rather than dropping the one I missed, which is the right behaviour and is why the record is correct.
- FIX ORDER, which changes what a fix pass costs: PP-01 + PP-05 are ONE respelling of PART 1's invocation → then PP-03 → then PP-04 (the red proof, pinned to the corrected clause) → PP-02 and PP-06 independent. **PP-04 must come LAST in the PART 1 group**; sequencing it first pins a red proof to an assertion three other findings are about to change.
- Filed as their own tickets, untouched: #1595, #1596, #1597, #1598, #1630, #1631, #1635, #1636, #1637, #1638, #1640.
