# Observations — harness-orchestrator — FEAT-2452-gh-one-transport

- 2026-11-23: plan team's pm applied cycle-1 findings but left all seven panel dispositions `open` (incl. one high); a plan with an open high finding is unsignable without overrule — folded `set-panel` dispositions into the simplify-apply product run; worth asking for the disposition table explicitly in the plan dispatch.
- 2026-11-23: set-mission --reason is capped at 240 chars (exit 11); grilling reason lines need trimming before the verb.
- 2026-11-23: OQ-3 (truncated writer stdout) answered locally: the receipt's only gate is the exact `APPROVAL-RESET:` line, which cannot appear on a never-signed plan (approval.status pending, no reset_at on disk); no remote call owed.
