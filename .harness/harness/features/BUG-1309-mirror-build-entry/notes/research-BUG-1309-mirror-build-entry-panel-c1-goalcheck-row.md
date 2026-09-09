# Panel cycle 1 — the goalcheck reader row was falsified, and is now corrected

**Done.** `panel.readers[2]` reads `reader: goalcheck / status: ran / persona: harness-pm /
cycle: 1`, with no `reason` key (`plan.yaml:190-193`). The stored row had claimed `skipped` under a
`harness-goal-checker` persona. It was a falsified record under rule 15: the cycle-1 goal-check ran,
harness-pm performed it, and its findings are what produced the amendment this same panel documents.

## The evidence, read independently

`notes/research-BUG-1309-mirror-build-entry-goalcheck-plan-c1-newtasks.md` is a cycle-1 goal-check of
T-10 and T-11 against the operator's stated intent. Anchors I opened:

- Title and BLUF (`:1-7`): "Goal-check — BUG-1309 plan cycle 1 — T-10 and T-11 only", verdict
  "No — not yet", explicitly "T-01..T-09 not re-graded".
- **§5 "The operator's stated intent — four clauses, individually"** (`:73-89`) grades each clause on
  its own: local-record refusals, the era set, explicit recovery, and the record-nothing rule. This is
  a goal-coverage read, not a narrower re-read — the stored `reason` was false in its own terms.
- §6 residuals (`:93-100`) name R1 (T-07's `unit` floor unowned), R2 (BE-21..BE-23 relabelled
  integration guards, DEC-217 Over clause) and R6 (approval dated 2026-09-04 over a task set since
  grown by T-10/T-11) — the drivers of the T-10/T-11 rework and T-12.

The note carries no persona line, so `harness-pm` rests on the dispatch's attribution plus the
note's location in pm's own `notes/research-*` namespace, which no other persona may write.

## The second mutation, and why

The deleted `reason` was the only record that goalcheck also ran in cycle 0. `transcription_rule`
now carries one appended sentence (`plan.yaml:177-180`) stating that goalcheck ran in cycle 0 under
run `2026-09-06-01-validator` against the whole plan, and that this row records its cycle-1 run by
harness-pm over amended T-10/T-11. Nothing else in the string changed — the pre-existing tail at
`:175-177` is byte-identical.

## Proof nothing else moved

Value file was built by loading the parsed `panel`, mutating those two keys, and dumping — never
retyped (`/tmp/panel_c1_goalcheck/step_snapshot.py`). Same computation before and after:

| Quantity | Before | After |
|---|---|---|
| `len(panel.findings)` | 11 | 11 |
| findings sorted-JSON sha256 | `01caf790…c99ad` | `01caf790…c99ad` |
| `approval` sha256 | `af260532…d0003` | `af260532…d0003` |
| `len(tasks)` / `len(decisions)` | 12 / 11 | 12 / 11 |
| `last_run` / `panel.cycle` | `2026-09-06-panelc1b-validator` / 1 | same |

All four `approval.rulings` ids resolve to live findings by explicit set membership:
`PF-1aa3b36ca9f98cdaf25b30f16e72069f`, `PF-8bfef7ee69e3adc23a65c02cfd5debd4`,
`PF-23f51fd8ee94dc42e9df11fbed42593b`, `PF-6030c547ed525627c274560e6edd9c05` — each `True`.
`should-not-exist` (fable-advisor) and `scope` (harness-code-reviewer) rows unchanged.

`check-plan-routes.py <plan.yaml>` → `0 violation(s) across 1 plan(s)`, exit 0. Its five `DEVIATION`
lines (T-04, T-06, T-07, T-10, T-12) are the expected DEC-174 carve-out output and pre-date this
change; only `VIOLATION` gates.

## Open

Nothing blocking. R6 stands untouched: `approval.status: approved` at `2026-09-04` still sits over a
task set that has since gained T-10, T-11 and T-12. Re-signature is the main session's, after the
operator sees the mismatch.
