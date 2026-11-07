# Answers — run 2026-11-07-02-product

Asked by the main session, answered by the operator (Mike Ruangutai), 2026-11-07, after signature.

**Q:** BUG-20261006-fleet-planning-recovery landed on main today (#2177, 4a05030d), inside the 30-day rule, but SC-01 and T-01 `verify` name exactly four surviving feature folders. Should it survive the prune?

**A:** Keep it. The survivor set is five folders: FEAT-71-corpus-independence, BUG-2161-abandon-source-tickets, BUG-2141-dec174-main-orchestrator, FEAT-2037-product-document-guidance and BUG-20261006-fleet-planning-recovery. The rule is unchanged: everything with activity in the last 30 days survives.
