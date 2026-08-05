# Grilling — remove cost tracking entirely (issue #58) — 2026-08-05

## Destination

The harness no longer meters, budgets, gates on, or reports money. `cost-report.py` and its test are
gone, INV-11 is gone, the `cost_model` block and the two USD budgets are out of `harness.json` and
its template, and no rule surface asks an agent to produce or carry a cost figure. `max_total_cycles`
— the only budget with teeth — is untouched. After this, nothing in the harness can answer "what did
this feature cost", and nothing else answers it either.

## Settled

- **DEC-148's context watchdog → DROPPED with the file.** Not preserved as a standalone script and
  not folded into `check-state.sh`. The new decision must record the drop and its reason so a future
  scan does not re-suggest it.
- **Historical `cost_usd` / `max_cost_usd` in shipped `feature.yaml` → LEFT IN PLACE** as the only
  surviving record of what features cost. `check-state.sh` must stop *requiring* them; nothing erases
  what is written.
- **`cost` stays in `check-state.sh`'s `CHECKPOINT_KEYS` — allowed, never required.** This is forced
  by the ruling above, not a separate preference: see the measurement in `## Facts`.
- **Route → plan and build it as a feature**, same shape as FEAT-07. Full BRIEF/PLAN/signature, the
  gates, and a goal-check. Not direct edits.
- **`max_total_cycles`, `cycles_used` and cycle counting are OUT OF SCOPE and untouched.**

## Not yet specified

- Whether anything replaces the ship briefing's actual-vs-budget line, or the briefing simply stops
  having one. `render-brief.py` carries a single `cost` reference, so the mechanical change is
  trivial; what a reader should see instead — if anything — is not sharp enough to state.
- Whether removing the two USD budgets leaves `warn_at_fraction` (`harness.json:236`) orphaned. It
  is a fraction *of* a budget; with both USD budgets gone it may have no referent, or it may still
  apply to `max_total_cycles`. Nobody has checked which.

## Out of scope

- Cycle counting and `max_total_cycles` — the hard budget, DEC-157, untouched and explicitly kept.
- Perf-review row 10 (count and budget RUNS, not just cycles). Still unfiled. Recorded here because
  after this feature it becomes the *only* remaining lever for noticing a feature going long, and
  dismissing that silently would be worse than naming it.
- Rewriting historical DECISIONS entries. DEC-99, DEC-114, DEC-134, DEC-148, DEC-157 and DEC-163 all
  carry `cost` or `budget` tags and are HISTORY; the new entry records the removal, it does not edit
  the past.

## Facts I verified (so pm does not re-derive them)

All at `ae2443d`.

- **The sweep is 18 files**, unchanged since the ticket was filed:
  `grep -rln -e cost_usd -e cost-report -e max_cost -e per_feature_usd -e INV-11` over `.claude/`,
  `docs/`, `harness.json` and `team-config.yaml`.
- **`cost-report.py` is 439 lines; `test-cost-report.py` is 94.** `run-unit-tests.sh:6` lists the
  test in `SCRIPTS`, and the script has a drift detector that fails when a `test-*.py` exists outside
  that list — so **both must be deleted together**, or the runner breaks.
- **INV-11 sites in `check-state.sh`:** the rule at `:369-373` ("run is complete but has no cost:
  block"), plus aborting references at `:248`, `:302`, `:357`, `:361`.
- **THE MEASUREMENT THAT FORCES THE WHITELIST DECISION: all 67 run `state.yaml` files on disk carry a
  `cost:` block — 67 of 67.** `check-state.sh:401` reports any top-level key not in `CHECKPOINT_KEYS`
  (`:340-350`, where `cost` sits at `:344`). Removing `cost` from that set would turn **every
  historical run into a violation**. It stays.
- **DEC-148 made TWO changes and only one is being deleted.** Its watchdog
  (`cost-report.py:338-346`) flags an agent whose average cache-read/turn exceeds
  `budgets.context_per_turn_tokens`. **That key does not exist in `harness.json`** — `grep` over the
  file returns nothing, and the script hardcodes a 200k default (`:338`). Its second half, the
  playbook relay rule ("the orchestrator ends its run at mission-phase boundaries"), was **superseded
  by DEC-159**, which makes one-phase-per-orchestrator mandatory regardless of any measurement. So
  the watchdog is a diagnostic whose behavioural consequence is now hard-coded elsewhere.
- **`harness.json` `budgets` (`:233-240`) holds** `per_feature_usd`, `per_run_usd`,
  `warn_at_fraction`, `max_total_cycles` and two `_rationale` strings. The template's
  `per_feature_usd` is 50.0 where this repo's is 120.
- **`cost_usd` is in exactly one digest schema** — `validate-digest.py:177`, the `orchestrator`
  entry, typed `str`. It is also named in a comment at `:171` and in the `F12` note at `:661`.
  **`lead` has no cost field.**
- **`render-brief.py` contains a single `cost` reference.** The `cost` hits in
  `templates/BRIEF.md`, `templates/PLAN.md` and `templates/codebase-INDEX.md` are prose about
  tradeoffs and context expense, not the budget line — do not edit those.
- **`check-state.sh` and `validate-digest.py` are inside the DEC-174 carve-out**, so their edits are
  direct, tests run explicitly, a human reading the diff. `cost-report.py`, `test-cost-report.py`,
  `run-unit-tests.sh` and `harness.json` are granted to `harness-backend-dev`
  (`team-config.yaml:155`) and `harness-dev-ops` (`:197`); `docs/**` to `harness-documentor`
  (`:116`). `.claude/skills/harness/SKILL.md`, `.claude/skills/harness-team/SKILL.md`,
  `.claude/agents/*.md` and `teams/*.yaml` are granted to nobody — declared main-session steps.
- **Gates green at `ae2443d`:** `run-unit-tests.sh` exit 0, `check-docs.sh` exit 0,
  `check-state.sh` zero violations.
- **The strongest evidence for the removal is FEAT-07 itself:** it finished at $702.82 against a
  $550 budget produced by the orchestrator's own arithmetic, and the meter could not see the eight
  of ten tasks that ran at depth 0 in the main session. FEAT-06 records the same understatement in
  its own `cost_note` for 9 of 10 tasks.
