# Handoff — BUG-285-yaml-loader-pin, plan → build — written at bb48814, seq-11

## Next

Nothing dispatches. The approval state must be resolved by the operator first: plan.yaml reads
`approved` (2026-09-09) over a task set amended five times since, BRIEF.md reads `pending`, and no
verb writes `approved` -> `pending`. On a fresh signature over the AMENDED plan, run the eng
segment: `plan-merge.py set-feature-station --station building`, then dispatch the `build` team to
`harness-eng-lead` — T-02 first (`execution_agent: harness-backend-dev`), then T-03 which
`depends_on: [T-02]`, with T-01 independent. Carry each task's `intent:` verbatim from plan.yaml.

## Trust

- plan.yaml holds T-01/T-02/T-03 and `panel.cycle: 2` with six findings (2 info open, 2 low open,
  1 high resolved by T-02 under both reporters' ids) — loaded and read back through harness_yaml —
  verified-at bb48814
- `UnicodeDecodeError` is a `ValueError` but NOT a `json.JSONDecodeError`, so the cycle-1 catch set
  genuinely missed it — probed all three `issubclass` relations myself — verified-at bb48814
- `factory_decompose.py`: comment `:116-119`, `try:` `:120`, `harness_yaml.load_file(path)` `:121`,
  `except` `:122`, `factory_cli.refuse` `:123` — read with line numbers at source — verified-at
  bb48814
- 79 `feature.json` files parse identically under both loaders, so T-02 changes no current
  behaviour and closes a latent divergence — ran both parsers over all of them — verified-at bb48814
- `check-plan-routes.py` in THIS worktree: all three tasks OK, exit 1 solely on the DEVIATION line
  (this worktree's team-config.yaml is behind main's) — ran it myself; the product lead reported
  "0 violations, exit 0" and that did NOT reproduce here — verified-at bb48814
- T-01's, T-02's and T-03's `intent:`/`verify:` blocks survived every amend and the panel write —
  per-field shas recorded in `runs/2026-09-11-03-panelrecordc2-product/digest.md` — UNVERIFIED by
  me; I confirmed the blocks load and are non-empty, not their shas

## Dead ends

- No verb writes `lanes:` — `apply` exits 7 CONFLICT on the top-level key, `amend --key lanes`
  exits 2 naming tasks/decisions; I probed both against a copy. D-05 records it; routing authority
  is each task's own `execution_agent` — verified-at bb48814
- No verb writes `approval:` downward. Do not send another squad to try — three separate returns
  already burned effort on it — `runs/2026-09-11-01-amend-product/digest.md` — verified-at bb48814
- Do not fold in the gh-sync.py:516-524 non-UTF-8 defect the panel found. Out of the operator's
  scope; it is a backlog candidate — `runs/2026-09-11-02-planpanelc2-validator/digest.md` —
  verified-at bb48814

## Working set

- .harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml
- .harness/harness/features/BUG-285-yaml-loader-pin/BRIEF.md
- .harness/harness/features/BUG-285-yaml-loader-pin/runs/2026-09-11-02-planpanelc2-validator/digest.md
- .claude/skills/harness/bin/factory_decompose.py
- tests/integration/test-gh-sync.py

## Done when

Scope: the amended three-task plan is signed and T-02/T-03 built with their probes landed
Authority: approval:.harness/harness/features/BUG-285-yaml-loader-pin/BRIEF.md#Approval
Authority: plan-task:T-02.verify
Authority: plan-task:T-03.verify
Authority: brief-sc:SC-11
