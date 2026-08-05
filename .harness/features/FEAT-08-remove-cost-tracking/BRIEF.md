# BRIEF — FEAT-08 Remove cost tracking

## Problem

The harness maintains a money meter that cannot measure the work and feeds a budget that cannot stop
anything.

**It cannot see the majority of the work.** `cost-report.py` attributes spend from transcript
snapshots and cannot separate a task run at depth 0 in the main session from the session total.
FEAT-06 ran 9 of 10 build tasks that way and records its own figure as an understatement; FEAT-07 has
8 of 10 in the same shape and finished at $702.82 against a $550 budget the orchestrator computed
itself. Every `feature.yaml` `cost_note` in this repo says the number is approximate; FEAT-05's is
additionally labelled a stale floor.

**The budget it feeds has no teeth by design.** DEC-134 made `max_cost_usd` informational after a $9
overrun killed a flow one $5 step from done — a crossing is flagged in a headline and never blocks.
`max_total_cycles` is the only budget with teeth (DEC-157) and is unaffected by cost.

**Keeping it is not free.** 439 lines of `cost-report.py` plus 94 lines of test, a `cost_model` block
in both configs carrying a dated per-model rate table that must be re-verified against published
pricing whenever rates change and that REFUSES to price a run it does not cover, and a
`(model, speed, inference_geo)` keying scheme whose own note warns that ignoring `speed` is a silent
halving (`.harness/harness.json:194`). `check-state.sh` warns when the table is more than 90 days
stale (`:261-271`) — a standing maintenance obligation for a number nobody is allowed to act on.

The instrumentation touches **18 files** today
(`grep -rln -e cost_usd -e cost-report -e max_cost -e per_feature_usd -e INV-11` over `.claude/`,
`docs/` and both configs, re-run at `ae2443d`). That the sweep grep returns 18 and not 0 is what makes
SC-01 discriminating.

## Goal

The harness stops metering, budgeting, gating on, and reporting money, and nothing replaces it. The
meter, its test, the `cost_model` block, the two USD budgets, INV-11, the digest-schema field and
every rule-surface instruction that asks an agent to carry a cost figure all go. Cycle counting —
the one budget with teeth — is untouched. The historical figures already written into shipped
`feature.yaml` and run `state.yaml` files stay exactly as they are, as the only surviving record of
what features cost. After this, the harness cannot answer "what did this feature cost", and nothing
else answers it either.

## Requirements

- REQ-01: The harness does not meter money. No script in the repo computes a dollar figure for a run,
  a feature, or an agent.
- REQ-02: The harness does not budget or gate on money. No configuration key bounds spend, and no
  invariant fails a run for a missing, stale, or excessive cost figure.
- REQ-03: No rule surface asks an agent to produce, carry, or report a cost figure. An agent that
  reads its own rules end to end finds no instruction that would make it emit one.
- REQ-04: The return contract neither requires nor rejects a cost field. A return written to the new
  contract validates, and a return still carrying the old field also validates, so no in-flight run
  is broken by the transition.
- REQ-05: The rework budget is unaffected. `cycles_used`/`max_total_cycles` still bound fix loops and
  exhaustion still blocks.
- REQ-06: Every cost figure already recorded in a shipped `feature.yaml`, and every `cost:` block in a
  historical run `state.yaml`, survives unchanged — and the repo remains free of state violations
  because of them.
- REQ-07: The written record explains why metering was removed and records that DEC-148's context
  watchdog was knowingly dropped with the file, with its reason, so a future scan does not re-propose
  it.
- REQ-08: No surviving document, index row, or rule surface advertises a script, configuration key, or
  invariant that this change deleted.
- REQ-09: The removal leaves no orphaned configuration: a key whose only consumer is deleted does not
  remain in either config.
- REQ-10: Prose about **context expense, token budgets and cycle budgets** — which the same greps
  match — survives untouched. Over-removal is the dominant failure mode of a sweep like this.

## Success Criteria

- SC-01: `grep -rln -e cost_usd -e cost-report -e max_cost -e per_feature_usd -e INV-11` over
  `.claude/`, `docs/`, `.harness/harness.json`, `.harness/team-config.yaml` and `.harness/README.md`
  returns **only** `docs/harness/DECISIONS.md` and `docs/harness/DECISIONS-INDEX.md` (which keep the
  historical entries and rows by REQ-06/constraint 3). **Discriminating:** the same command returns
  18 files at `ae2443d`, so this is not an already-empty absence-grep.
  verify: automated        evidence: command
- SC-02: `.claude/skills/harness/bin/cost-report.py` and `.claude/skills/harness/bin/test-cost-report.py`
  do not exist, and `.claude/skills/harness/bin/run-unit-tests.sh` exits 0 — which also proves its
  drift detector (`:9-24`, exits 2 on an unlisted `test-*.py`) is satisfied rather than merely
  bypassed.
  verify: automated        evidence: unit
- SC-03: `.claude/skills/harness/bin/check-state.sh` reports **zero violations** against the repo as
  it stands, with all 67 historical run `state.yaml` files and all 7 `feature.yaml` files in place.
  This single command proves three things at once: INV-11 no longer fails a complete run that has no
  meter to run, `cost` is still in `CHECKPOINT_KEYS` so 67 historical `cost:` blocks are not 67 new
  unknown-key violations, and the `cost_model.rates` check no longer fails a config that has no
  `cost_model`.
  verify: automated        evidence: command
- SC-04: An `orchestrator` DIGEST that **omits** `cost_usd` is accepted by
  `.claude/skills/harness/bin/validate-digest.py` (exit 0, `digest ok`), and one that **still carries**
  `cost_usd` is also accepted. **Discriminating on both halves:** at `ae2443d` the omitting payload is
  rejected `BLOCKED (contract violation) — missing 'cost_usd'` at exit 1, and the carrying payload is
  accepted; after the change the first must flip and the second must not.
  verify: automated        evidence: unit
- SC-05: `budgets.max_total_cycles` and `_max_total_cycles_rationale` are present and unchanged in
  BOTH `.harness/harness.json` and `.claude/skills/harness/templates/harness.json`, and
  `git diff` shows no change to any line of `check-state.sh` or `SKILL.md` that mentions
  `cycles_used`, `max_cycles` or `max_total_cycles`.
  verify: automated        evidence: command
- SC-06: The historical record is byte-identical. `grep -h -e cost_usd -e max_cost_usd
  .harness/features/*/feature.yaml | wc -l` returns **89** (its value at `ae2443d`), and
  `grep -l '^cost:' .harness/features/*/runs/*/state.yaml | wc -l` returns **67 of 67**.
  verify: automated        evidence: command
- SC-07: No orphaned configuration. `cost_model`, `_cost_model_note`, `_modifier_note`,
  `_budgets_note`, `per_feature_usd`, `_per_feature_rationale`, `per_run_usd` and `warn_at_fraction`
  are absent from BOTH `.harness/harness.json` and `.claude/skills/harness/templates/harness.json`,
  and both files still parse as valid JSON. `warn_at_fraction` is included because its only consumer
  is `cost-report.py:406` (D-04).
  verify: automated        evidence: command
- SC-08: `docs/harness/DECISIONS-INDEX.md`'s DEC-148 row no longer asserts a live mechanism:
  `grep -n 'DEC-148' docs/harness/DECISIONS-INDEX.md` shows a row containing neither `cost-report.py`
  nor `context_per_turn_tokens`, and **`gen-decisions-index.py --stdout | diff -
  docs/harness/DECISIONS-INDEX.md` exits 0** — so the row survives regeneration rather than being a
  hand-edit the generator will overwrite. The row must also still make DEC-148's two halves
  distinguishable and name DEC-159 as the authority for the relay half.
  verify: automated        evidence: command
- SC-09: `docs/harness/DECISIONS.md` carries a new entry that (a) records the removal and its reason,
  (b) states explicitly that DEC-148's context watchdog is DROPPED with the file — not preserved as a
  standalone script and not folded into `check-state.sh` — with the reason, and (c) states that
  historical `cost_usd` figures are deliberately left in place. Its `DECISIONS-INDEX.md` row carries a
  real ruling, not the generator's `⚠ RULING PENDING` sentinel.
  verify: inspection
- SC-10: `.claude/skills/harness/bin/check-docs.sh` exits 0.
  verify: automated        evidence: command
- SC-11: `.claude/skills/harness/bin/run-unit-tests.sh` exits 0 with every listed script passing —
  run as a whole, not per-task. FEAT-07 reddened its build on a cap enforced by a unit test that no
  task's `verify:` invoked; every task here that touches `bin/`, either `harness.json`, either
  template, or `DECISIONS-INDEX.md` carries this clause in its own `verify:`.
  verify: automated        evidence: unit
- SC-12: **Over-removal guard.** The protected non-money prose survives verbatim:
  `.claude/skills/harness/SKILL.md:21` (a feature dir "costs ~100k tokens"), `:127` ("cost a working
  day"), `:229` ("Cost grows with the square of session length"), `:24`/`:69`/`:110` (the cycle
  budget), `.claude/skills/harness-team/SKILL.md:20`/`:108`/`:154`/`:160`/`:194`/`:265`, and the three
  YAML-fixture `cost:` hits in `test-harness-yaml.py`, `test-harness-yaml-corpus.py` and
  `test-check-domain.py`. A reviewer reads the diff of each file and confirms only the money lines
  moved.
  verify: inspection
- SC-13: `.harness/README.md` — CLAUDE.md's named layout authority for `.harness/` — describes the
  post-change harness: `grep -n -i -e cost -e 'cost budget' .harness/README.md` shows no `cost_model`
  in the `harness.json` column (`:17` today), no "cost" in the `feature.yaml` row (`:26`), no "cycle
  and cost budgets" for the orchestrator (`:46`), and no INV-11 description (`:86`).
  verify: automated        evidence: command
- SC-14: No surviving document advertises a command that no longer exists. Every remaining
  `cost-report.py` mention in `docs/harness/BUILD.md` and `docs/harness/SPEC.md` is either deleted or
  carries an inline "removed" marker naming the new decision; nothing in either file reads as a live
  instruction to run it. `grep -n 'cost-report' docs/harness/BUILD.md docs/harness/SPEC.md` — every
  hit is on a line containing the removal marker.
  verify: automated        evidence: command
- SC-15: A dispatched agent reading only its rules finds nothing that would make it emit a cost
  figure. Specifically, `.claude/agents/harness-orchestrator.md`,
  `.claude/skills/harness/SKILL.md`, `.claude/skills/harness-team/SKILL.md`,
  `.claude/skills/harness/teams/build.yaml` and `.claude/skills/harness/teams/review.yaml` contain no
  instruction to run a meter, no `cost:` / `cost_usd:` field in a return template, no `max_cost_usd`
  key, and no actual-vs-budget reporting requirement — and the ship-review briefing's step-2 list no
  longer names a cost line.
  verify: inspection

## Verification gaps — stated where the signature is taken (DEC-163)

Read from `test_kinds` in `.harness/harness.json` at `ae2443d`. **Exactly one kind has a runner:**
`unit` → `run-unit-tests.sh`, detecting `.claude/skills/harness/bin/test-*.py` among others. Every
other kind — `functional`, `integration`, `component`, `ui`, `eval`, `typecheck` — has `cmd: null` and
resolves to a soft skip.

- **No `test_kinds` runner's detect globs match `docs/**`, `.claude/skills/**/*.md`,
  `.claude/agents/*.md`, `.claude/skills/harness/teams/*.yaml`, `harness.json` or `.harness/README.md`.**
  Most of this feature's surface is therefore outside every runner. Rather than downgrade those
  criteria to `inspection` and lose their teeth, they carry `evidence: command`: a **named,
  deterministic shell command stated inside the criterion**, run and recorded by qa. `command` is
  deliberately **not** a `test_kinds` kind — naming one of the null kinds would be a gate that looks
  real and silently skips, and naming `unit` for a grep would be false. What this does not buy: these
  commands live in the SC text, not in a committed test, so nothing re-runs them after this feature
  ships. That is accepted; the surfaces they guard are deleted, not maintained.
- **SC-09, SC-12 and SC-15 are `inspection`** — whether a decision entry states its reason well
  enough that a future scan does not re-propose the watchdog, whether a diff removed only money
  lines, and whether a rule surface reads coherently without its budget section are judgments no grep
  makes. Their evidence is a reviewer's `file:line` finding.
- **No `uat` criterion.** Nothing here changes anything a user operates by hand.

## Constraints

- **`max_total_cycles`, `cycles_used` and cycle counting are OUT OF SCOPE and untouched** (DEC-157).
  This is the only budget with teeth and is explicitly kept.
- **Historical `cost_usd` / `max_cost_usd` in shipped `feature.yaml` are LEFT IN PLACE** as the only
  surviving record of what features cost. `check-state.sh` must stop *requiring* them; nothing erases
  what is written.
- **`cost` stays in `check-state.sh`'s `CHECKPOINT_KEYS`** — allowed, never required. Forced, not
  chosen: all 67 run `state.yaml` files on disk carry a `cost:` block (re-measured at `ae2443d`:
  67 of 67), and `check-state.sh:401` flags any top-level key not in that set, so removing it would
  turn every historical run into a violation.
- **No historical DECISIONS entry is rewritten.** DEC-99, DEC-114, DEC-134, DEC-148, DEC-157 and
  DEC-163 are history. The new entry records the removal; the past stays. The one permitted touch is
  the DEC-148 **index row's ruling prose**, which is a hand-written summary, not the entry.
- **DEC-174 carve-out.** `check-state.sh`, `validate-digest.py` and their tests are the harness's own
  enforcement layer: those edits are made **directly** — ordinary edits, tests run explicitly, a human
  reading the diff — never dispatched through a team run whose gates are the thing being changed.
- **Files-only; PyYAML is required (DEC-171 am.1).** No new dependency, no build step.
- **Out of scope, and named rather than silently dropped:** the perf review's row 10 (count and budget
  RUNS, not just cycles). After this feature it becomes the only remaining lever for noticing a
  feature going long, and it is still unfiled. It belongs in the backlog, not here.
- **Nothing replaces the ship briefing's cost line.** `render-brief.py` needs no edit: its single
  `cost` reference (`:11`) is a prose comment about why HTML is not hand-authored, not a budget
  renderer — re-read at `ae2443d`. The briefing simply stops having a cost line (D-06).

## Settled facts recorded here so nobody re-derives them

- **`context_per_turn_tokens` is a no-op deletion.** Its only live uses are `cost-report.py:338` and
  `:366`; both go with the file. The key exists in **neither** config — `cost-report.py` hardcodes a
  200k default. There is no orphaned config to remove and no task for it. Re-verified at `ae2443d`:
  `grep -rn context_per_turn_tokens` over `.claude/`, `docs/` and both configs returns only
  `cost-report.py` and the DEC-148 index row.
- **Unknown DIGEST keys are ignored by `validate-digest.py`** (probed: a payload carrying
  `bogus_extra_key` returned `digest ok`, exit 0). This is what makes SC-04's second half achievable
  and makes removing the schema field safe for in-flight returns.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-05
