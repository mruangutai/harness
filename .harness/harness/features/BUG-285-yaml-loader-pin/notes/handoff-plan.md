# Handoff — BUG-285-yaml-loader-pin, plan → build — written at 66be772, seq-13

## Next

Nothing dispatches. The operator must resolve the approval state first: plan.yaml reads `approved`
(2026-09-09) over a task set amended since, BRIEF.md reads `pending`, and no verb writes
`approved` -> `pending`. On a fresh signature over the AMENDED plan, run the eng segment:
`plan-merge.py set-feature-station --station building`, then dispatch the `build` team to
`harness-eng-lead` — T-02 first (`execution_agent: harness-backend-dev`), then T-03 which
`depends_on: [T-02]`; T-01 is independent. Carry each `intent:` verbatim from plan.yaml.

## Trust

- plan.yaml holds T-01/T-02/T-03 and `panel.cycle: 2` with three readers (should-not-exist, scope,
  goalcheck) and six findings, 4 open and 2 resolved by T-02 — loaded and read back through
  harness_yaml — verified-at 66be772
- `UnicodeDecodeError` is a `ValueError` but NOT a `json.JSONDecodeError`, which is why cycle 1's
  catch set was gating — probed all three `issubclass` relations myself — verified-at 66be772
- `factory_decompose.py`: comment `:116-119`, `try:` `:120`, `load_file` `:121`, `except` `:122`,
  `refuse` `:123`; early `os.path.exists` return `:114-115` — read at source — verified-at 66be772
- 79 `feature.json` files parse identically under both loaders, so T-02 changes no current
  behaviour and closes a latent divergence — ran both parsers over all of them — verified-at 66be772
- check-plan-routes.py is cwd-dependent: exit 1 (DEVIATION) inside the worktree, exit 0 from the
  main checkout, same plan; all three tasks route OK either way — ran both — verified-at 66be772
- the six 2026-09-11 lead digests are clean under MAIN's validate-digest.py and fail only under
  this branch's older copy (requires `sc_status`); the cycle-0 panel digest is the mirror case,
  failing main's enum for `severity_max: info` — ran main's validator over the runs tree — verified-at 66be772
- T-01/T-02/T-03 `intent:`/`verify:` per-field shas as recorded in
  `runs/2026-09-11-03-panelrecordc2-product/digest.md` — UNVERIFIED by me; I confirmed the blocks
  load and are non-empty, not their shas

## Dead ends

- No verb writes `lanes:` — `apply` exits 7 CONFLICT, `amend --key lanes` exits 2; I probed both
  against a copy. D-05 records it; routing authority is each task's `execution_agent` —
  verified-at 66be772
- No verb writes `approval:` downward. Do not send another squad at it — four returns already
  burned effort there — `runs/2026-09-11-01-amend-product/digest.md` — verified-at 66be772
- Do not "fix" the digest-contract violations by adding `sc_status` — it satisfies this branch's
  copy and no single value satisfies both contracts; the merge resolves it —
  `runs/2026-09-11-02-planpanelc2-validator/digest.md` — verified-at 66be772
- Do not fold in the gh-sync.py:516-524 non-UTF-8 defect the panel found. Out of the operator's
  scope; backlog candidate — `runs/2026-09-11-02-planpanelc2-validator/digest.md` —
  verified-at 66be772

## Working set

- .harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml
- .harness/harness/features/BUG-285-yaml-loader-pin/BRIEF.md
- .harness/harness/features/BUG-285-yaml-loader-pin/notes/research-BUG-285-goalcheck-plan-c3.md
- .harness/harness/features/BUG-285-yaml-loader-pin/runs/2026-09-11-02-planpanelc2-validator/digest.md
- .claude/skills/harness/bin/factory_decompose.py

## Done when

Scope: the amended three-task plan is signed and T-02/T-03 built with their probes landed
Authority: approval:.harness/harness/features/BUG-285-yaml-loader-pin/BRIEF.md#Approval
Authority: plan-task:T-02.verify
Authority: plan-task:T-03.verify
Authority: brief-sc:SC-11
