# Q4 — Cycle-13 SIMPLIFY routing correction

**Decision:** Approved by the operator on 2026-08-28.

The max-13 authorization already permits the full downstream sequence: configured QA, SIMPLIFY including its single warranted apply, commit, immutable re-pin, Review sync, and the full validator panel. R-01—the resolver consolidation identified by `validate-fix-c13-simplify-eng`—is within that existing SIMPLIFY apply, not an additional post-panel source-fix cycle. Keep `max_total_cycles: 13`. Apply only R-01 under the one-fix ceiling, rerun required QA, then continue to the panel. No further fix is authorized if that panel fails; only panel PASS may proceed to goal-check, documentation, UAT handling, and ship decision.
