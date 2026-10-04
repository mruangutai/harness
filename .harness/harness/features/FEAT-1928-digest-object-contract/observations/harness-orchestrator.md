# Observations — harness-orchestrator — FEAT-1928-digest-object-contract

- 2026-10-03: The pre-cutover hook releases a lead claim before the validator-owned append of its fenced block, so a lead whose return object was accepted leaves a prose-only digest.md that close-run refuses at stage digest; preserve the returned object as runs/<run>/return-object.json for main to render, never hand-author the fence.
- 2026-10-03: check-state refuses cycles_used < count of FAIL runs; a lead FAIL that only awaits a main-session signature still forces the regate run after it to carry one cycle.
- 2026-10-03: check-domain refuses orchestrator/lead writes to agent://Main and xd://report_issue, so every main-session instruction must ride the return and the handoff note.
- 2026-10-03: dispatch-guard reads the HARNESS-FEATURE line from the task field, not the shared context field of a batched task call.
