# BRIEF — FEAT-29 GraphQL budget

## Problem

On 2026-08-18 the account's GraphQL rate budget reached 4,941 of 5,000 in a single session while
REST sat at 15 of 5,000. Two live agent runs were left at risk of failing mid-flight, and when the
budget is exhausted a run dies with a raw `gh` error that names a rate limit but not which budget,
not what spent it, and not when it resets — so the operator's first move is to guess.

Measurement (`notes/research-plan-product.md`, 2026-08-19, at `6bbd706`) attributes it. **One run of
`.claude/skills/harness/bin/check-state.sh` costs 490-506 GraphQL points** (board 3, 473 items,
commit `6bbd706`). This project's own CLAUDE.md says to run it before every commit, so a working
session spends thousands of points on the state gate alone. The cost is INV-26 at `check-state.sh:1174`, which reads the entire 473-item board
through `gh project item-list --limit 500`. A standalone sample of that call read 608 points on
board 3, but the run that contains it measured 490-506, so 608 is a contaminated upper bound taken
with another agent run in flight — the honest record is 490-506 per run. The same call against the
four-item board 6 costs 102 points, so its cost is dominated by the query's field selection, and it
grows with the number of items returned.

The exclusion that let this stand was a rotted number. On 2026-08-10 the same call was recorded at
31 points and scoped out of issue #211 as "not the burn". The figure was written down without the
board it was measured on or that board's item count, so it could not be falsified as the board grew,
and a real exclusion decision was built on top of it.

## Goal

Bring the harness's routine GraphQL spend down to a level where a normal working session cannot
exhaust the budget, and make the next surprise attributable instead of a guess. The state gate must
keep detecting exactly what it detects today — an unstationed card and a card that is not on the
board stay two different findings — while costing a small fraction of what it costs now. When the
budget does run out, the operator must be told which budget, and when it resets, instead of reading
a raw `gh` error.

## Requirements

- REQ-01: A full `check-state.sh` run costs a small, bounded number of GraphQL points, and INV-26
  reports the same violations and non-violations it reports today.
- REQ-02: An unstationed card and a card absent from the board remain distinguishable findings after
  the read is made cheaper.
- REQ-03: **AMENDED 2026-08-19, operator ruling — the recorder is OPT-IN, not always-on.** The
  original text read: *"The operator can find out, after the fact, which harness operations spent
  GraphQL points and how many, without re-running anything."* That is struck. It required
  always-on recording to mean anything, and two measurements taken during this feature made the
  trade a bad one. First, the recorder is **blind to the calls that caused the incident it was
  designed for**: its own coverage header says a `gh` command typed directly into Bash is
  invisible, and the 2026-08-19 burn was ~360 points of `gh pr checks` typed into Bash. Second,
  after T-01 and T-02 the operation it *can* see costs 5 points instead of 506, so it now watches
  the cheap path and misses the expensive one. It also forks two `rate_limit` reads per wrapped
  call, which measurably raised `--kind integration` runtime. The capability is kept and the
  default inverted: **the recorder is OFF unless `HARNESS_GH_COST_LOG=1` is set**, for use while
  investigating a burn. The operator accepts that a future unexplained burn is investigated from
  scratch unless logging was switched on first.
- REQ-04: When a `gh` call fails because the GraphQL budget is exhausted, the operator is told it is
  the GraphQL budget and when it resets, rather than a raw `gh` error.
- REQ-05: Every recorded GraphQL cost figure in this repository carries the condition it was measured
  under, so a later reader can tell drift from falsification.
- REQ-06: The cost record declares its own blind spots, so it is never mistaken for a complete
  account of what was spent.

## Success Criteria

- SC-01: A `check-state.sh` run against the live board costs no more than 100 GraphQL points,
  measured by differencing `gh api rate_limit --jq .resources.graphql.used` across the run, with raw
  before and after values, the board's item count and the commit recorded. The same measurement,
  captured before the change lands, reads 490-506 — that is the red state, and it is captured
  first precisely because it cannot be recovered afterwards.
  verify: inspection
- SC-02: The board-read function returns, for a board fixture containing a stationed card, an
  unstationed card and a card belonging to another repository, exactly the same mapping the current
  implementation returns for that fixture: the other repository's card excluded, the stationed card
  present with its value, the unstationed card present with the value None and not dropped.
  verify: automated      evidence: unit
- SC-03: A whole-board read of the four-item fixture board 6 through the new read costs no more
  than 10 GraphQL points, differenced live with raw before and after values recorded, against a
  measured 102 points for the current `gh project item-list --limit 500` read of that SAME four-item
  board (before 1790, after 1892, board 6, 4 items, 2026-08-19, at `6bbd706`). Identical item count
  on both sides, so the saving cannot be attributed to the board returning fewer items — it is the
  query shape. `notes/measurement-board6.md` is the record.
  verify: inspection
- SC-04: `check-state.sh` emits the identical violation set before and after the change when run
  against the same tree, compared line by line, with any difference explained or the change rejected.
  verify: inspection
- SC-05: **AMENDED 2026-08-19 with REQ-03.** With `HARNESS_GH_COST_LOG=1`, every harness `gh`
  invocation that flows through `factory_gh.run_gh` or `gh-sync.py`'s wrapper is recorded with its
  subcommand and its GraphQL cost to a durable file, and tests prove the record is written for a
  wrapped invocation and that a *failing* wrapped invocation is recorded too, with its exit code,
  rather than silently skipped. **With the variable unset — the new default — a test proves NO file
  is created and NO line is written**, including for a failing invocation. That second half is the
  half that can fail: an opt-in recorder whose off state is untested is a recorder that is always on.
  verify: automated      evidence: unit
- SC-06: Every daily cost-record file opens with a coverage line stating plainly which invocations
  the record cannot see — `gh` commands typed directly into Bash by the main session or an agent,
  which flow through neither `factory_gh.run_gh` nor `gh-sync.py`'s wrapper — so the file is never
  read as a complete account of what was spent. The statement lives in a named constant in
  `gh_cost_log.py` and is written as the first line of each `.harness/logs/gh-cost-<date>.jsonl`.
  verify: inspection
- SC-07: When a `gh` call made through a harness wrapper fails with a rate-limit error, the harness
  surfaces a message naming the GraphQL budget and its reset time; one test drives the
  exhausted-budget response and asserts the message, and a second proves an unrelated failure does
  NOT produce it. The criterion is explicitly scoped to wrapped calls — a `gh` command typed
  straight into Bash still returns raw text, and that limit is stated where the operator will read
  it.
  verify: automated      evidence: unit
- SC-08: The 2026-08-10 grilling note's 31-point figure is corrected in place with the measured
  490-506 points per `check-state.sh` run and the condition it holds under (board 3, 473 items,
  commit `6bbd706`, 2026-08-19), recording 608 only as the contaminated upper bound it is — a run
  that contains the call cannot cost less than the call. ~~No surviving document asserts that
  `project item-list` is cheap enough to ignore~~ **AMENDED 2026-08-20, operator ruling.** No
  document THAT IS STILL IN FORCE asserts that `project item-list` is cheap enough to ignore, and
  no such document states a bare corrected number without its condition. A shipped feature's
  artifacts are frozen, dated history and are out of scope: `FEAT-11-graphql-field-resolve` reads
  `status: Done` and four of its documents carry the 31-point figure, but editing them would
  falsify a record of what was known on its date. The clause as signed quantified over every
  surviving document while the task discharging it named one file, so it could not be met by any
  amount of correct work. **AMENDED 2026-08-20 (second), operator ruling.** The condition binds
  PER DOCUMENT, not per figure: a document states its condition once and its figures inherit it.
  Read per-figure, the signed `BRIEF.md` and `plan.yaml` would themselves become violations of a
  rule they define, reinstating the unmeetable-criterion defect the first amendment cured. The
  governing condition set is THREE — board, item count, and the commit measured at — which
  overrides signed decision D-03's two: a figure without its commit cannot be re-derived, and that
  is precisely how the 31 survived nine days unfalsifiable.
  verify: inspection
- SC-09: **AMENDED 2026-08-20, operator ruling.** ~~`gh pr checks` polling by the main session no
  longer runs at a 10-second interval~~ — **the conduct conjunct is DROPPED (second amendment,
  2026-08-20, operator ruling): it was live conduct in a terminal, never an artifact, so no
  inspection at any pin can settle it and its own `verify:` method cannot reach it.** Grade SC-09
  on the rule conjunct alone. The recorded operating rule forbids shell wait loops
  outright, naming Monitor and `run_in_background` as the replacements. The rule must be present
  in the COMMITTED tree, not merely the working copy. ~~with the measured 2-points-per-poll cost
  cited~~ — the cost-citation clause is DROPPED. It was written when the remedy was a longer
  interval, where a per-poll price informs the choice. Approval amendment 1 replaced that remedy
  with a prohibition, and nobody choosing nothing needs a price.
  verify: inspection
- SC-10: The full unit and integration suites pass, and no test that passed before this feature
  fails after it.
  verify: automated      evidence: integration

## Verification gaps

- `component`, `ui`, `eval` and `typecheck` have `cmd: null` in `.harness/harness.json` and soft-skip
  in qa. No criterion here rests on them; this feature touches no UI and no model behaviour.
- `functional` is excluded under DEC-187 and is not used.
- **The cost criteria (SC-01, SC-03) are `inspection`, not `automated`, deliberately.** A cost gate
  wired into CI would spend the very budget it measures on every run, and would read another agent's
  traffic as its own — this session watched `graphql.used` jump about 300 points with no call of its
  own in between. So the saving is proven by a one-shot differenced measurement with raw numbers on
  the record, and only the query SHAPE is gated automatically.
- The ~4,550-point attribution rests on a run count inferred from convention, not recorded anywhere.
  That gap is what REQ-03 exists to close; it cannot be closed retroactively for this incident.

## Constraints

- **The pre-change baseline must be captured before any code lands.** Once the read is cheap the
  red state is gone and SC-01 and SC-04 have nothing to grade against.
- **`check-state.sh` is a DEC-174 carve-out.** Its edit is made directly by a human reading the
  diff, never dispatched through a team run whose gates are the thing being changed. `gh_board.py`
  and `factory_gh.py` are not carve-out files and may be built by the team.
- INV-26's detection behaviour is fixed. A station-filtered `--query` is not an acceptable fix: the
  contract at `gh_board.py:124-131` requires unstationed cards to survive the read, and a station
  filter deletes them.
- A truncated board read must keep raising rather than reporting an empty column.
- Assertions must avoid two known-broken absence idioms: `test "$(git grep ... | wc -l)" = 0` passes
  when the search errors (#248), and `git grep -E` does not honour `\b` (#249).
- Board pruning is not assumed. See the open question below.
- Do not build the `gh issue create` REST migration. Measured at 2 points per create, it would
  recover roughly 36 of 4,941 points.

## Open questions

- Q1 (blocking): board 3 holds 473 cards and every cost here is linear in that count. Is pruning or
  archiving old cards in scope? A one-off prune to ~50 cards would beat any code change on its own,
  and it is not exclusive with the code fix — but it changes the task set, so it is the user's call.

  **RULED 2026-08-19 — code fix only. No prune, no archive.** The task set stands as planned; no
  task is added or removed. The reasoning the operator's ruling rests on: a prune lowers today's
  bill but leaves the cost linear in card count, so the figure rots again as the board refills —
  which is the exact failure this feature exists to stop, the 31-point measurement from 2026-08-10
  having rotted to 490-506 the same way. Re-measured at signature: the board holds **474** cards,
  one more than when this question was written, which is the linearity making the argument.

## Approval

status: approved
approved_by: operator (Mike Ruangutai), via main session
date: 2026-08-19
