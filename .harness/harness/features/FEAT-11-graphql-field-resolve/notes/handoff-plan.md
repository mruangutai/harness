# Handoff — FEAT-11-graphql-field-resolve, plan → build — written at 835b297, seq-3

## Next

Nothing dispatches until the operator signs BOTH `BRIEF.md ## Approval` and `plan.yaml
approval.status`. On signature: `gh-sync.py open`, then dispatch T-01 to `harness-eng-lead`
(routes to `harness-backend-dev`), then the qa segment against `harness.json` `gates.qa_gate`.
T-01 is the only task; it carries its own `verify:` block, which is long and self-checking.

## Trust

- All three sha256 pins in T-01's MF-1 clause match the files on disk — recomputed by me, not
  relayed — `plan.yaml:77-79` vs `.claude/skills/harness/bin/test-factory-{decompose,claim,land}.py`
  — verified-at 835b297
- T-01's `verify:` block is syntactically valid bash — `bash -n` on the extracted scalar —
  verified-at 835b297
- `plan.yaml` round-trips through `yaml.safe_load`; 1 task, 4 decisions, approval `pending` —
  verified-at 835b297
- The grilling artifact's claim that `_validate_stations` and the `Redy` case depend on
  `factory_gh.py:251-262` is FALSE — `factory_decompose.py:255-268` propagates without reading the
  text; `test-factory-decompose.py:1025-1048` runs against a `Recorder` and never enters
  `factory_gh` — verified-at 835b297. The operator's constraint stands anyway; only the reason was
  wrong. Full ruling in `feature.yaml` `e1_ruling`.
- The real dependency is `project_field_options` RAISING at `factory_gh.py:206-210`, a third error
  path the grilling never named; the plan already covers it — `plan.yaml:201` — verified-at 835b297
- SC-01 cannot be met by any agent: it writes to board 6. It is operator-run by construction and
  will read `not_met` at end of build — `BRIEF.md` SC-01 — verified-at 835b297
- The frozen `next_step` strings were asserted NOWHERE before this plan — `grep "does not offer it"
  .claude/skills/harness/bin/test-*.py` returns zero files — verified-at 835b297

## Dead ends

- Do NOT re-run the plan-contract validator for prose — the four falsified sites were re-verified
  by flattened-whitespace grep at my tier — `runs/plan-fix-product/digest.md` — verified-at 835b297
- Do NOT pin T-01's sentinel guard to a commit sha; a hardcoded sha rots as the tree moves and
  reddens with correct delivery behind it — validator MF-1 + my P-13 — verified-at 835b297
- Do NOT add a guard against aliased-repetition query shapes — qa measured cost flat at 1 point
  through N=300 — `notes/review-harness-qa-plan-contract.md` — verified-at 835b297
- Do NOT reopen the grilling artifact's `## Settled`: org boards, `project_items`, `item-edit`,
  no caching, no `field-list` fallback — operator's decisions — source: mission brief

## Working set

- `.harness/features/FEAT-11-graphql-field-resolve/BRIEF.md` (5 REQs, 12 SCs)
- `.harness/features/FEAT-11-graphql-field-resolve/plan.yaml` (T-01, D-01..D-04)
- `.harness/features/FEAT-11-graphql-field-resolve/DESIGN.md` (the error-message contract)
- `.harness/features/FEAT-11-graphql-field-resolve/feature.yaml` (budgets, `e1_ruling`, collision)
- `.harness/features/FEAT-11-graphql-field-resolve/runs/plan-contract-validator/digest.md`
