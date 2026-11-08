# Observations — harness-orchestrator — BUG-2169-guard-yaml-reimport

- 2026-11-07: set-mission's judgement reason is capped at 240 chars (feature-schema.json); the grilling's full `reason:` line exceeds it and must be condensed before the verb accepts it.
- 2026-11-07: Under this host (runtime omp) the product lead returned its object as final-message JSON; no yield hook appended the fenced durable record to runs/<id>/digest.md, so a valid PASS return could only be closed with --refused-return --verdict BLOCKED plus a continue judgement. Re-dispatching the lead to "re-yield" changes nothing — the append is hook-bound to a live runtime claim.
