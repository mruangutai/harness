# Altitude simplify receipt — BUG-285 canonical reader

**Diff pin:** `8c3143bd..2367a1881ea483d5326a23268dc034c2a3b82134` (reviewed tree tip: `2367a1881ea483d5326a23268dc034c2a3b82134`).

## Finding result

**Empty result — no qualifying altitude findings.**

## Assessment

The changed read capabilities have a single authoritative home in `.claude/skills/harness/bin/artifact_accessors.py`: strict JSON, feature, plan, fleet, manifest, frontmatter, OMP, hook-payload, and GitHub-response accessors are consumed by their callers rather than reimplemented there. The legacy `feature_json_write`, `factory_config`, and `harness_yaml` reader ownership was removed rather than retained as a compatibility route. The typed manifest view is also owned at that boundary. The permanent AST inventory/audit in `check-plan-routes.py` and its classification corpus provide the compensating control for residual intentional primitive and writer-transform parsing, without creating a caller-level policy home. These match the settled boundaries and require no fold-in, briefing row, or leave recommendation.
