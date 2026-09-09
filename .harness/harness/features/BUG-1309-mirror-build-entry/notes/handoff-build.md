# Handoff — BUG-1309-mirror-build-entry, build (re-opened) — written at aee2ab19, seq-2

## Next

The operator ruled FIX on all three panel-c7 highs and the plan now specifies those remedies, so the
next act is the **main session's, by hand**: implement R-1, R-2 and R-3 exactly as
`notes/direct-packet-2026-09-08-panel-c7.md` specifies — three code edits (`merge-gate.py`
`git_merge`; `merge-gate.py` `feature_for` plus its caller; `gh-sync.py`
`_build_entry_recovery_notice`) and six named test cases, five in
`tests/integration/test-merge-gate.py`, one in `tests/integration/test-gh-sync.py`. All DEC-174
enforcement-layer work; no squad may execute any of it, and the packet supersedes the briefing's
F-01/F-02/F-03 sections. T-04 and T-05 are back at `building`; the other eleven tasks stay `done`.
After it lands: re-pin `review_sha`, qa `test_matrix` re-run, review panel c8 over the delta, pm
goal-check of the affected SCs, operator SC-10 UAT, rewritten briefing.

## Trust

- Operator ruled FIX on PANEL-1/2/3 and re-signed the BRIEF — relayed inline by the main session,
  transcribed in `notes/rulings-2026-09-08-panel-c7.md`; the BRIEF half verified-at `ea0bdd6b`
- Plan amended: T-04 `intent` derives the recovery command, T-05 `intent` carries the flag-aware walk
  and the two-or-more-owners DENY, T-05 `verify` gates 19 names and T-04's 6, D-13..D-15 added — read
  at source — verified-at `d8f4dc49`
- `approval:` bytes untouched; the plan still reads `date: '2026-09-04'` over text amended today —
  `git diff -U0` earliest changed line 203, approval is 3-25 — verified-at `d8f4dc49`
- INV-33 clear after the re-pin; ten INV-26 rows remain, the parent row new today and seven task rows
  older (`git show ea0bdd6b:…plan.yaml` read `status: review`) — verified-at `aee2ab19`
- The three code defects reproduce at the old pin, 5/5 both directions for PANEL-1 — panel c7's
  security and ui reviewers, not re-measured here — UNVERIFIED

## Dead ends

- Never let an unattributable record cause a refusal: `473d82cb` did, panel c5 failed it, `894adc0f`
  scoped it back — `notes/review-harness-qa-c5.md`
- Never dispatch a squad at `merge-gate.py`, `gh-sync.py`'s Build-refusal branch or the gate tests —
  `plan.yaml` lanes rows 34-36, 47-49, 73-75
- Never order a plan-panel re-run for these amendments: `amend` leaves approval intact and never
  resets it — `notes/rulings-2026-09-08-panel-c7.md`
- Never host the new T-04 case in `tests/unit/test-gh-sync-build-entry.py`: T-04's `verify` greps the
  integration runner's `ok    <name>` format — `notes/research-BUG-1309-planamend-c13b.md`
- Never run `gh-sync.py` for this segment: a main-session-direct phase's mirror writes are the main
  session's — `.claude/skills/harness/references/github-mirror.md`

## Working set

- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/direct-packet-2026-09-08-panel-c7.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/rulings-2026-09-08-panel-c7.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml`
- `.claude/skills/harness/bin/merge-gate.py`
- `tests/integration/test-merge-gate.py`

## Done when

Scope: R-1/R-2/R-3 land with the six named cases green and the operator returns SC-10, SC-04 and the plan signature
Authority: approval:.harness/harness/features/BUG-1309-mirror-build-entry/BRIEF.md#Approval
Authority: finding:.harness/harness/features/BUG-1309-mirror-build-entry/notes/ship-review-2026-09-08-resume.md#F-01
