# Handoff — FEAT-29-graphql-budget, build → validate — written at e7104ca, seq-4

## Next

The build phase is closed; do not dispatch a squad. The operator executes **T-07 then T-09** per
`notes/layer0-batch-b-FEAT-29.md`. When `measurement-after.md` and `measurement-board6.md` exist and
both `verify:` blocks exit 0, delegate **pm's goal-check through `harness-product-lead`** over all ten
SCs, then dispatch **ship-refresh and distillation as TWO dispatches in ONE message** (never combined
— distillation must be cold), then write the final CEO briefing.

## Trust

- `matrix_ok: true`; panel PASS with `must_fix` empty, `severity_max: low` —
  `runs/2026-08-19-09-validator/digest.md` — verified-at c472a02
- Suites green: unit exit 0 / 175 `^PASS ` lines / 18 scripts / 0 FAIL, integration exit 0 / 12 of 12
  / 0 FAIL — re-run by me — verified-at e7104ca
- SIMPLIFY applied nothing; `git diff 8c7d7bc -- .claude/skills/harness/bin/` is empty, so the code
  T-07 measures is final — verified-at e7104ca
- `review_sha` = `e7104ca` = branch tip — `git rev-parse` — verified-at e7104ca. **Re-pin after every
  commit**; it was stale on FEAT-25 and FEAT-27
- Board stations: T-01/02/03/04/07/09 `Backlog`, T-05/06/08 `Done`, parent `Building` — live read —
  verified-at bee6234, and no mirror subcommand has run since
- The cheap read returns 486 items for 5 GraphQL points against 506 for the run containing the old
  path — live call — verified-at bee6234
- SC-08 and SC-09 are `not-assessed` because both sit on `NOBODY` paths — `check-domain.sh --resolve`
  — verified-at 3fbfd0a. They are pre-ship steps for the operator, not gaps

## Dead ends

- Do NOT run `gh-sync start-task` or `close-task` for any task until T-07's after-measurement lands —
  seven control lines quote cards reading `Backlog` — `notes/layer0-batch-b-FEAT-29.md` — verified-at e7104ca
- Do NOT re-dispatch over a run whose `state.yaml` lacks `completed_at`, and do NOT assert a negative
  ("X left no receipt") in a brief — both caused duplicated work here —
  `observations/harness-orchestrator.md` — verified-at e7104ca
- Do not edit `check-state.sh`, `test-check-state.py`, `CLAUDE.md`, `.harness/notes/**`,
  `.harness/logs/**` — carve-out or `NOBODY` — verified-at 3fbfd0a
- Do not re-open the matrix integration question or SC-05's OFF clause — both ruled, and the second
  rested on a false premise refuted at `test-gh-cost-log.py:251-259` — verified-at c472a02

## Working set

- `.harness/harness/features/FEAT-29-graphql-budget/notes/layer0-batch-b-FEAT-29.md`
- `.harness/harness/features/FEAT-29-graphql-budget/runs/2026-08-19-09-validator/digest.md`
- `.harness/harness/features/FEAT-29-graphql-budget/runs/2026-08-19-10-eng/digest.md`
- `.harness/harness/features/FEAT-29-graphql-budget/feature.json`
- `.harness/harness/features/FEAT-29-graphql-budget/BRIEF.md`
