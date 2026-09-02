# Handoff — FEAT-54-handoff-done-when, plan → signature — written 2026-09-02, seq-2

## Next

Do nothing until the operator signs. The revised plan is complete and pending signature: BRIEF.md
`## Approval` and plan.yaml `approval:` both read pending, and only the main session may sign
(`plan-merge.py sign-approval`). Two things ride the signature: whether to record the batched
2026-09-02 ruling as `approval.rulings` (nothing else can — DEC-120), and whether to rule on the
four `open` panel findings (three low, one info) or sign over them. After signature the build
starts at T-01, main-session-direct like 10 of the 12 tasks under DEC-174.

## Trust

- The feature is FEAT-54 everywhere: dir, ids, notes, run records — `grep -rn FEAT-52` over the
  feature dir returns only STATE.md's and `notes/research-FEAT-54-planrevision-c2.md`'s commentary
  ABOUT the rename — verified-at working tree by running it.
- The three operator rulings are in the plan: write-time-only resolution as D-10 with T-01/T-02/
  T-06(e1,e2)/T-07 and BRIEF REQ-06/SC-15; D-04 + T-09/T-12/SC-09 untouched; no T-13, no D-09,
  SC-07 rewritten — verified by reading plan.yaml and BRIEF.md back after each run.
- 12 tasks T-01..T-12, decisions D-01..D-08 + D-10, `status: plan`, `approval.status: pending` —
  verified by parsing plan.yaml through harness_yaml.
- `check-plan-routes.py` reports 0 violations across 6 plans; the DEVIATION lines are the declared
  DEC-174 carve-outs — verified-at working tree by running it.
- Panel c2 ran with both readers, `severity_max: med`, nothing high/critical/unrated; its record is
  plan.yaml `panel:` (cycle 2, three readers incl. goalcheck, 7 findings) — validator digest
  `runs/2026-09-02-c2-validator/digest.md`, transcription `notes/research-FEAT-54-planfix-c2c.md`.
- Goal-check c2 says the plan DELIVERS the stated intent: 0 uncarried settled lines, 0 out-of-scope
  violations — `notes/research-FEAT-54-goalcheck-plan-c2.md`. Its F-03 was dismissed at source by
  the panel; its F-01 is closed by the c2 transcription.
- INV-32 wants three panel readers on an APPROVED plan (`check-state.sh:519`); all three are now
  recorded — verified by reading the constant at source and the landed key.
- cycles_used 8 of 10 — the revision plus three fix cycles. UNVERIFIED: whether a further panel
  rerun would be needed if signature triggers more repairs; the budget has 2 left.

## Dead ends

- Do not `Edit`, `Write` or redirect into plan.yaml: one writer, `plan-merge.py`. `apply` is
  add-only (exit 7 on a changed value); `amend --show` then `--expect-sha256` changes a field;
  `set-panel` replaces the panel — verified this run by using each.
- Do not try to rewrite the top-level `feature:` key: no verb can. Renaming a feature means
  deleting plan.yaml and re-creating it with `apply` from a full proposal — verified-at
  plan-merge.py:516-543 and by doing it.
- Do not pass relative paths or shell variables to a write command: `bash-write-guard` resolves
  relative paths against the MAIN checkout and refuses any unexpanded `$var` target. Literal
  absolute worktree paths only — verified by three refusals this run.
- Do not open a pre-signature fix dispatch for a panel finding: DEC-207 routes them into the one
  batched review at the gate.
- Do not treat the four `open` findings as defects to fix: they carry no ruling and none gates.

## Working set

- .harness/harness/features/FEAT-54-handoff-done-when/plan.yaml
- .harness/harness/features/FEAT-54-handoff-done-when/BRIEF.md
- .harness/notes/grilling-handoff-done-when-2026-09-02.md
- .harness/harness/features/FEAT-54-handoff-done-when/notes/research-FEAT-54-goalcheck-plan-c2.md
- .harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-02-c2-validator/digest.md
