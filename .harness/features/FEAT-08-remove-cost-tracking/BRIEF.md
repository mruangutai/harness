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
- REQ-04: **UNDER AMENDMENT A-4 — see `## Amendments`. The approved text below is left in place and
  has deliberately NOT been overwritten; its SECOND clause is retired by the user's ruling.**
  The return contract neither requires nor rejects a cost field. A return written to the new
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

- SC-01: **UNDER AMENDMENT A-4 — see `## Amendments`. (A-2 amended this criterion first and is
  SUPERSEDED BY A-4; read A-4, not A-2.) The text below is the approved text and is UNREACHABLE as
  written; it has deliberately NOT been overwritten.** A single replacement text and its
  measurements are in A-4; the user re-signs.
  `grep -rln -e cost_usd -e cost-report -e max_cost -e per_feature_usd -e INV-11` over
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
- SC-04: **UNDER AMENDMENT A-4 — see `## Amendments`. The approved text below is left in place and
  has deliberately NOT been overwritten; A-4 NARROWS it to its first half.**
  An `orchestrator` DIGEST that **omits** `cost_usd` is accepted by
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
  **AMENDED BY A-4 — see `## Amendments`.** The behaviour is unchanged and re-verified structurally;
  what changes is its referent (SC-04's second half is dropped) and its evidential status (the
  committed suite asserts the property only incidentally). A-4 §4 carries the replacement text.

## Amendments

### A-2 — SC-01 is unreachable as written (2026-08-05, drafted by `harness-pm`) — **SUPERSEDED BY A-4**

> **SUPERSEDED BY A-4 (2026-08-05).** The user chose NEITHER of the two options below. A-2 is kept
> verbatim, not deleted, because the record of the two rejected options is why A-4's wording is what
> it is — and because A-2's `ae2443d` and `95c1c38` measurements are still the discriminating
> baseline A-4 builds on. **Do not implement anything in this section.** The live replacement text
> for SC-01 is in A-4.

**This BRIEF is AMENDED and AWAITING THE USER'S RE-SIGNATURE.** The `## Approval` block below still
carries the signature taken against the pre-amendment text and has been left untouched — only the
main session may write it. SC-01's approved text at `:69` is **also** left in place, with a pointer
added; overwriting a signed criterion with an unsigned one is the thing this section exists to
avoid. **`harness-pm` recommends but does not choose.**

#### The problem

SC-01 requires the sweep to return **only** `DECISIONS.md` and `DECISIONS-INDEX.md`. Four other
files cannot leave it, and **three already-approved requirements are why**. SC-01 is the feature's
headline criterion, so this is not a wording tidy-up.

| File | Why it cannot leave | Mandated by |
|---|---|---|
| `bin/test-validate-digest.py` | carries `cost_usd: "12.83"` as the backward-compatibility pin (`:753`, comment at `:749`) | **T-01's intent**, proving **SC-04**'s second half. Strictly unavoidable — SC-04 requires the fixture SC-01 forbids |
| `docs/harness/BUILD.md` | retains `(cost-report.py removed — DEC-178)` markers | **T-11** + **D-07**, blessed by **SC-14** |
| `docs/harness/SPEC.md` | same marker at the §15.5 retrospective | **T-10** + **D-07**, blessed by **SC-14** |
| `bin/test-check-state.py` | `:205`, `:326` name INV-11 in prose explaining what the deleted invariant used to do | nothing. **Avoidable by rewording**, at the cost of deleting the explanation of why the new case exists |

SC-14 is the sharpest conflict: *"every remaining `cost-report.py` mention carries an inline removed
marker"* **presupposes mentions remain**. SC-01 forbids exactly those mentions. **Three requirements
agreeing against one is evidence about which one is wrong** — SC-04, SC-14 and D-07 are therefore
NOT amended, and no amendment below touches them.

#### Measurement — pinned to SHAs, because S4 is running now

`harness-documentor` is mutating `SPEC.md` and `BUILD.md` concurrently, so a working-tree grep
returns a set that is neither the base nor the final. Every figure below is `git grep` against a
commit.

```
git grep -ln -e cost_usd -e cost-report -e max_cost -e per_feature_usd -e INV-11 <SHA> \
  -- .claude/ docs/ .harness/harness.json .harness/team-config.yaml .harness/README.md
```

| SHA | Files | Which |
|---|---|---|
| `ae2443d` (base) | **18** | the ten `.claude/` surfaces, both `harness.json`, both `teams/*.yaml`, `BUILD.md`, `SPEC.md`, `DECISIONS.md`, `DECISIONS-INDEX.md` |
| `95c1c38` (S2 complete) | **6** | `test-check-state.py`, `test-validate-digest.py`, `BUILD.md`, `DECISIONS-INDEX.md`, `DECISIONS.md`, `SPEC.md` |

**The `6 == 6` coincidence is not confirmation, and must not be read as one.** At `95c1c38`
`BUILD.md` (5 raw hits) and `SPEC.md` (12) are in the sweep for **pre-T-10/T-11** reasons; post-S4
they will be in it for **marker** reasons. Same file set, different cause. The four-survivor set is
**verified at `95c1c38` only for the two test files**, and is a **projection** for `BUILD.md` and
`SPEC.md` that S4's actual output must confirm. If S4 lands and either file leaves the sweep
entirely, see the superset wording below — that is a pass, not a failure.

#### Option (a) — widen the expected set, each survivor with its reason named  · **RECOMMENDED**

> - SC-01: `grep -rln -e cost_usd -e cost-report -e max_cost -e per_feature_usd -e INV-11` over
>   `.claude/`, `docs/`, `.harness/harness.json`, `.harness/team-config.yaml` and `.harness/README.md`
>   returns **no file outside** this set of six, each of which survives for a named, already-approved
>   reason:
>   `docs/harness/DECISIONS.md` and `docs/harness/DECISIONS-INDEX.md` — the historical entries and
>   rows, kept by REQ-06 / constraint 3;
>   `docs/harness/BUILD.md` and `docs/harness/SPEC.md` — the inline `(cost-report.py removed —
>   DEC-178)` markers mandated by T-11/T-10 under D-07 and required by SC-14, which presupposes that
>   mentions remain;
>   `.claude/skills/harness/bin/test-validate-digest.py` — the `cost_usd: "12.83"` backward-
>   compatibility pin (`:753`) mandated by T-01 and required by SC-04's second half;
>   `.claude/skills/harness/bin/test-check-state.py` — prose at `:205`/`:326` explaining what the
>   deleted INV-11 used to do, which is why the new test case exists.
>   **Superset, not exact set:** a file leaving is a pass; a seventh file appearing is a failure.
>   Presence of the four survivors is already carried by SC-04 (the pin) and SC-14 (the markers);
>   SC-01's job is the absence half.
>   **Discriminating:** the same command returns **18 files at `ae2443d`**, of which **12 are outside
>   this set** — so this is not an already-empty absence-grep and would NOT have passed at the base
>   commit. It returns **6 at `95c1c38`**, all six inside the set.
>   verify: automated        evidence: command

#### Option (b) — narrow the pattern to exclude fixture and marker contexts

Excluding marker lines alone is insufficient: measured, dropping every line containing `DEC-178`
leaves **6 files at `95c1c38`** and **18 at `ae2443d`** — a no-op at base, and it does not reach the
two test fixtures. (b) therefore needs **two** exclusions: drop `DEC-178`-marked lines *and* exclude
`.claude/skills/harness/bin/test-*.py` from the file scope. Measured with both:

```
git grep -n -e cost_usd -e cost-report -e max_cost -e per_feature_usd -e INV-11 <SHA> \
  -- .claude/ docs/ .harness/harness.json .harness/team-config.yaml .harness/README.md \
     ':!.claude/skills/harness/bin/test-*.py' | grep -v 'DEC-178' | cut -d: -f2 | sort -u
```
→ **15 files at `ae2443d`**, **4 at `95c1c38`**. Expected set would be the two `DECISIONS` files.

> - SC-01: the command above returns **only** `docs/harness/DECISIONS.md` and
>   `docs/harness/DECISIONS-INDEX.md`. Fixture files under `bin/test-*.py` and lines carrying the
>   `DEC-178` removal marker are excluded, because SC-04 and SC-14 respectively require them.
>   **Discriminating:** the same command returns **15 files at `ae2443d`**, so it would not have
>   passed at the base commit.
>   verify: automated        evidence: command

**Neither option is a deletion.** (a) fails at `ae2443d` with 12 out-of-set files; (b) fails with 15.
Both figures are stated so the check is on the record for the option that is rejected as well as the
one recommended.

#### Recommendation: **(a)**, one reason

**(b) buys its cleaner expected set by creating two permanent escape hatches from the sweep, and the
worse of the two is real, not theoretical:** excluding `bin/test-*.py` wholesale means SC-01 stops
watching `test-cost-report.py` — the deleted meter's own test — so a future reinstatement of the
meter's test would not register, and any file can be removed from the sweep thereafter by adding a
`DEC-178` marker line. (a) names each survivor and its mandating requirement inside the criterion, so
the criterion audits itself: a seventh file, or a survivor whose stated reason no longer holds, fails
it. (b)'s marker clause also duplicates SC-14, which already checks exactly that.

#### One sub-choice inside (a) — the user's call at signature

`test-check-state.py:205`/`:326` is the **only** one of the four that is avoidable: the INV-11
references are historical prose, not a fixture, and could be reworded out. **Recommendation: keep
them.** Deleting the explanation of why a test case exists in order to satisfy a grep is the tail
wagging the dog, and the grep is meant to find live instructions, not history. If the user prefers
the rewording, **SC-01 needs no re-amendment** — the superset wording in (a) makes a file leaving the
set a pass. The choice can therefore be deferred past signature.

#### Untouched, and checked rather than assumed

- **SC-04, SC-14 and D-07 are not amended.** Nothing in A-2 edits them.
- **`## Problem`, line `:29`** — "That the sweep grep returns 18 and not 0 is what makes SC-01
  discriminating" — re-read for this amendment. It survives both options verbatim (18 at `ae2443d`
  is confirmed above) and needs no edit.
- **SC-05's cycle surfaces** are not in scope of A-2.

### A-4 — the user ruled: delete the pin, not the criterion (2026-08-05, drafted by `harness-pm`)

**This BRIEF is AMENDED and AWAITING THE USER'S RE-SIGNATURE.** The `## Approval` block below still
carries the signature taken against the pre-amendment text and has been left untouched — only the
main session may write it. A-4 is bundled into the same pending re-signature as A-1 and A-3. Nothing
downstream should treat that signature as covering A-1, A-3 or A-4 until the user re-signs.
**A-4 supersedes A-2 in full**; A-2 is marked in place, not deleted.
**A-4's counterpart section is `PLAN.md ## Amendments` → A-4** (amendment numbering is feature-wide
across both signed artifacts). This section carries the BRIEF-side changes; the PLAN-side changes to
T-01 and T-02 are there.

#### 0. The ruling

A-2 offered two options for the unreachable SC-01 — widen the expected set, or narrow the pattern.
The user chose neither: *"why can't we remove it outright? i don't care about backwards
compatibility and any extra code to maintain it is a waste."* The ruling is to **delete the thing
the exception existed to protect** — the `cost_usd: "12.83"` backward-compatibility pin in
`test-validate-digest.py` — and to reword the two INV-11 prose sites in `test-check-state.py`.
Both edits are **main-session-direct** (DEC-174 carve-out surfaces) and are **follow-up work, not
yet done**.

Two premises of the ruling, re-verified here rather than relayed:

- **Zero producers.** `grep -rn --exclude-dir=worktrees cost_usd .claude/agents
  .claude/skills/harness/SKILL.md .claude/skills/harness-team/SKILL.md` → **no output, exit 1**
  (working tree at `5ce3b13`; `bin/` is clean against `5ce3b13` — `git diff --quiet 5ce3b13 --
  .claude/skills/harness/bin/` exits 0). T-05/T-06 removed the last instruction to emit the field,
  so the guarantee protects a transition window with no inhabitants.
- **The pin's replacement coverage is NOT what the dispatch claimed.** See §3 — this is the one
  place A-4 contradicts its own brief, and it does not change the ruling.

#### 1. The sweep at `5ce3b13`, decomposed — 6 today, 4 after

```
git grep -ln -e cost_usd -e cost-report -e max_cost -e per_feature_usd -e INV-11 5ce3b13 \
  -- .claude/ docs/ .harness/harness.json .harness/team-config.yaml .harness/README.md
```
→ **6 files**, pasted verbatim:

```
5ce3b13:.claude/skills/harness/bin/test-check-state.py
5ce3b13:.claude/skills/harness/bin/test-validate-digest.py
5ce3b13:docs/harness/BUILD.md
5ce3b13:docs/harness/DECISIONS-INDEX.md
5ce3b13:docs/harness/DECISIONS.md
5ce3b13:docs/harness/SPEC.md
```

**6 = the 4 survivors + the 2 the follow-up edits remove → 4 after.**

| File | Disposition | Why |
|---|---|---|
| `docs/harness/DECISIONS.md` | **survivor** | historical entries, kept by REQ-06 / constraint 3 |
| `docs/harness/DECISIONS-INDEX.md` | **survivor** | historical rows, same |
| `docs/harness/BUILD.md` | **survivor** | inline `(cost-report.py removed — DEC-178)` markers (T-11, D-07), **blessed by SC-14** |
| `docs/harness/SPEC.md` | **survivor** | same marker at SPEC `:2129` (T-10, D-07), blessed by SC-14 |
| `bin/test-validate-digest.py` | **leaves** | **all three** of its hits go: the pin payload at `:753` and its comment at `:749` are deleted, and the surviving fixture's comment at `:769` is reworded off the literal spelling (PLAN A-4 §T-01) |
| `bin/test-check-state.py` | **leaves** | **both** of its hits go: the INV-11 prose at `:205` and `:326` is reworded (PLAN A-4 §T-02) |

**The departures are verified by enumeration, not by arithmetic.** Every hit in the two leaving
files was listed with the full five-token pattern at `5ce3b13` and confirmed to sit inside text the
follow-up edit removes or rewords:
`test-validate-digest.py` → `:749`, `:753`, `:769`; `test-check-state.py` → `:205`, `:326`.
**`:769` is the trap**: it is the comment on the fixture that SURVIVES, and it carries the literal
spelling. Deleting the pin alone would leave the file in the sweep and re-create A-2's defect.

Every BUILD.md and SPEC.md hit at `5ce3b13` was re-read and **every one carries the removal marker**
(`git grep -n <tokens> 5ce3b13 -- docs/harness/SPEC.md docs/harness/BUILD.md` → BUILD `:191`, `:224`,
`:225`, `:333`, `:578`; SPEC `:2129`). That is exactly the state SC-14 mandates, which is why these
two are survivors and not defects: **SC-14's "every remaining mention carries an inline removed
marker" presupposes mentions remain.** No criterion-contradicts-criterion paragraph is needed any
more — that was the cost of the option the user rejected.

**SC-01 is therefore REACHABLE, conditional on the two main-session-direct follow-up edits landing.
Reachable is not the same as passing now: at `5ce3b13` the sweep returns 6, and 2 of them are
outside the amended expected set.**

#### 2. Why `--exclude-dir=worktrees` joins the command — and why it is a no-op at the base

FEAT-09's worktree now lives at `.claude/worktrees/FEAT-09/`, a second full copy of the repo inside
SC-01's search path. Working tree at `5ce3b13`:

| Command | Files |
|---|---|
| `grep -rln <tokens> .claude/ docs/ …` | **78** |
| `grep -rln --exclude-dir=worktrees <tokens> .claude/ docs/ …` | **6** |

**78 cannot be pinned to a SHA and is not claimed to be**: `.claude/worktrees/` is gitignored
(`.gitignore:21`), so it is a working-tree figure by construction. The **6** is confirmed by two
independent methods — `git grep` at `5ce3b13` (§1) and the flagged working-tree grep above — and
they return the same six paths. That agreement is a cross-check of one tree, and is **not** the
`6 == 6` coincidence A-2 warned about (which compared two different SHAs).

**The flag is a no-op at `ae2443d`, verified as a fact about the disk rather than inferred from grep
semantics:** `git log -1 --format=%cI ae2443d` → `2026-08-05T06:06:25-07:00`;
`stat -f '%SB' .claude/worktrees/FEAT-09` → `Aug  5 07:02:15 2026`. The worktree postdates the base
commit by 56 minutes, so no worktree existed when the discriminating **18-file** base measurement was
taken. **That measurement stands unchanged.** (Independently: A-2's 18 came from `git grep` at a SHA,
which cannot see an untracked path — re-run for this amendment, still 18.) The flag also aligns the
criterion with `.harness/harness.json`, whose `test_kinds` `exclude` strings carry
`.claude/worktrees/**` at `:85`, `:90`, `:96`, `:102`, `:108`, `:114`, `:120` and `:133`.

#### 3. Replacement text — SC-01

> - SC-01: `grep -rln --exclude-dir=worktrees -e cost_usd -e cost-report -e max_cost
>   -e per_feature_usd -e INV-11` over `.claude/`, `docs/`, `.harness/harness.json`,
>   `.harness/team-config.yaml` and `.harness/README.md` returns **no file outside** this set of
>   four, each surviving for a named, already-approved reason:
>   `docs/harness/DECISIONS.md` and `docs/harness/DECISIONS-INDEX.md` — the historical entries and
>   rows, kept by REQ-06 / constraint 3;
>   `docs/harness/BUILD.md` and `docs/harness/SPEC.md` — the inline `(cost-report.py removed —
>   DEC-178)` markers mandated by T-11/T-10 under D-07 and **required by SC-14**, which presupposes
>   that mentions remain.
>   **Superset prohibited, subset allowed:** a fifth file is a FAILURE; a file leaving the set is a
>   pass. `--exclude-dir=worktrees` excludes `.claude/worktrees/**`, a second checkout of this repo,
>   matching `harness.json`'s `test_kinds` exclusions.
>   **Discriminating:** the same command returns **18 files at `ae2443d`**, of which **14 are
>   outside this set** — so this is not an already-empty absence-grep and would NOT have passed at
>   the base commit. At `5ce3b13` it returns **6**, of which **2** are outside the set: the two files
>   the main-session-direct follow-up edits remove.
>   verify: automated        evidence: command

#### 4. Replacement text — SC-04, and the REQ-04 disposition

> - SC-04: An `orchestrator` DIGEST that **omits** `cost_usd` is accepted by
>   `.claude/skills/harness/bin/validate-digest.py` (exit 0, `digest ok`).
>   **Discriminating:** at `ae2443d` that same payload is rejected
>   `BLOCKED (contract violation) — missing 'cost_usd'` at exit 1, so it can only go green once the
>   schema entry is gone.
>   verify: automated        evidence: unit

The second half — *"and one that still carries it is also accepted"* — is **dropped**, and its
fixture with it. SC-04 remains discriminating on the surviving half.

**REQ-04 moves with it, and this is a ruling on a REQUIREMENT, not only on a criterion.** REQ-04's
second clause — *"and a return still carrying the old field also validates, so no in-flight run is
broken by the transition"* — is exactly what SC-04's second half and the pin existed to verify.
It is **RETIRED by the user's ruling**: with zero producers (§0) there is no in-flight run to break,
and the user ruled that code maintained for backward compatibility is waste. A pointer has been added
at REQ-04; its approved text is left in place, unoverwritten.

What still covers the mechanism: **unknown-key tolerance is generic and structural**, not
cost-specific. `validate-digest.py`'s field loop iterates `{**schema, **UNIVERSAL}` and there is no
branch anywhere that rejects a key present in the payload but absent from that set. Behaviour is
unchanged, and **`PLAN.md` D-01's safety rationale ("the measured extra-key tolerance is what makes
removal safe") is therefore UNCHANGED and is not amended** — the tolerance is still true and still
what makes removal safe.

**The dispatch's replacement-coverage anchor does not hold, and is corrected here rather than pasted
forward.** `test-validate-digest.py:1213` and `:1233` were opened at `5ce3b13`: both are **comment
lines, not assertions**. `:1212-1215` explains that case (g2) was green at SHA `4091b36` *because*
`task` was then an unknown key — `task` is in the dev schema today (`vd` field loop), so the case no
longer exercises tolerance. `:1232-1234` uses "unknown key ignored" as the name of the **bad** shape
its detector pair exists to rule out — the opposite property.

Measured instead of argued. A strict-unknown-key **mutant** of `validate-digest.py` (built from
`git show 5ce3b13:`, one added rejection of any payload key outside `{**schema, **UNIVERSAL}`,
allowing the two separately-checked keys `headline` and `artifact`) was run through the real suite
via its `VALIDATE_DIGEST_BIN` override. Result: **2 FAILING**, and they are:

- `orchestrator digest with the reconciled schema` — the pin fixture at `:753`. **The only
  deliberate assertion of unknown-key tolerance in the suite.**
- `[hook] DEC-156: file check governs leads only — a dev's artifact is not read` — whose dev payload
  carries `branch: none`, a field in the **lead** schema only (`validate-digest.py:165`). Incidental,
  not an assertion about tolerance.

**Residual, stated rather than softened: once the pin is deleted, the committed suite asserts
unknown-key tolerance only incidentally.** The behaviour is safe; the *coverage* is thin. A-4 does
NOT add a test to close this — that would be new mandate beyond the ruling. It is raised as an open
question (see the DIGEST), with a concrete cheap shape: one orchestrator fixture carrying
`bogus_extra_key`, asserted accepted. That is the user's call.

The settled fact at `## Settled facts` (the `bogus_extra_key` probe) is amended by pointer, not
overwritten. Its replacement reading: **unknown DIGEST keys are ignored — structural, verified at
`5ce3b13` by the mutant run above; this is what makes removing the schema field safe for any return
still carrying it, and after the pin is deleted the committed suite covers it only incidentally.**

#### 5. Falsifiability closure — why SC-01 is the falsifier for both follow-up edits

T-02's `verify:` clauses check `check-state.sh`, not `test-check-state.py`, so **nothing in T-02
catches the INV-11 prose rewording**. That is the unfalsifiable-site failure A-3 named, and it would
recur here. **The amended SC-01's four-file set closes it:** `test-check-state.py` and
`test-validate-digest.py` are each in the sweep today and each leaves it only if its follow-up edit
lands. Superset-prohibited is what gives this teeth — if either edit is skipped, SC-01 returns a
fifth (or sixth) file and fails.

#### 6. Untouched, and checked rather than assumed

- **SC-14, D-07, T-10 and T-11 are NOT amended.** The markers are correct and required; SC-01 is the
  criterion that was wrong.
- **D-01 is NOT amended** (§4): its rationale rests on tolerance, which is unchanged.
- **A-1 and A-3 are NOT touched, and nothing is renumbered.** A-3's "Cross-reference to A-2 — no
  effect" (`PLAN.md:879-883`) says SPEC.md is "already among the six": **the set of six becomes four,
  and A-3's conclusion still holds because `docs/harness/SPEC.md` remains in it.** A-3 is not edited.
- **`## Problem`, the "18 and not 0" sentence** — re-verified at `ae2443d` for this amendment (still
  18). Survives verbatim; no edit.
- **No `cost:` block is recorded for this amendment** — `cost-report.py` was deleted by T-03 and
  INV-11 by T-02.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-05
