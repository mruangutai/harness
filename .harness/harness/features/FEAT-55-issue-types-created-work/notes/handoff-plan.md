# Handoff — FEAT-55, plan → signature (round 5) — written at b0aa961a, seq-8

## Next

Sign the plan. The fourth ruling batch is fully discharged: five FIX rulings in ONE revision (c8),
four ACCEPT rulings honoured by touching nothing but their disposition strings, and the cycle-5
panel returned PASS, `severity_max: med`, `must_fix: []`, both readers running. **Nothing gates the
signature.** Five findings ride it unruled — four new `low` plus one carried `med` — so
`plan-merge.py sign-approval` may run now, accepting each via `--overrule PF-ID:<reason>`. Cited:
plan.yaml `panel:`, STATE `## Open Questions` Q1–Q6. A fifth ruling batch instead buys ONE revision
and no re-panel: one cycle of ten remains, and more is an operator decision on `max_total_cycles`.

## Trust

- All five FIX rulings HOLD at source, each re-verified by quoted content string —
  `runs/2026-09-05-02-validator/digest.md` `roll_call` — verified-at b0aa961a
- The backfill-only refusal case is non-inert and route-own on all THREE routes — plan.yaml T-03
  `CASE K` / T-05 `CASE H` / T-07 `CASE J`, each letter in its own verify loop — verified-at b0aa961a
- The pinned read-back row was SPLIT to 394 chars and its guard is durable in the standing unit
  suite — plan.yaml D-08, T-01 `tests/unit/test-issue-types-pin.py`, T-11 §3, T-12 §1 — verified-at
  b0aa961a
- The four `operator_accepted` surfaces are UNCHANGED, and both approval fragments still read
  `pending` — plan.yaml `panel:` and `approval:`, BRIEF.md `## Approval` — verified-at b0aa961a
- Intent delivered, verbatim YES, 0 route violations, SC-10 `partial` —
  `notes/research-FEAT-55-goalcheck-plan-c7.md` — verified-at b0aa961a
- Nine findings, every id computed by `panel_findings.py id`, five carried ids reproducing —
  `notes/research-FEAT-55-panel-transcription-c5.md` — verified-at b0aa961a
- INV-32 was NOT observed passing: it skips an unapproved plan, so its predicates were applied to
  the stored block by hand with a positive control — same note — UNVERIFIED

## Dead ends

- No pre-signature fix dispatch for any finding, gating or not, and no re-run of the goal-check or
  the panel before a revision — DEC-176, plan.yaml `panel.cycle: 5` — verified-at b0aa961a
- Do not pin `review_sha`: cycle 5 graded a specification, `code_grade: n_a` — feature.json `runs`
  — verified-at b0aa961a
- Do not trust any line anchor: c8 rewrote two decisions and eight task bodies, the transcription
  rewrote `panel:` wholesale, the file is 1665 lines — `notes/research-FEAT-55-planrepair-c8.md` —
  verified-at b0aa961a
- Do not re-raise the four `operator_accepted` findings on their merits — the operator ruled them,
  `notes/answers-plan-panel-20260905-c4.md` — verified-at b0aa961a
- `apply` is add-only (exit 7) and `amend --key` takes only `tasks|decisions`, so a `panel:` edit
  needs the panel setter — `plan-merge.py --help` — verified-at b0aa961a
- Do not mirror to GitHub: this plan is unsigned — `references/github-mirror.md` — verified-at
  b0aa961a
- BUILD: land T-11 then T-12 BEFORE the qa segment — the pin guard is deliberately red until they
  do, `run-unit-tests.sh` globs it, `gates.qa_gate` is blocking, and DEC-174 leaves its `loop_back`
  no legal owner — plan.yaml `panel.sequencing_note` — verified-at b0aa961a

## Working set

- .harness/harness/features/FEAT-55-issue-types-created-work/plan.yaml
- .harness/harness/features/FEAT-55-issue-types-created-work/notes/answers-plan-panel-20260905-c4.md
- .harness/harness/features/FEAT-55-issue-types-created-work/notes/research-FEAT-55-planrepair-c8.md
- .harness/harness/features/FEAT-55-issue-types-created-work/runs/2026-09-05-02-validator/digest.md

## Done when

Scope: the operator's signature on FEAT-55's cycle-5 plan package, or one final ruling batch
Authority: approval:.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness/features/FEAT-55-issue-types-created-work/BRIEF.md#Approval
