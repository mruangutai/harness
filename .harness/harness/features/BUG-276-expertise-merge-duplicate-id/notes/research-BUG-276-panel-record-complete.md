# Panel record completed — BUG-276

**The panel record is now complete and INV-32-clean: three reader rows, nine findings, no high
finding left open.** One write, `plan-merge.py set-panel`, exit 0. Nothing outside `panel:` moved —
`approval.status: pending`, top-level `status: plan`, 2 tasks, 9 decisions, `lanes.resolved_at:
6d969ed3` all re-read unchanged after the splice.

## What was missing, and is not any more

1. **The `goalcheck` reader row.** INV-32 (`check-state.sh:534`) expects
   `{should-not-exist, scope, goalcheck}`; only the first two were recorded, so the gap would have
   fired at signature. Recorded `status: ran` (it ran, and its six findings are on disk), persona
   `harness-pm`, with the PRODUCT-segment ordering, its artifact path, and the no-run-directory fact
   that explains `feature.json`'s `2026-09-07-goalcheck-product-no-rundir`.
2. **The goal-check's six findings.** The record carried three of nine — a third of what the panel
   found. All six transcribed from
   `notes/research-BUG-276-goalcheck-plan-c0.md` at their own severities, never reassigned.

## The nine findings as they now stand

| id | reader | sev | disposition |
|---|---|---|---|
| PF-8eac8a4b4f41d3ea8f759cdec6e73186 | should-not-exist | med | open (D-09, operator to settle) |
| PF-d6fb0ad9a0491cc93c7ac648cd092e8c | should-not-exist | low | open (rejected, reason recorded) |
| PF-9f0a5387a328f3997e3d0b55b95e076d | scope | low | resolved, T-02 |
| PF-59b9da56871cca170a7f66678c292035 | goalcheck | med | open — F-01, D-07's separate defect |
| PF-fa07abe46cb1b84dc4cfa20dd9f63996 | goalcheck | high | resolved — F-02, BRIEF Problem restated |
| PF-d92aa22ff6536470a2ea63c104c04546 | goalcheck | high | resolved, T-01 — F-03, trimmed to 9 and 11 |
| PF-15e24dab70b6caca5bf5ba4837356157 | goalcheck | low | open — F-04, correction the operator must read |
| PF-a61ef43ee533a58c480f0002e0be4b96 | goalcheck | med | resolved, T-01 — F-05, D-08 behavioural tails |
| PF-1f9cd11c94c62290357384a3935fd1a0 | goalcheck | info | resolved, T-02 — F-06, trace names the case |

**Every open finding is info/low/med.** The two high findings are resolved, so they gate nothing
(`check-state.sh:527-533`) — and they stay recorded at **high**, because downgrading a resolved
finding falsifies what was found.

**Two findings are open on purpose, not by omission.** PF-59b9… is a real unfixed defect the plan
deliberately excludes (D-07) and recommends as its own ticket; PF-15e2… is the inverted-premise
correction the operator must read at signature — resolving it would hide it.

## Verification (re-read, not trusted)

- All nine ids recomputed with `panel_findings.py id` against the summaries **as stored in
  plan.yaml after the write**: nine of nine match. The three pre-existing ids are unchanged and
  their summaries, dispositions and notes are byte-identical (lines 79-108).
- `panel.readers` = 3 rows, each `status: ran`; `panel.findings` = 9; `last_run:
  2026-09-07-03-validator`, `cycle: 0`.
- plan.yaml is untracked in this worktree, so no git diff baseline exists — verification is by
  re-read of the file plus the structural counts above.

## Open questions

None. The two open goalcheck findings are operator reading material at signature, not questions
blocking this run.
