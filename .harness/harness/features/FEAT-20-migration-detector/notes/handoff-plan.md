# Handoff — FEAT-20-migration-detector, plan → build — written at 88b1182, seq-1

## Next

**Do not dispatch anything until the operator signs both files.** On signature: create
`feat/FEAT-20-migration-detector`, run `gh-sync.py open .harness/features/FEAT-20-migration-detector`,
then split the build by lane — **T-03 and T-04 are the ONLY dispatchable tasks** (eng-lead for
`.github/workflows/tests.yml`, product-lead→documentor for the two `docs/harness/` files). **T-01 and
T-02 are `main-session-direct` and go up to the main session, never to a lead.** Lane assignments are
`plan.yaml` `lanes.rows`, resolved at `88b1182`.

## Trust

- Approval is `pending` in both artifacts; nobody in the plan squad signed — `plan.yaml:4-7`,
  `BRIEF.md:232-234` — verified-at 88b1182
- Five of eight surfaces are `main-session-direct`, incl. `layout_migration.py` as a carve-out BY
  CONTENT because INV-27's verdict is computed from its return value — `plan.yaml` `lanes.rows` —
  verified-at 88b1182
- All four `change_type` values (`logic`, `cross_module`, `config`, `docs`) exist in the project test
  matrix, so the qa gate is derivable — `.harness/harness.json` `test_matrix` — verified-at 88b1182
- No task moves any file; SC-10 is the criterion that holds unit-0 scope — `BRIEF.md:189` — verified-at 88b1182
- The plan's baseline is `88b1182`, not eng-lead's cited `cf3af8f`; the tree fast-forwarded mid-run —
  `git rev-parse --short HEAD`, `.git/logs/HEAD` — verified-at 88b1182
- Q3's reader-table asymmetry is an instruction TO T-01's implementer, already accepted — team digest
  Q3, `runs/plan-product/digest.md` — verified-at 88b1182

## Dead ends

- Do not re-litigate the per-surface partition, the two green-end fixtures, or the vacuity fix; they
  are the settled output of two send-backs — `runs/plan-eng/review-architecture-c2.md`,
  `notes/review-harness-ui-reviewer-plan-c1.md` — verified-at 88b1182
- Do not commission `DESIGN.md` or a prototype; the gate fired and returned no, twice independently
  — team digest S3/S4, `runs/plan-product/digest.md` — verified-at 88b1182
- Do not "fix" `.github/workflows/tests.yml:110-114`'s false claim inside T-03; it is pre-existing,
  issue #279 is OPEN, and T-03 is forbidden to copy it forward — team digest Q4 — verified-at 88b1182
- Do not reopen anything in the map hand-off; it is the settled record for the whole effort —
  `.harness/notes/map-336-phase1-handoff-2026-08-14.md` — source: operator, 2026-08-14

## Working set

- `.harness/features/FEAT-20-migration-detector/BRIEF.md`
- `.harness/features/FEAT-20-migration-detector/plan.yaml`
- `.harness/features/FEAT-20-migration-detector/STATE.md`
- `.harness/features/FEAT-20-migration-detector/runs/plan-product/digest.md`
- `.harness/notes/map-336-phase1-handoff-2026-08-14.md`
