# BUG-1507 — panel record: the goalcheck reader row

**The record was incomplete, not the work.** `plan.yaml`'s `panel.readers` listed two rows
(`should-not-exist`, `scope`) while `check-state.sh:534` expects the reader set
`{should-not-exist, scope, goalcheck}`. The goal-check reader did run. One row closes INV-32.

## Evidence the row is `ran`, not `skipped`

- goal-check run `2026-09-08-01-product` — verdict FAIL, 9 findings, 3 of 5 DoD bullets discharged;
  artifact `notes/research-BUG-1507-goalcheck-plan-c0.md`.
- repairs landed in fix cycle `2026-09-08-1-product` — verdict PASS; artifact
  `notes/research-BUG-1507-planfix-c1.md`.
- both runs are recorded in `feature.json` `runs:` and in `STATE.md`'s log.

A `skipped` row would additionally require `persona` and `reason` (`check-state.sh:540-547`); this
row is `{ reader: goalcheck, status: ran }` — two keys, nothing else.

## What was written

Single write, via the only permitted route:
`plan-merge.py set-panel --file <plan.yaml> --value-file /tmp/bug1507-panel.yaml`, exit 0, output
`PANEL cycle 0 -> …` then `APPLIED …`. The value file was produced programmatically —
`harness_yaml.load_file(plan.yaml)`, append one reader dict, `yaml.safe_dump` — so no finding
summary was ever retyped. That matters because a `PF-` id is a content hash of its summary.

## Finding ids and summaries — before vs after

| # | id | id equal | summary equal |
|---|---|---|---|
| 1 | `PF-4d48a7518cc7333294cad13b27fdaed6` | yes | yes |
| 2 | `PF-f0a35051dae0d5f3a0b09b52a6a8b862` | yes | yes |
| 3 | `PF-0274cfb40625bb45a968c559d773bcfd` | yes | yes |
| 4 | `PF-41dcf8d793040a3bae0c6a120579d480` | yes | yes |

`(id, summary)` pair lists compared equal, 4 = 4. Dispositions unchanged: all `resolved`, with
`resolved_by` `T-05` / `T-02` / `T-03` / `D-03`.

## Everything else unchanged

`approval:` `{date: '2026-09-08', approved_by: operator, status: approved}`; top-level
`status: review`; `panel.last_run: 2026-09-08-01-validator`, `panel.cycle: 0`; `lanes:` 5 rows at
`resolved_at 4b5dbb23`; decisions `D-01..D-06`; tasks `T-01..T-05` all `done`.

## Diff

```
.harness/harness/features/BUG-1507-ready-station-signature/plan.yaml | 2 ++
1 file changed, 2 insertions(+)
```

One hunk, `@@ -63,4 +63,6 @@ panel:` — two added lines (`- reader: goalcheck` / `status: ran`)
between the `scope` row and `findings:`. Nothing landed outside `panel:`; `safe_dump`
re-serialization produced no incidental reflow. `git status --porcelain` shows plan.yaml modified
and unstaged; nothing staged, no commit.

## Confirmation

`check-state.sh` at this tree reports BUG-1507's INV-32 only as four `note` lines (one per resolved
finding). No `fail` line names BUG-1507 or INV-32.

## Open

- `check-state.sh` notes a separate, pre-existing item on this feature: run dir
  `2026-09-08-panelrow-product` exists on disk but `feature.json` does not record it. Out of scope
  here — flagged for the orchestrator's reconciliation.
