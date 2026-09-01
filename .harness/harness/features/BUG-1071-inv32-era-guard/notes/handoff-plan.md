# Handoff — BUG-1071, plan → build — written at 75daa3bb, seq-1

## Next

Implement the era guard in `check-state.sh`'s INV-32 block, main-session-direct under
DEC-174 — this is gate-script and validator-test code, so it must not run through the
enforcement path it changes. Test-first: the pre-era exemption, the boundary in both
directions, the undated-approval warn, and a mutant proving the guard binds.

## Trust

- INV-32 fires on all 32 approved plans and 0 can satisfy it — `check-state.sh` exit 1,
  `grep -c VIOLATION` = 32, all INV-32; no `plan.yaml` in the tree holds a `panel:` key —
  verified-at 75daa3bb
- The cause is the absent era boundary, not the rule — `check-state.sh:176-182` iterates
  every plan and makes any approved plan without a `panel:` block a hard `bad` —
  verified-at 75daa3bb
- FEAT-45's own plan is among the 32, signed 2026-08-30 with no `panel:` key, so the
  feature that shipped the invariant does not satisfy it — verified-at 75daa3bb
- `approval.date` is the only durable signature timestamp and is present on 31 of the 32;
  the newest is FEAT-45 at 2026-08-30 — verified-at 75daa3bb
- `FEAT-40-harness-writes-done` is `approved` with no `approval.date` at all, so its era
  cannot be placed — verified-at 75daa3bb

## Dead ends

- Backfilling a `panel:` block into 32 historical plans — a panel cannot be retroactively
  run, so the record would be fabricated — source: operator selection, 2026-08-31
- Grandfathering by `_is_shipped` alone — FEAT-41 is `Building` and approved pre-panel, so
  it would still fail; its `feature.json` status is `Building` — verified-at 75daa3bb
- Downgrading INV-32 to a warn wholesale — that deletes the invariant for new work, which
  is the half worth keeping — source: operator selection, 2026-08-31

## Working set

- `.claude/skills/harness/bin/check-state.sh` — INV-32 block, lines 174-242
- `.claude/skills/harness/bin/test-check-state.py` — `_inv32_plan`, `_inv32_run`, `case_inv32`
- `.claude/skills/harness/templates/plan.yaml` — the `approval:` mapping shape
- `issue://1071` — the filed defect and its measurements
