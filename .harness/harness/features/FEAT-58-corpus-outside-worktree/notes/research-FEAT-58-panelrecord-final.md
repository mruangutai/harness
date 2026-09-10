# Panel record — final panel transcribed, GC5-01 corrected — FEAT-58

**The `panel` key now records `planpanelfinal-validator` cycle 0 at `severity_max: high`, and the
nine stale `disposition: open` rows are corrected.** Four new findings (PL-01..PL-04) transcribed in
the digest's own fix order; the three highs recorded UNRESOLVED and carried to the operator's
batched signature review; VL-01..VL-09 carried forward inside `findings:` with every `PF-` id,
label, severity, reader, reporter, `lands_on`, `summary` and `fix_order` byte-verbatim and only
`disposition` changed. Nothing was re-ranked, re-worded, merged, split, waived or risk-accepted.
Transcription only.

## Transcribed counts

`panel.findings` holds 13 rows: **high 6, med 1, low 5, info 1** (4 new + 9 carried).
New, in the digest's fix order:

| label | sev | reader | id | lands on | disposition |
|---|---|---|---|---|---|
| PL-01 | high | should-not-exist | `PF-1d3964400ea46a7edd0c8330c9e15668` | N-06 PART 1, REQ-05, SC-12 | open — unresolved |
| PL-02 | high | should-not-exist | `PF-1cfbb60f627e9e729ce7f666a707ea4d` | D-12 / N-02 check 5 / N-06 PART 3, SC-09 | open — unresolved |
| PL-03 | high | scope | `PF-865cca158450fe71c0c7bec43669fe36` | N-10 PART 7 (c), SC-14, REQ-03 | open — unresolved |
| PL-04 | med | validator-lead | `PF-329bd0b3fbc7c8a03dbcf45a87666f0f` | N-09 PART 1 or N-06 PART 4 | open — med, unresolved |

Ids computed once with `panel_findings.py id --reader … --summary …` on the row's own values as
written. PL-04's `fix_order` carries the panel's ranking rationale intact: med on its own merit,
ranked to land WITH the two highs because it is their common root; PL-01+PL-02 both edit N-06 and
must land in one pass; PL-03 independent, one clause. PL-02 carries `remedy_route:` — the SC-09
amendment in `BRIEF.md` is the OPERATOR's, not pm's and not a fix cycle's (panel Q1, blocking).

Both readers `status: ran`, personas recorded, neither skipped, no `on_fail` loop fired (stated in
`note` and in each reader's `note`). `should-not-exist` holds no write grant, so its two highs are
transcribed from `runs/planpanelfinal-validator/digest.md`; its third (info, affirmative) return is
recorded under `assessed_and_dismissed` rather than dropped. Both `should-not-exist` highs
reconciled at **the reader's own severity (high), deliberately NOT raised to critical — decided,
not averaged**; nothing lowered (`severity_reconciliations`, four rows).

## The VL correction (GC5-01)

| id | now | `resolved_by` |
|---|---|---|
| VL-01 | resolved — **DISSOLVED** by the Q6 strike, not remedied | D-14 |
| VL-02 | resolved — APPLIED | N-09 PART 3 SELF-SCOPE + D-13 |
| VL-03 | resolved — APPLIED | D-15 + N-06 PART 2 |
| VL-04 | **ruling**, not a defect (blind class ACCEPTABLE AS SCOPED) | the ruling itself, carried in N-12's intent |
| VL-05 | resolved — APPLIED | N-09 |
| VL-06 | resolved — APPLIED | N-01 |
| VL-07 | resolved — **DISSOLVED**, no residual | the operator's DoD amendment + `summary_caveat:` |
| VL-08 | resolved — APPLIED | the five SC edits |
| VL-09 | resolved — discharged | the operator's closure; post-fix goal-check exists and PASSED |

VL-07's added `summary_caveat:` states its frozen summary quotes a DoD sentence the operator has
since WITHDRAWN, preserved verbatim as historical record — a reader must not act on it.
`panel.prior_cycle` carried intact: `planpanel3-validator`, all **13** F-01..F-13 rows, same keys
and values; `carried_because` extended to note this replacement preserves it too.
`orchestrator_verified_premises:` records both measurements (89 dirs vs 79 records; `deny()`
`:63-66` exit 0 and allow `:91-92` exit 0) explicitly attributed to the ORCHESTRATOR's own tier.

## `set-panel` stdout (exit 0)

```
PANEL cycle 0 -> …/features/FEAT-58-corpus-outside-worktree/plan.yaml
APPLIED …/features/FEAT-58-corpus-outside-worktree/plan.yaml
```

## Nothing else changed

`git diff --stat` over the feature directory lists `BRIEF.md`, `feature.json`,
`observations/harness-pm.md` and `plan.yaml` — the first three are **pre-existing uncommitted work
from earlier cycles, untouched by this dispatch** (mtimes 13:29:07, 14:07:52, 13:44:14 against this
write at 14:13:32). **BRIEF.md was not touched.** In `plan.yaml` every hunk from this write is inside
`panel:` (lines 552–1100); the `decisions:`-labelled hunks at old 140/264/420/441 sum to exactly the
+110-line offset that shifts `panel:` from old 443 to new 553, so they predate this write, and every
`tasks:`-labelled hunk starts at new line 1211 — past the panel block. `cmd_set_panel` splices only
the indexed `panel` line range (`plan-merge.py:1067-1078`), carrying all other lines byte-for-byte.
Read back from disk: `status: plan`, `approval.status: pending`, 11 tasks, 15 decisions — unchanged.

## Open

- Q1 (the panel's, carried, blocking): PL-02's remedy needs the operator to amend SC-09 in
  `BRIEF.md`. No agent in this chain may make that edit, and no high may be risk-accepted here.
