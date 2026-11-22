# Operator ruling — FEAT-2274 — 2026-11-22 — out-of-list paths (validate c2 OQ-1)

Presented after validate c2 PASS over `242f9714`: four paths changed outside the signed plan's task
`files:` lists, each with its reason in `notes/t03-decision-dispositions.md` (§ "Paths changed
outside the task `files:` lists") and in the fix-round evidence:

| Path | Task | Why |
|---|---|---|
| `tests/integration/canonical-reader-classification.json` | T-01 | three exempt rows for the narrow gates' stdlib applicability readers; the inventory refuses an unclassified reader |
| `.claude/skills/harness/SKILL.md` | T-01/T-03 | sentence made false by T-01: omp, not dispatch-guard, refuses a target outside `spawns:` |
| `.claude/skills/harness-zero-micro-management/SKILL.md` | T-01/T-03 | same correction |
| `tests/unit/test-lead-start-preflight.py` | T-01 (fix c1, V4) | standing caller test migrated from the deleted Python spawns refusal to the passthrough contract |

Recommendation given: approve all four; none adds product behaviour.

## Ruling

Mike Ruangutai: **"yes, approve all four and open the PR"**. All four paths are approved as
part of the feature's scope, and the PR is authorized.
