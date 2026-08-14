# Answers — FEAT-20-migration-detector — operator ruling on the goal-check escalation

Answers the blocking question raised by run `2026-08-14-2-product` (pm's goal-check),
recorded at `434307a`. Given by the operator (Mike Ruangutai) on 2026-08-14, directly in
the orchestrator's turn rather than through the main session's answers round-trip.

## Q1 — SC-10, the file-boundary criterion — RULED: option 1

**The operator signs the shipped-surface reading.** SC-10 binds what this feature *ships*,
which is exactly the eight files it enumerates. The harness's own per-feature bookkeeping —
`STATE.md`, `feature.json`, task statuses in `plan.yaml`, run digests, receipts, handoff
notes — is outside the criterion's subject, not a violation of it.

**`BRIEF.md`'s text stands as signed.** No edit to `BRIEF.md`, no re-plan, no change to any
shipped or bookkeeping file. This note is the whole of the change.

**SC-10 is therefore MET**, and all 15 success criteria are met.

### The evidence the ruling rests on, measured at `434307a`

- `git diff --name-only 88b1182..434307a` — 27 paths. The 8 outside `.harness/` are
  `layout_migration.py`, `test-layout-migration.py`, `test-check-state.py`,
  `check-state.sh`, `.github/workflows/tests.yml`, `run-unit-tests.sh`, `DECISIONS.md`,
  `DECISIONS-INDEX.md` — a one-for-one match with the criterion's closed set.
- `git diff --diff-filter=R 88b1182..434307a` — empty. "Nothing moves" holds outright.
- `layout_migration.py` on the live tree — `features: CLEAN — evidence legacy`,
  `docs: CLEAN — evidence legacy`, exit 0. The tree is entirely on the old layout, so no
  reader was migrated. The feature's own detector confirms the feature stayed in its lane.

### Why this needed the operator and could not be settled below

`BRIEF.md` carries the operator's signature. Deciding that a signed criterion means
something narrower than its words is a signature act. pm returned `ESCALATE` and explicitly
declined to adopt the reading; the orchestrator declined to mark the criterion met, waived
or edited. Both were correct — a criterion reinterpreted by the agents it exists to
constrain is how an approval gate erodes.

### What was deliberately NOT decided here

The criterion's wording is left unimproved. It will trip the same way on the next feature,
because every feature writes the same bookkeeping. Rewording it — and the broader question
of whether containment criteria should state an outcome ("nothing is renamed, no reader is
migrated") rather than enumerate permitted files — is live, unowned, and carried to the
briefing's backlog. It is not part of this ruling.

## Effect

The feature's goal is met. The orchestrator proceeds to close-out — ship-refresh and
feature-close distillation — and then the CEO briefing. Merge and ship acceptance remain
the operator's, unchanged.
