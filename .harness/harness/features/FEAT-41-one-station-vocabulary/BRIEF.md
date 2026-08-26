# BRIEF — FEAT-41 One station vocabulary

## Problem

Six places hold the names of the board's columns and nothing ties them together. `harness.json`
declares six; `gh-sync.py:104` hardcodes seven capitalised ones; `check-plan-routes.py:415` gives
`plan.yaml` a third vocabulary entirely (`pending`/`building`/`done`); `feature-schema.json`
carries a fourth as an enum. Rename a column and the harness keeps writing the old word, silently
— `check-plan-routes.py:337` already records the shape: a capital-B `Building` "would read as
not-done forever". Underneath that, `plan.yaml` — the file the whole flow reads for what is
happening — has no code writer at all. `gh-sync.py:815`'s docstring claims `start-task` records
`building` there; its body contains zero `plan.yaml` writes, so an LLM types the value by hand,
and `harness-orchestrator.md:78` records five task statuses lost that way already. The result is
live today: `check-state.sh` reports `VIOLATION INV-26 FEAT-40-harness-writes-done parent (issue
#842): the plan derives Review — the board reads Done`, because `ship`'s `Done` write was made in
a worktree that was then deleted and never committed.

## Goal

One vocabulary, declared once, written only by code. `harness.json` names the six stations;
`plan.yaml` records where each task and the feature itself stand, in those same words; one
function projects `plan.yaml` onto the GitHub board. No language model edits `plan.yaml` — every
write goes through a command that validates the station first, and the approval signature through
the same command, refused unless the caller is the main session.

## Requirements

- REQ-01: The six station names are mandated and declared in exactly one place; a configuration
  declaring anything else is refused loudly rather than silently obeyed.
- REQ-02: Everything the harness stores or compares is lowercase; the board's exact spelling
  appears only where the harness talks to GitHub.
- REQ-03: `plan.yaml` records a station for each task and for the feature, drawn from that one
  vocabulary.
- REQ-04: One function decides every card's station, from `plan.yaml`; no other code makes that
  decision.
- REQ-05: `plan.yaml` is written only by code. An agent cannot write it with an editor tool, and
  cannot write the approval signature at all; only the main session can record a signature.
- REQ-06: A feature's station is recorded in exactly one file.
- REQ-07: A shipped feature's terminal record survives on the default branch, and `ship` refuses a
  feature directory that is about to be deleted.

## Constraints

Which of these BLOCK and which SUPPLY is stated for each, because most of them supply.

- **DEC-174 BLOCKS execution.** This work changes hooks, validators and gate scripts, so the
  harness may plan it but must not execute those changes through the enforcement path being
  changed. Twelve of the plan's thirteen tasks are therefore executed by the main session
  directly; only T-12, the decision-record task, runs on the team lane, with `harness-documentor`.
  This is the largest cost of the feature and it is accepted, not worked around.
- **DEC-203 section 6 SUPPLIES the six values and BLOCKS their casing.** It states one lifecycle
  field whose values are case sensitive byte for byte, in `feature.json`. REQ-02 and REQ-06
  contradict that clause, so the entry takes an amendment. Everything else in DEC-203 — a ticket
  is open until its card reaches `Done`, the harness writes `Done` at ship, the parent rule, the
  seven-purpose read-back bound — is untouched and still binds.
- **DEC-191 BLOCKS deleting a key silently.** `feature.json`'s key set is closed with
  `additionalProperties: false` and `status` is one of its eight required keys, so REQ-06 moves
  the schema and the decision together.
- **DEC-182 SUPPLIES `plan.yaml`** and currently states that `plan.yaml` is deliberately excluded
  from the shape gate (`check-domain.sh:1017`). REQ-05 reverses that clause; it takes an amendment.
- **DEC-180 SUPPLIES the mechanism for REQ-05**: the shape gate is independent of domain and binds
  every author including the main session. The domain region cannot be used, because
  `check-domain.sh` exits 0 for a payload with no `agent_type`.
- **DEC-120 SUPPLIES the signature rule** and this feature makes it mechanical rather than
  documentary.
- **DEC-179 SUPPLIES route resolution** — every task's lane is resolved at plan time.
- **DEC-202 constrains where agent prose is edited**: `.omp/agents/` is canonical and
  `.claude/agents/` is generated.
- Out of scope, from the source ticket: the board's column names themselves. They are correct.
- **A disclosure, not a decision.** After REQ-05 lands, a shell command that writes a *legal*
  station value into `plan.yaml` is still not attributable to its author. The post-Bash sweep
  reads what landed on disk, so it catches a dead word and a broken file; it cannot catch a
  well-formed forgery. Closing that would need write attribution the platform does not offer.

## Success Criteria

- SC-01: `harness.json` declares the six stations once, as one ordered lowercase list, and a
  declaration naming anything else is refused with an error naming the offending key.
  `_STATION_KEYS` no longer exists anywhere in the tree.
  verify: automated        evidence: unit
- SC-02: No capitalised station name survives as a **quoted literal** in non-test source. The
  observation: `grep -rnE "[\"'](Backlog|Plan|Ready|Building|Review|Done)[\"']"` over
  `.claude/skills/harness/bin/*.py` and `*.sh`, excluding `test-*`, returns **zero** lines,
  including in comments and docstrings. The grep is quoted-literal, not bare-word, because the
  bare-word form returns 746 hits across 28 files — almost all of it English prose — and can
  therefore never reach zero. Discriminating today: re-measured at `ee66ae2` on 2026-08-25 by
  running the criterion's own grep, it returns **27 lines across 5 files** — `check-state.sh` 11,
  `gh-sync.py` 9, `board_lifecycle.py` 3, `check-plan-routes.py` 3, `worktree_terminal.py` 1,
  which sums to the total — and this feature repoints every one of them. Both the earlier totals
  (31, then 26) and the earlier per-file split were hand-carried rather than read off the command;
  these two numbers come from its output. `factory_config.station_column` produces the six column names with `.capitalize()` and so
  holds no literal of its own.
  verify: automated        evidence: unit
- SC-03: A `plan.yaml` task status or feature station outside the vocabulary is refused by the
  writer with a non-zero exit naming the value, and reported by `check-plan-routes.py` as a
  violation. No live `plan.yaml` carries a **task** status of `pending` afterwards — the
  four-space-anchored `grep -rn "^    status: pending" .harness/harness/features/*/plan.yaml`
  returns zero. Anchored, not bare: at `ee66ae2` the bare grep returns 72 hits and the anchored
  one 55, and three of the 17-hit difference are `approval:` blocks at two-space indent
  (`FEAT-19/plan.yaml:5`, `FEAT-28/plan.yaml:5`, and this feature's own `plan.yaml:7`) which the
  work is forbidden to touch. A bare grep therefore can never reach zero.
  verify: automated        evidence: integration
- SC-04: Changing one task's station in `plan.yaml` changes the card the projection function
  would write, and `gh_board.set_station` has **exactly one policy site** — one call that decides
  a station — outside tests. Two non-policy callers survive by design and are named here so the
  count is falsifiable: `board-station.py:153`, the operator's manual override, and
  `board_lifecycle.py:1013` and `:1016` inside `_apply_fix`, which applies a finding `reconcile`
  already made. So the whole-tree count of `gh_board.set_station(` outside tests is **four** after
  the work and **ten** at `ee66ae2`. More than four means a policy site survived; fewer means a
  disclosed residual was removed without a decision.
  verify: automated        evidence: unit
- SC-05: A `Write` or `Edit` of a `plan.yaml` is denied with exit 2 and a message that BOTH names
  the verb to use instead AND states the reason the previously-legal route is now closed — that
  `plan.yaml` has exactly one writer, `plan-write.py`, because every station value must be
  validated before it lands — for a payload carrying an `agent_type` AND for a payload without one.
  A denial carrying only the verb does not meet this criterion.
  verify: automated        evidence: integration
- SC-06: A shell write that lands a station value outside the vocabulary in a `plan.yaml` is
  reported by the post-Bash sweep, naming the file and the offending value.
  verify: automated        evidence: integration
- SC-07: `sign-approval` is refused when the hook payload carries an `agent_type` and permitted
  when it does not, and the refusal names BOTH the refused verb — the literal string
  `sign-approval` — and the sanctioned route.
  verify: automated        evidence: integration
- SC-08: No `feature.json` in the tree carries a `status` key, the schema rejects one, and each of
  the eleven former readers reads the feature's station from `plan.yaml` instead.
  verify: automated        evidence: integration
- SC-09: At `review_sha`, `git show <review_sha>:.harness/harness/features/FEAT-40-harness-writes-done/plan.yaml`
  records the done station, and a run of `check-state.sh` reports no `INV-26` line for
  FEAT-40. The failing state is demonstrated first: the same command at `ee66ae2` reports the
  violation.
  verify: inspection
- SC-10: `gh-sync.py ship` refuses a feature directory inside `.claude/worktrees/`, naming the
  main-checkout path instead, and on the success path the terminal station write is committed —
  a test asserts the file is clean against `HEAD` after `ship` returns.
  verify: automated        evidence: integration
- SC-11: The whole suite is green and `check-plan-routes.py` exits 0 over every live plan,
  including this one.
  verify: automated        evidence: integration
- SC-12: The renamed writer is reachable by its new name from every live caller, and no live
  caller still names `plan-merge.py`. If the rename task is struck at approval, this criterion is
  struck with it.
  verify: automated        evidence: unit
- SC-13: `check-state.sh`'s INV-26 takes its expected station from the same function that writes
  it, and a station it cannot map is loud. Observations, both required: `grep -n "_EXPECT"
  .claude/skills/harness/bin/check-state.sh` returns nothing, and a fixture plan carrying a task
  station outside the vocabulary makes INV-26 emit a violation line naming the feature, the task
  id and the value — where at `ee66ae2` the same fixture is silently skipped by the
  `if _want is None: continue` at circa `:1476`. The failing state is demonstrated first.
  verify: automated        evidence: integration

## Verification gaps

- `component`, `ui`, `eval` and `typecheck` carry `cmd: null` in `.harness/harness.json`. None of
  them detects a file this feature touches, so no criterion above rests on a null runner.
- `test-gh-sync.py` is measured at **149 s** and is run in full by two tasks (T-06 and T-10),
  about 298 s across the plan, against a 60-second guideline per verify. Nothing is unproven by
  this — the tests do run — but the plan pays roughly five minutes for it. Narrowing either verify
  would remove the only proof those tasks have, so it is accepted here and carried as **PB-01**
  below, which is what makes the cost temporary rather than permanent.

## Proposed backlog

Proposed only. These become GitHub issues when the main session accepts the ship — not during the
build, and not opened by an agent. The row exists so a deferral has an instrument instead of
living in prose that nothing ever reads again.

- **PB-01 — case selection for `run-unit-tests.sh`.** Let a `verify:` name the cases it needs
  instead of running a whole test file. `test-gh-sync.py` costs 149 s and this plan runs it in
  full twice (T-06 and T-10), about 298 s, against a 60-second-per-verify guideline. Recovers
  roughly 150 s on a plan of this shape and takes future verifies back under the guideline.
  Deferred out of FEAT-41 because it edits the test harness — whose KIND CROSS-CHECK this feature
  already touches at T-08 and T-13 — and changing the harness inside a feature that is rewriting
  the harness's own enforcement surface buys a failure mode worth more than the time it saves.
- **PB-02 — where an abandoned feature's card belongs.** FEAT-28 is abandoned and its card sits at
  `Done`, which reads as shipped to anyone scanning board 3. Deferred out of FEAT-41 because it
  predates this feature, is not one of issue #845's seven items, and — more to the point — this
  feature decides `abandoned` names no column at all, so there is no station to move the card to.
  Recovers a truthful board: the question of what the board shows for an abandoned feature is its
  own decision, and answering it here would be deciding it by accident.
- **PB-03 — FEAT-12's parent issue has no card on board 3.** Issue 223 is projected by
  `gh_board.project` but carries no item on the board (measured at `8f8a6a3`, 2026-08-25): the
  feature shipped and its parent was never added. Deferred out of FEAT-41 because T-10's one-time
  pass is a migration — it moves cards and adds none — so the gap is printed as a skip and left
  visible rather than closed by a side effect nobody asked for. Recovers full board coverage for
  shipped features, and closing it is one deliberate add rather than a rule inside a migration.

## Approval

status: pending
approved-by:
date:
