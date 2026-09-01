# STATE

## Current

- feature: FEAT-50-run-artifact-integrity
- run: .harness/harness/features/FEAT-50-run-artifact-integrity/runs/2026-08-31-3-product/state.yaml
- squad: none
- status: awaiting-user

Plan phase COMPLETE and at its user gate. `BRIEF.md` and `plan.yaml` are drafted,
reviewed, panelled and left `pending`; only the main session signs. Five segments ran:
product authoring, the eng four-angle simplify pass plus architecture review, the
validator design-contract check, the panel goal-check against stated intent, and the
`plan-panel` team. Two fix cycles were applied to the draft; 4 of 10 cycles used,
6 runs recorded.

The plan covers issues #1056, #1057 and #1058. 7 REQ (all traced), 16 SC, 8 tasks
(6 `main-session-direct` under DEC-174, 2 `team`), 8 decisions, 12 lane rows,
`panel:` recording 3 readers `ran` and 7 open findings at `severity_max: high`.

Gates run at 75daa3b: `check-plan-routes.py` exits 0, `0 violation(s) across 1 plan(s)`,
`examined 46`. Suites untouched and green: unit exit 0 / 0 `^FAIL ` / 1463 lines,
integration exit 0 / 0 `^FAIL ` / 1945 lines. `check-state.sh` exits 1 with exactly 32
INV-32 rows before AND after — this feature adds none while pending.

Three defects were found live inside this planning run and are corroborating evidence,
not noise: #1058 reproduced (a product lead reused `runs/2026-08-31-01-product/` and
its `digest.md` now holds cycle-2 content, destroying the cycle-0 record); three lead
`digest.md` files fail the DEC-156 contract; and the reason they did is measured —
`check_artifact_file` resolves a lead's relative `artifact:` path against the MAIN
checkout, so for every lead running in a worktree the file is not found and the check
is SKIPPED. That is the same blind spot #1057 names, in a fourth place the plan does
not yet cover.

## Open Questions

- Q1 (blocking, operator): INV-32 is retroactively red across 32 approved plans, so
  "check-state exits 0" cannot be met by fixing these three issues. Rule between
  (a) scope INV-32 to plans approved on or after DEC-207, (b) backfill 32 signed plans
  (PRINCIPLES rule 15 forbids it; recorded available and not recommended), or (c) the
  shipped form — no violation naming FEAT-50 and an identical row count. The plan
  carries (c) and plans no INV-32 work. Record the answer as an
  `## Operator ruling — INV-32` section in `notes/answers-2026-08-31-plan.md`, NOT in
  `approval.rulings`, which `check-state.sh` validates against `panel.findings`.
- Q2 (blocking, operator): two `high` panel findings are open and un-overruled, so
  INV-32 will refuse this plan at signature. Either resolve them in a fix cycle and
  re-transcribe `panel:`, or record an overrule in `approval.rulings` carrying
  `finding` (a `PF-` id present in `panel.findings`), `who`, a `YYYY-MM-DD` `date`,
  and `ruling: overrule`. All four are validated.
- Q3 (blocking, operator): the fourth defect above is verified, in scope by nature and
  outside the three filed issues. Widen FEAT-50 to cover it, or file it as its own
  ticket?
- Q4 (non-blocking, harness owner): `check-state.sh` INV-6 fires for a plan-phase
  validator run, but DEC-207 says a plan-phase gate grades a pending specification
  WITHOUT a `review_sha`. The invariant cannot tell a specification review from a code
  review, so a correct plan phase is structurally red.
