# Handoff — FEAT-08-remove-cost-tracking, plan → build — written at ae2443d, seq-1

## Next

STOP. Do not dispatch anything until BOTH `BRIEF.md` and `PLAN.md` carry
`status: approved` in their `## Approval` sections — both read `pending` today, and an
unapproved artifact is a step-0 BLOCKED for a build mission. Once signed, the first
action is PLAN segment S1 = **T-01 (`validate-digest.py`) and T-02 (`check-state.sh`)**,
executed **main-session DIRECT under the DEC-174 carve-out** — never dispatched through
a team run, because those two files are the gates being changed. Order is load-bearing:
S1 loosens the gates before S2 (T-03, T-04) removes the machinery.

## Trust

- `cost_usd` is REQUIRED in `SCHEMAS["orchestrator"]` and unknown DIGEST keys are IGNORED — I probed both against the live validator (omit → exit 1 `missing 'cost_usd'`; extra key → `digest ok` exit 0) — verified-at ae2443d
- The supersession marker is GENERATED from the superseding decision's TITLE or a body line starting `**Supersedes DEC-NN` — `gen-decisions-index.py:24, :232-237, :284, :324-326`; pm's proposed DEC-178 title returns `None`, DEC-83 control returns `DEC-82` — verified-at ae2443d
- All 67 run `state.yaml` files carry a `cost:` block, so `cost` must STAY in `CHECKPOINT_KEYS` (`check-state.sh:344`) — allowed, never required — verified-at ae2443d
- `check-state.sh:258-259` hard-fails when `harness.json` has no `cost_model.rates`; stripping the config before loosening the checker makes the repo an instant violation — pm's finding, `PLAN.md` D-02 — verified-at ae2443d
- Gates green: `run-unit-tests.sh` 0, `check-docs.sh` 0, `check-state.sh` zero violations, `gen-decisions-index.py --stdout | diff -` 0 — verified-at ae2443d
- The validate panel is FOUR-WIDE by user ruling — `feature.yaml` `validate_panel` — verified-at ae2443d

## Dead ends

- Do NOT edit `render-brief.py` — its single `cost` hit at `:11` is a prose comment, not a budget renderer; the grilling artifact implies otherwise and is wrong — verified-at ae2443d
- Do NOT edit `test-harness-yaml.py`, `test-harness-yaml-corpus.py`, `test-check-domain.py` — their `cost:` hits are duplicate-key YAML fixtures — verified-at ae2443d
- Do NOT delete `context_per_turn_tokens` from either `harness.json` — the key exists in neither; `cost-report.py:338` hardcodes 200k — verified-at ae2443d
- Do NOT pre-emptively skip a review-panel step, and do NOT re-open the four `## Settled` rulings or the DEC-83 double-heading off-by-one — `feature.yaml` `validate_panel` / `pending` — source: user rulings

## Working set

- `.harness/features/FEAT-08-remove-cost-tracking/PLAN.md` (12 tasks, 9 decisions, 4 segments)
- `.harness/features/FEAT-08-remove-cost-tracking/BRIEF.md` (15 SCs; SC-12 is the over-removal guard)
- `.harness/features/FEAT-08-remove-cost-tracking/feature.yaml`
- `.harness/notes/grilling-remove-cost-2026-08-05.md`
- `.harness/features/FEAT-08-remove-cost-tracking/runs/plan-product/digest.md`
