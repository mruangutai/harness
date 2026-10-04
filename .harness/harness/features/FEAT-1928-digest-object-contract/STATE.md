# STATE

## Current

- feature: FEAT-1928-digest-object-contract
- run: main-session-direct remediation
- squad: main-session (DEC-174)
- status: building
- tasks: T-01 done, T-02 building, T-03 done, T-04 done, T-05 building
- review_sha: none; the previous review is superseded and is not a ship claim
- cycles_used: 5 of 10, including both observed live-probe send-backs
- evidence: native null/retry 18/18; actual claim lifecycle 28/28; refactored authorization suite ALL PASSED; canonical-reader self-test ALL PASS
- remaining: integrate origin/main af2a958a; finish signed verification and simplification; commit clean source; refresh pin-bound receipts; independent validation; ship
- grade-2 reason, authorized_destination: keep identity, checkout, registered-run and exact-path checks in one complete authorization decision rather than scatter its coupled proof across single-use predicate wrappers.
- grade-2 reason, run_live: the lifecycle operation and its mandatory session/claim/run-record cleanup belong to one try/finally; splitting that lifetime would obscure which resources are still live.
- grade-2 reason, receipt_header: keep the small provenance envelope assembled in one place so the distinction between executed binary identity and release-source metadata remains visible.
- briefing: notes/ship-review-validate-validator.md records the superseded panel, not current ship readiness
- next: fresh pinned independent review after all source and live verification

## Open Questions

- None. SC-06 preserves 291 cases and exactly 14 operator-approved intentional deltas; canonical-reader verification and native YieldTool-path evidence remain mandatory.
