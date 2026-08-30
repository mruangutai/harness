# BRIEF — FEAT-41 One station vocabulary

## Problem

Six places hold the names of the board's columns and nothing ties them together. `harness.json`
declares six; `gh-sync.py:104` hardcodes seven capitalised ones; `check-plan-routes.py:421` gives
`plan.yaml` a third vocabulary entirely (`pending`/`building`/`done`); `feature-schema.json`
carries a fourth as an enum. Rename a column and the harness keeps writing the old word, silently
— `check-plan-routes.py:342` already records the shape: a capital-B `Building` "would read as
not-done forever". Underneath that, `plan.yaml` — the file the whole flow reads for what is
happening — has no code writer at all. `gh-sync.py:815`'s docstring claims `start-task` records
`building` there; its body contains zero `plan.yaml` writes, so an LLM types the value by hand,
and `.omp/agents/harness-orchestrator.md:96` records five task statuses lost that way already.
Every anchor in this paragraph was re-derived at `0d4845b`.

The cost was live and is now recorded rather than observable. `check-state.sh` used to report
`VIOLATION INV-26 FEAT-40-harness-writes-done parent (issue #842): the plan derives Review — the
board reads Done`, because `ship`'s `Done` write was made in a worktree that was then deleted and
never committed. **That violation closed itself when FEAT-40 merged to `main`** — measured at
`0d4845b`, `check-state.sh` emits zero `INV-26` lines and its only violation is this feature's own
unapproved BRIEF. Merging hid the symptom; it fixed neither defect. `ship` still writes the
terminal station without committing it, and still accepts a feature directory inside a worktree
that is about to be deleted, so the next shipped feature loses its terminal record the same way.

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

- **DEC-174 BLOCKS execution — for twelve of the plan's thirteen tasks, not for all of them.**
  This work changes hooks, validators and gate scripts, so the harness may plan it but must not
  execute those changes through the enforcement path being changed. Twelve tasks are therefore
  executed by the main session directly. **The thirteenth, T-15, is on the `harness-documentor`
  team lane**: it touches exactly one file, `.harness/harness/docs/DECISIONS.md`, which is not an
  enforcement surface, and `check-domain.sh --resolve` grants that path to `harness-documentor` —
  measured, not assumed. `check-plan-routes.py` prints one ordinary team line for the whole plan,
  `OK T-15 granted to harness-documentor`. **An earlier version of this paragraph said all
  thirteen tasks were main-session-direct and that the plan carried no team-lane task at all.**
  That was true only in the window between the removal of the old decision-record task on
  2026-08-29 and its return as T-15 on 2026-08-30, and it is corrected here rather than quietly
  restated. DEC-174's lane assignments are unchanged throughout; this is a corrected count, not a
  re-resolution. The cost of the twelve is the largest cost of the feature and it is accepted,
  not worked around.
- **DEC-203 section 6 SUPPLIES the six values and BLOCKS their casing.** It states one lifecycle
  field whose values are case sensitive byte for byte, in `feature.json`. REQ-02 and REQ-06
  contradict that clause. **The contradiction IS recorded by this feature**, by T-15, as an
  amendment to the entry and not a strike — see the disclosure below. Everything else in DEC-203 — a ticket
  is open until its card reaches `Done`, the harness writes `Done` at ship, the parent rule, the
  seven-purpose read-back bound — is untouched and still binds.
- **DEC-191 BLOCKS deleting a key silently.** `feature.json`'s key set is closed with
  `additionalProperties: false` and `status` is one of its eight required keys, so REQ-06 moves
  the schema; the decision entry **is** corrected alongside it, by T-15 — see the disclosure
  below. The closed key set itself is untouched: it goes from eight required to seven.
- **DEC-182 SUPPLIES `plan.yaml`** and currently states that `plan.yaml` is deliberately excluded
  from the shape gate (`check-domain.sh:1040-1046`, re-derived at `0d4845b`; the comment sat at
  `:1011-1017` before the rebase). REQ-05 reverses that clause, and the reversal **is** recorded
  in the entry, by T-15 — see the disclosure below. The entry ruled out a budget check and a parse
  check, the two things it considered; a write DENIAL is a third thing it did not, so the
  amendment narrows the clause rather than contradicting the argument behind it.
- **A DISCLOSURE, NARROWED ON 2026-08-30 AND NOT DELETED.** The three clause corrections above
  were to be recorded inside this feature; were deferred on 2026-08-29 when the operator declined
  the recording task's external dependency; and are now recorded inside this feature again, by
  **T-15** on the `harness-documentor` lane. What dissolved the dependency was not a new decision
  but a reading of an existing one: DEC-188 at `DECISIONS.md:5945-5947` already prescribes
  **amendment** for anything "merely dated, narrowed, or partly overtaken" and requires the
  operator's word before a strike, which settles the strike-versus-subsume question the deferral
  was waiting on. **So the sentence this bullet used to carry — that the feature lands changes
  contradicting three clauses without recording the contradiction anywhere — is no longer true,
  and it is corrected here rather than quietly removed.** DEC-188's own enforcement is "a human
  reading a diff", and it holds "only while the striking actually happens every time"; the diff a
  human reads is this feature's, which is the argument for recording now rather than later.
  **What remains deferred is narrower, and is stated plainly because you sign against this
  document:** the **new station-vocabulary decision entry** is still not written by this feature.
  Its content points are fixed and preserved in `plan.yaml`'s D-09 so the triage inherits them
  rather than re-deriving them. That residual is carried as **PB-04**, now narrowed to the new
  entry alone.
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
  `_STATION_KEYS` no longer exists anywhere in the tracked tree. Graded with
  `--exclude-dir=__pycache__`: measured at `0d4845b`,
  `__pycache__/factory_config.cpython-314.pyc` carries the name as a compiled code-object
  constant, and a gitignored build artifact is not the tree this criterion is about.
  verify: automated        evidence: unit
- SC-02: No capitalised station name survives as a **quoted literal** in non-test source. The
  observation: `grep -rnE "[\"'](Backlog|Plan|Ready|Building|Review|Done)[\"']"` over
  `.claude/skills/harness/bin/*.py` and `*.sh`, excluding `test-*`, returns **zero** lines,
  including in comments and docstrings. The grep is quoted-literal, not bare-word, because the
  bare-word form — `grep -rnE "\b(Backlog|Plan|Ready|Building|Review|Done)\b"` over the same two
  globs but WITHOUT the `test-` exclusion — returns 756 lines at `0d4845b`, almost all of it
  English prose, and can therefore never reach zero. It read 746 at `ee66ae2`; the growth is test
  files, which is why the invocation is written out here rather than left to be re-guessed.
  Discriminating today: RE-MEASURED at `0d4845b` by
  running the criterion's own grep, it returns **27 lines across 5 files** — `check-state.sh` 11,
  `gh-sync.py` 9, `board_lifecycle.py` 3, `check-plan-routes.py` 3, `worktree_terminal.py` 1,
  which sums to the total, IDENTICAL line-for-line to the `ee66ae2` reading even though four of
  those five files changed in the rebase — and this feature repoints every one of them. Both the
  earlier totals
  (31, then 26) and the earlier per-file split were hand-carried rather than read off the command;
  these two numbers come from its output. `factory_config.station_column` produces the six column names with `.capitalize()` and so
  holds no literal of its own.
  verify: automated        evidence: unit
- SC-03: A `plan.yaml` task status or feature station outside the vocabulary is refused by the
  writer with a non-zero exit naming the value, and reported by `check-plan-routes.py` as a
  violation. No live `plan.yaml` carries a **task** status of `pending` afterwards — the
  four-space-anchored assertion T-04's verify runs,
  `python3 -c "import glob,re;bad=[(p,i+1) for p in sorted(glob.glob('.harness/harness/features/*/plan.yaml')) for i,l in enumerate(open(p)) if re.match(r'^    status: pending\s*$',l)];assert not bad,bad"`,
  exits 0. Anchored, not bare: RE-MEASURED at `0d4845b` the bare grep returns 74 hits and the
  anchored assertion finds 56 — it was 72 and 55 at `ee66ae2` — and three of the 18-hit difference are `approval:` blocks at two-space indent
  (`FEAT-19/plan.yaml:5`, `FEAT-28/plan.yaml:5`, and this feature's own `plan.yaml:7`, all three
  re-confirmed at `0d4845b`) which the
  work is forbidden to touch. A bare grep therefore can never reach zero. It is a Python
  assertion and not `grep ... ; test $? -eq 1` for a second reason measured at `0d4845b`: nine of
  the forty feature directories carry no `plan.yaml`, and a shell that expands the glob to its
  non-existent members makes `grep` exit 2 whether or not it matched, so the shell form can never
  pass either.
  verify: automated        evidence: integration
- SC-04: Changing one task's station in `plan.yaml` changes the card the projection function
  would write, and `gh_board.set_station` has **exactly one policy site** — one call that decides
  a station — outside tests. Two non-policy callers survive by design and are named here so the
  count is falsifiable: `board-station.py:153`, the operator's manual override, and
  `board_lifecycle.py:1016` and `:1019` inside `_apply_fix`, which applies a finding `reconcile`
  already made — both re-derived at `0d4845b`, where they sat at `:1013` and `:1016` at `ee66ae2`.
  So the whole-tree count of `gh_board.set_station(` outside tests is **four** after
  the work and **ten** at `0d4845b`, re-measured and unchanged by the rebase. More than four means a policy site survived; fewer means a
  disclosed residual was removed without a decision.
  verify: automated        evidence: unit
- SC-05: **STRUCK on 2026-08-30 with T-13**, and recorded rather than deleted (PRINCIPLES rule
  15). It required the `plan.yaml` write denial to name the writer by its POST-RENAME basename,
  which T-09 forbids in capitals — the basename in that message must be the one on disk when T-09
  runs. So the criterion was unmeetable for the whole plan and became meetable only at a task that
  no longer exists. Three independent readers converged on striking it rather than rewording it,
  and striking it is what dissolves the contradiction instead of answering it.
  **A COVERAGE LOSS COMES WITH IT AND IS NOT SOFTENED HERE.** SC-05 also carried the only
  criterion-level assertion that the denial STATES THE REASON rather than merely the verb, for a
  payload with an `agent_type` and for one without. Nothing replaces that. It survives only as
  T-09's own `verify:` and the load-bearing instruction in T-09's intent, neither of which is a
  success criterion. Carried as **PB-07**.
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
  carries a top-level `status: done`, and a full run of `check-state.sh` reports no `INV-26` line
  for **any** feature. **This criterion was re-based at `0d4845b` and the original is recorded
  rather than rewritten away.** It used to demand that the live `INV-26` violation naming FEAT-40
  and issue #842 be closed by this feature, and to demonstrate the failing state by reproducing
  that violation. FEAT-40 has since merged to `main`, and the violation closed itself: measured at
  `0d4845b`, FEAT-40's `feature.json` reads `Done`, `check-plan-routes.py` skips it as shipped, and
  `check-state.sh` emits zero `INV-26` lines. Demanding its closure would now be true by
  construction. What remains is falsifiable and is the half of REQ-07 the merge did not deliver:
  measured at `0d4845b`, FEAT-40's `plan.yaml` carries **no** top-level `status` key at all, so the
  first clause fails before the work and is discharged by T-07's migration, not by T-10. The
  `INV-26` clause is retained as a regression bound on that migration and on T-10's board pass — a
  new `INV-26` line means something was moved wrong — not as a defect to close.
  verify: inspection
- SC-10: `gh-sync.py ship` refuses a feature directory inside `.claude/worktrees/`, naming the
  main-checkout path instead, and on the success path the terminal station write is committed —
  a test asserts the file is clean against `HEAD` after `ship` returns.
  verify: automated        evidence: integration
- SC-11: The whole suite is green and `check-plan-routes.py` exits 0 over every live plan,
  including this one.
  verify: automated        evidence: integration
- SC-12: **STRUCK on 2026-08-30 with T-13**, exactly as its own last sentence pre-authorized —
  "If the rename task is struck at approval, this criterion is struck with it." It existed only to
  verify the rename. Recorded rather than deleted, and **no coverage is lost**: every behaviour it
  touched belongs to T-03, which keeps the writer's existing name throughout, and D-01 records the
  reversal.
- SC-14: `DECISIONS.md` carries exactly three amendment records naming
  `FEAT-41-one-station-vocabulary` — one inside `DEC-182`, one inside `DEC-191` and one inside
  `DEC-203` — and each of the three amended clauses is **still standing**, none struck. Graded by
  T-15's own verify, which splits the file into entries on `^## DEC-`, counts the marker per
  entry, and asserts all three original clauses are still present. It exits 1 today, where the
  marker count is zero, so the criterion can fail. The entries are AMENDED and never struck:
  DEC-188 at `DECISIONS.md:5945-5947` reserves striking for a flat contradiction and requires the
  operator's word first, and all three of these are narrowings.
  verify: automated        evidence: unit
- SC-13: `check-state.sh`'s INV-26 takes its expected station from the same function that writes
  it, and a station it cannot map is loud. Observations, both required: `grep -n "_EXPECT"
  .claude/skills/harness/bin/check-state.sh` returns nothing, and a fixture plan carrying a task
  station outside the vocabulary makes INV-26 emit a violation line naming the feature, the task
  id and the value — where at `0d4845b` the same fixture is silently skipped by the
  `if _want is None: continue` at circa `:1501`, re-derived from `:1476` at `ee66ae2`. The failing state is demonstrated first.
  verify: automated        evidence: integration

## Verification gaps

- `component`, `ui`, `eval` and `typecheck` carry `cmd: null` in `.harness/harness.json`. None of
  them detects a file this feature touches, so no criterion above rests on a null runner.
- `test-gh-sync.py` is measured at **149 s** and is run in full by THREE tasks — T-06, T-07 and
  T-10, counted off the plan's own `verify:` blocks at `0d4845b` — about **447 s** across the plan,
  against a 60-second guideline per verify. The figure recorded before this audit was two tasks and
  298 s and it undercounted T-07, whose verify has always run the file. Nothing is unproven by
  this — the tests do run — but the plan pays roughly seven and a half minutes for it. Narrowing any
  of the three verifies
  would remove the only proof that task has, so it is accepted here and carried as **PB-01**
  below, which is what makes the cost temporary rather than permanent.

## Proposed backlog

Proposed only. These become GitHub issues when the main session accepts the ship — not during the
build, and not opened by an agent. The row exists so a deferral has an instrument instead of
living in prose that nothing ever reads again.

- **PB-01 — case selection for `run-unit-tests.sh`.** Let a `verify:` name the cases it needs
  instead of running a whole test file. `test-gh-sync.py` costs 149 s and this plan runs it in
  full three times (T-06, T-07 and T-10), about 447 s, against a 60-second-per-verify guideline.
  Recovers roughly 300 s on a plan of this shape and takes future verifies back under the guideline.
  Deferred out of FEAT-41 because it edits the test harness — whose KIND CROSS-CHECK this feature
  already touches at T-08 — and changing the harness inside a feature that is rewriting
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
- **PB-04 — open the new station-vocabulary decision entry.** **NARROWED on 2026-08-30.** This
  row used to carry two things: the three clause corrections AND a new entry. The three clause
  corrections came back into the feature as **T-15** once DEC-188 was read as settling the
  strike-versus-subsume question, so only the new entry is still deferred. Its content points are
  fixed and preserved in `plan.yaml`'s D-09, so this row is a recording job, not a fresh
  derivation. Deferred because opening a new top-level entry is decisions-authority work this
  feature was stripped of on 2026-08-29 and has not been given back. Recovers a `DECISIONS.md`
  that states the station vocabulary positively, rather than only as three amendments to entries
  that predate it.
- **PB-05 — rename the plan writer, if it is still worth doing.** T-13 would have renamed the tool
  to say "write" rather than "merge", because after T-03 it owns five verbs of which merge is one.
  **It is not happening in this feature**: struck on 2026-08-30 because it is a 35-line rename
  across 13 files that must be hand-built under DEC-174, it changes no behaviour, and its file
  list reached `.harness/harness/docs/DECISIONS.md` — a surface this feature lost standing over.
  SC-05 and SC-12 were struck with it and D-01 records the reversal. Recovers a tool whose name
  describes what it does; costs a rename with no behavioural gate behind it, which is why it lost
  to everything else in the plan.
- **PB-06 — move the task-to-issue map into `plan.yaml`.** The grilling settled this and this
  feature does **not** close it. Verbatim, at
  `.harness/notes/grilling-845-one-vocabulary-2026-08-25.md:27-28`: "**The task-to-issue map moves
  into `plan.yaml`.** Today the key and the value live in different files." No task in this plan
  moves it, and T-06's own specification is the evidence that the split survives the feature
  intact — `rec["issues"]` maps task id to sub-issue number and is read from
  `gh-sync.load_recorded`, which parses the `github:` block of `feature.json`, while the task id
  it keys on lives in `plan.yaml`. **This is untouched, not partially addressed.** Deferred
  because it is grilling-settled intent rather than anything issue #845 or #867 asks for, and
  because a further hand-built task under DEC-174 buys less than an honest record does. Recovers
  the last place where one fact is split across two files.
- **PB-07 — restore a success criterion over the `plan.yaml` write-denial message.** SC-05 was
  struck with T-13 on 2026-08-30 because it named the post-rename basename, and it carried the
  only criterion-level assertion that the denial states the REASON the old route closed, not
  merely the verb to use instead, for a payload with an `agent_type` and for one without.
  Nothing replaces it: the requirement now rests on T-09's `verify:` and on the intent text that
  calls the reason clause load-bearing, neither of which is a criterion. Deferred rather than
  fixed in place because rewording a criterion at the same moment its task is struck is how the
  original contradiction got in. Recovers criterion-level cover for the one message an agent
  actually reads when the write route closes underneath it.

## Approval

status: pending
approved-by: none
date: none

Returned to pending on 2026-08-30. Striking T-13 is a scope change to a signed brief, so the
2026-08-29 signature does not survive it; it stands in the record and is not rewritten. What
changed since it: SC-05 and SC-12 struck, SC-14 added, the lane paragraph corrected, the
`DECISIONS.md` disclosure narrowed because T-15 now records the three clause amendments, PB-04
narrowed and PB-05, PB-06 and PB-07 opened. Scope is unchanged and whole — all twelve surviving
tasks stay and both source tickets are closed by this feature.
