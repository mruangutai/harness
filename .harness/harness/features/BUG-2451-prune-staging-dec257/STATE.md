# STATE

## Current

- feature: BUG-2451-prune-staging-dec257
- run: .harness/harness/features/BUG-2451-prune-staging-dec257/runs/2026-11-27-04-validate-c3-validator/state.yaml
- squad: validator
- status: validate c3 FAIL — one new must_fix MF-3R (T-01, substance, med): a DEC-238/DEC-257 heading without the literal `## DEC-NNN ` anchor empties the claim scan (fail-open); MF-2R's four acceptance lines met on ordinary probes, A-3 resolved; SC-01..SC-04 and both perspectives met; awaiting operator on OQ-B (accept residual, or grant a round)
- mission: patch
- station: review
- cycles_used: 0 / 10 (two main-session-direct fix rounds are uncounted because they were not runs: fix-c1 10823d58 inside the ruling, fix-c2 c9596b9a under the operator's extra round)
- review_sha: a97dbc6a8337cfbe9402d2a727aa28797a1efaf8 (contains c9596b9a and merge 6e8c8c58; stale if any fix commits)
- rework: ruling 1 of 1 round spent plus the operator's one extra MF-2R round spent; spend reads 2 rounds, 37 of 45 minutes; no further rework authorised
- deviation: the c3 dispatch carried outputSchema and schemaMode against the main session's instruction (orchestrator error); the lead's digest validated and landed

## Open Questions

- OQ-B (blocking): accept MF-3R as a recorded residual and ship, or grant one more test-only round — runs/2026-11-27-04-validate-c3-validator/digest.md
- Backlog kept by the operator (still true at the pin): A-1, A-2, SEC, SCHEMA
- New c3 advisories (not gating): related-claim-in-another-decision scope trade (DEC-250 probe), DEC-257/DEC_257 co-edit, `Force-`+newline+`stage` split-token miss, red-first census omits the DEC_257 literal
