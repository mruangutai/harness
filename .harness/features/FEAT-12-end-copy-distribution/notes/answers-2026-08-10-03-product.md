# Operator answers — FEAT-12 — 2026-08-10

**CLOSED — the operator signed FEAT-12 on 2026-08-10 and this file was dispatched with that
signature as one consolidated revision (harness.md §2 — one review pass, one fix run).**

## Settled

- **D-06 is REVERSED: remove `.claude/settings.json.harness-bak` in this feature.** The plan deferred
  it because it is inert — `merge-settings.py` writes it and never reads it back. The operator ruled
  removal anyway: it is tracked on kaya's `origin/master` and names six harness scripts this feature
  deletes, so leaving it means kaya's master permanently carries a tracked file pointing at paths
  that do not exist. The plan states the cost itself: one path on T-03, one entry on T-05's pathspec.
  Fold it into the existing tasks — it is not a new task.

## Still open

- Signature on BRIEF.md and plan.yaml. The operator is reading first and will call it.
- Q1 (REQ-03 narrowed to kaya's three top-level tooling directories) and Q3 (FEAT-12 needs its own
  branch) are ratifications that ride with the signature, not separate answers.
