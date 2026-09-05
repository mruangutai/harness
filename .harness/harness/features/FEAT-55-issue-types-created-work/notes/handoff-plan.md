# Handoff — FEAT-55, plan → signature (round 4) — written at 0141315d, seq-7

## Next

Take the operator's FOURTH batched signature pass. Pass three's five rulings are applied in one
consolidated revision (c6), the SC-06 gap they opened is closed (c7), and the cycle-4 panel returned
PASS with `severity_max: med` and `must_fix: []`. **Nothing gates the signature.** Eleven findings
ride this pass, all `med`/`low`/`info`, each carrying a `fable-advisor` recommendation by operator
instruction. Either sign with `sign-approval --overrule PF-ID:<reason>` per accepted finding, or
order a fourth ruling batch first — but only TWO cycles remain of ten. Collect any rulings into ONE
`notes/answers-<runid>.md`, then dispatch exactly one consolidated revision. Cited: plan.yaml
`panel:`, STATE `## Open Questions` Q1–Q12.

## Trust

- All five c3 rulings are in the plan and the cycle-4 `scope` reader re-verified each HOLDING at
  source — `runs/2026-09-05-27-validator/digest.md` `discharged_rollcall` — verified-at 0141315d
- R1 is no longer inert: the three `FAKE_TYPES=partial` cases seed a declared-type `created`
  remnant, so a backfill-before-refusal implementation reddens — plan.yaml T-03 F / T-05 G / T-07 I
  — verified-at 0141315d
- Neither approval fragment moved; both read `pending` — plan.yaml `approval:`, BRIEF.md
  `## Approval` — verified-at 0141315d
- `panel:` holds ELEVEN findings, all seven carried ids reproducing, nothing above `med`, and its
  readers block is `reader:`-keyed with three entries per the SIGNED FEAT-52 precedent, so INV-32
  has no hard BAD at signature — `bin/check-state.sh:533-546` — verified-at 0141315d
- Intent delivered, unhedged YES, 0 route violations — `notes/research-FEAT-55-goalcheck-plan-c6.md`
  — verified-at 0141315d
- Both readers RAN at cycle 4, neither skipped, and the advisor consult RAN and moved three carried
  items — `.harness/notes/analysis-fable-advisor-consult-FEAT-55-c4.md` — verified-at 0141315d
- The advisor's Q2 deferral rests on DEC-205's rewrite-in-place rule, which the validator lead did
  not re-read — `runs/2026-09-05-28-validator/digest.md` `adequacy_notes` — UNVERIFIED

## Dead ends

- No pre-signature fix dispatch for any panel finding, gating or not — `skill://harness` plan phase,
  DEC-176 — verified-at 0141315d
- Do not re-run the goal-check or the panel before a revision — plan.yaml `panel.cycle: 4` —
  verified-at 0141315d
- Do not pin `review_sha`: cycle 4 graded a specification, `code_grade: n_a` — feature.json `runs` —
  verified-at 0141315d
- Do not trust a line anchor stored inside a `panel:` finding: the cycle-4 transcription rewrote the
  block wholesale — `notes/research-FEAT-55-panel-transcription-c4.md` — verified-at 0141315d
- `apply` cannot revise an existing task or decision: add-only, exits 7. `amend` is the verb —
  `plan-merge.py --help` — verified-at 0141315d
- Do not mirror to GitHub: this plan is unsigned — `references/github-mirror.md` — verified-at
  0141315d
- Do not re-raise the old Q10: the `step:`-keyed two-entry readers block was a FEAT-55 transcription
  defect, now corrected — `notes/research-FEAT-55-panel-transcription-c4.md` — verified-at 0141315d

## Working set

- .harness/harness/features/FEAT-55-issue-types-created-work/plan.yaml
- .harness/harness/features/FEAT-55-issue-types-created-work/BRIEF.md
- .harness/harness/features/FEAT-55-issue-types-created-work/runs/2026-09-05-27-validator/digest.md
- .harness/notes/analysis-fable-advisor-consult-FEAT-55-c4.md

## Done when

Scope: the operator's fourth batched signature pass over FEAT-55's revised plan package
Authority: approval:.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness/features/FEAT-55-issue-types-created-work/BRIEF.md#Approval
