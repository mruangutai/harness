# Observations — harness-orchestrator — FEAT-2581-feature-record-package

- 2026-11-27: plan phase closed three FAIL runs (plan-product, repanel-product, repanel2-product), one cycle each. Every substance apply by pm leaves unread text by construction, so a re-panel with apply-after-read can never end clean; inserting one in-run re-read (c3) ended with no unread text but the second read raised four new med findings, all in T-03's verify prose.
- 2026-11-27: findings fell high to med but stayed inside one mechanism — a verify block specifying a verifier program in plan text. Each hardening pass gave the reader new surface to find gaps in.
- 2026-11-27: pm's in-run record-panel from panel-cN.md already carried goalcheck with true provenance in cycles 2 and 3; re-recording from the lead digest would have replaced reader reasons with `none`, so I ran record-panel myself only for cycle 1.
- 2026-11-27: task dispatch refused `outputSchema: null` and accepted only the injected strict lead schema with schemaMode strict.
