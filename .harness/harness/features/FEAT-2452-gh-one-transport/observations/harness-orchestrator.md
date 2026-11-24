# Observations — harness-orchestrator — FEAT-2452-gh-one-transport

- 2026-11-23: plan team's pm applied cycle-1 findings but left all seven panel dispositions `open` (incl. one high); a plan with an open high finding is unsignable without overrule — folded `set-panel` dispositions into the simplify-apply product run; worth asking for the disposition table explicitly in the plan dispatch.
- 2026-11-23: set-mission --reason is capped at 240 chars (exit 11); grilling reason lines need trimming before the verb.
- 2026-11-23: OQ-3 (truncated writer stdout) answered locally: the receipt's only gate is the exact `APPROVAL-RESET:` line, which cannot appear on a never-signed plan (approval.status pending, no reset_at on disk); no remote call owed.
- 2026-11-23: main session (as orchestrator) re-attached `outputSchema`/`schemaMode` to every validator-lead dispatch, nine times in total, three times while stating in the same message that the call carried only name/agent/task/solutionSpace. A self-asserted "I checked the keys" check failed every time; the hook accepted the identical schema, so it was invisible.
- 2026-11-23: three validate rounds each surfaced the next unvalidated field of one payload class (container → blocker state → relation repository). Asking the fix builder to audit every decision-bearing field in one pass came one round too late.
- 2026-11-23: a local run of every CI `checks` step in a fresh env -i clone caught canonical-reader inventory drift (a refactor moved reads into helpers) that validate's matrix never runs; CI would have failed the PR.
