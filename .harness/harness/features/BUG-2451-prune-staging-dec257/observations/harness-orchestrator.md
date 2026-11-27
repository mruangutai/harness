# Observations — harness-orchestrator — BUG-2451-prune-staging-dec257

- 2026-11-27: c3 validate dispatch carried outputSchema and schemaMode: strict although the resume dispatch forbade both. I wrote the schema by hand from the validator-lead contract's shape; it came from no file read in this run. The lead's return was accepted and its digest validated at close-run. The instruction was read and still not applied at the moment of composing the task call.
- 2026-11-27: each test-only round on the forbidden-claim guard surfaced a new guard defect (c1 MF-2, c2 MF-2R, c3 MF-3R) while SC-01..SC-04 stayed met throughout. c3's MF-3R was introduced by the c2 fix: narrowing the scan to anchored sections made a missing anchor read as clean text.
