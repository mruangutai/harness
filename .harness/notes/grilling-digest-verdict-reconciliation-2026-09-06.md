# Grilling — digest verdict reconciliation — 2026-09-06

## Destination
Ship a state-gate fix that prevents a completed lead run from recording a feature-level verdict that contradicts its durable digest.

## Settled
- A completed lead-hosted run with a valid durable digest must have an exactly equal `VERDICT:` and `feature.json.runs[].verdict`; a mismatch is a blocking state-check violation.
- The state gate detects and reports divergence; it does not auto-repair either record.
- Scope is only completed lead-hosted runs with durable digests. Non-lead, incomplete, missing, and legacy-run behavior remains unchanged.
- This is BUG-440 and follows the full Harness BUG flow. The known cause skips the debug investigation segment.
- `check-state.sh` and its test are enforcement-layer surfaces, so their implementation is main-session-direct.

## Not yet specified
- None.

## Out of scope
- Retroactive repair of historical records.
- Changing cycle accounting, feature.json schema, or digest-return semantics.

## Facts I verified (so pm does not re-derive them)
- FEAT-22 recorded one `digest.md` `FAIL` versus `feature.json` `PASS` mismatch after reconciling 17 runs manually.
- `check-state.sh` validates a completed lead digest structurally but does not compare its verdict with the matching `feature.json` run entry.
- `feature.json.runs[]` has `id`, `squad`, and `verdict`; its run id maps to `runs/<id>/`.
