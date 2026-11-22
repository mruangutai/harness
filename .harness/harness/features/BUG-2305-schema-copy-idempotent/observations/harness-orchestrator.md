# Observations — harness-orchestrator — BUG-2305-schema-copy-idempotent

- 2026-11-22: Patch intake dispatch sent with no outputSchema/schemaMode; the host returned the call carrying the hook's injected pair plus the #2240 note, so the ticket's persistence mechanism was observed first-hand in this run. check-state INV-37 (no build-entry receipt) is the expected pre-signature state; gh-sync open is main's at build entry.
