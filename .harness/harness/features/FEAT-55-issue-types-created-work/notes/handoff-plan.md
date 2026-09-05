# Handoff — FEAT-55, plan → signature (round 3) — written at 407af0ba, seq-6

## Next

Take the operator's THIRD batched signature pass. Pass two's rulings are applied in one consolidated
revision (c5); the panel re-ran at cycle 3 and FAILed. `PF-df3caaeb7d520653866034e477d3718b` (F1,
`awaiting_user`) gates it: it proves the operator's OWN ruled fix inert. Twelve findings ride this
pass, each carrying a `fable-advisor` recommendation by operator instruction. Collect every ruling
into ONE `notes/answers-<runid>.md`, then dispatch exactly one consolidated revision. Cited:
plan.yaml `panel:`, STATE `## Open Questions` Q1–Q9.

## Trust

- Both c5 rulings are in the plan: T-03 case F asserts ZERO `updateIssue`, its verify loop carries
  `partial` and `github.issue_types`, T-10 §6 runs on an explicit TARGET, BRIEF SC-10 matches —
  plan.yaml, BRIEF.md — verified-at 407af0ba
- Neither approval fragment moved — plan.yaml `approval`, BRIEF.md `## Approval` — verified-at
  407af0ba
- `panel:` holds TWELVE findings — six carried verbatim with every id reproducing, six new —
  `notes/research-FEAT-55-panel-transcription-c3.md` — verified-at 407af0ba
- Both readers RAN at cycle 3, none skipped — `runs/2026-09-04-19-validator/digest.md` —
  verified-at 407af0ba
- F1's premise HOLDS: three `partial` cases, all fresh, backfill set empty by construction —
  `.harness/notes/analysis-fable-advisor-consult-FEAT-55-c3.md` — verified-at 407af0ba
- Intent delivered, eleven baseline findings closed, 0 route violations —
  `notes/research-FEAT-55-goalcheck-plan-c4.md` — verified-at 407af0ba
- Anchors inside `panel:` findings past plan.yaml`:159` are stale by +77; re-measured table —
  `.harness/notes/analysis-fable-advisor-consult-FEAT-55-c3-tail.md` — verified-at 407af0ba
- `github.issue_types` is absent from `.harness/harness.json`, so D-12's "EXISTING key" is
  inaccurate and N4 has no installed base — lead-verified at `:357` — UNVERIFIED by me

## Dead ends

- No pre-signature fix dispatch for any panel finding, gating or not — `skill://harness` plan phase,
  DEC-176 — verified-at 407af0ba
- Do not dispatch F1's remedy as a fix cycle: neither pm nor the orchestrator may discharge a `high`
  finding's risk — plan.yaml `panel:` F1 `disposition` — verified-at 407af0ba
- Do not pin `review_sha`: cycle 3 graded a specification, `code_grade: n_a` — feature.json `runs` —
  verified-at 407af0ba
- Do not re-run goal-check or panel before a revision — plan.yaml `panel.cycle` — verified-at
  407af0ba
- `apply` cannot revise an existing task or decision: add-only, exits 7. `amend` is the verb —
  `plan-merge.py --help` — verified-at 407af0ba
- Do not mirror to GitHub: this plan is unsigned — `references/github-mirror.md` — verified-at
  407af0ba

## Working set

- .harness/harness/features/FEAT-55-issue-types-created-work/plan.yaml
- .harness/harness/features/FEAT-55-issue-types-created-work/BRIEF.md
- .harness/harness/features/FEAT-55-issue-types-created-work/runs/2026-09-04-19-validator/digest.md
- .harness/notes/analysis-fable-advisor-consult-FEAT-55-c3.md
- .harness/notes/analysis-fable-advisor-consult-FEAT-55-c3-tail.md

## Done when

Scope: the operator's third batched signature pass over FEAT-55's revised plan package
Authority: approval:.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness/features/FEAT-55-issue-types-created-work/BRIEF.md#Approval
