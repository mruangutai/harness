# Observations — harness-orchestrator — BUG-2295-handoff-one-per-phase

- 2026-11-22: Grilling named tests/unit/test-check-domain.py as the test home; the file does not exist at dd04e52a — handoff shape cases live in tests/integration/test-check-domain-post.py. Re-anchoring grilling facts at the cut commit before dispatch saved pm a dead end.
- 2026-11-22: The patch-product task call carried outputSchema/schemaMode despite the assignment forbidding them; the host reported them as hook-injected and the lead return validated and closed normally. Flagged, not actionable here.
