# BRIEF — BUG-1507-ready-station-signature

## Problem

Two of the six mandated stations are written by nothing. The `/harness-plan` mission tells the
operator to run `gh-sync.py status <feature-dir> Ready` right after the signature
(`.claude/commands/harness-plan.md:24`), and `gh-sync.py` refuses a capitalized station before any
write (`gh-sync.py:1324-1325`; the lowercase CLI contract is stated in that file's own comment at
`:114-117`, FEAT-41 D-14). The same file's KICKOFF step, one line group above, tells the operator to
run `board-station.py <issue-number> Plan` — measured at 4b5dbb23: exit 2,
`board-station: 'Plan' is not a station`. `references/github-mirror.md` teaches the same refused
spellings in three places (`:94`, `:96`, and the post-table prose at `:55-56`) while its own
"a phase transition happens" row at `:44` already says lowercase, so the reference contradicts
itself. Separately, nothing anywhere instructs anyone to advance a feature's OWN station to
`building`: `SKILL.md`'s build phase (`:136-159`) names no such write, and `gh-sync.py start-task`
writes task stations only. Net, measured against the plan corpus: every feature's station history
reads `plan -> review -> done`. The operator cannot see "signed, not started" or "being built" from
either the board or the plan, and `factory_claim.py`'s poll of the ready column has nothing to find.

## Goal

Make the instructions the harness actually follows produce the two stations the harness already
enforces. After this, following the documented plan mission verbatim moves the source ticket to Plan
at kickoff and the task sub-issues to Ready at the signature, the orchestrator records the feature's
own station as `building` when it starts dispatching build work, and the written contract states
what `gh-sync.py status <dir> building` does instead of leaving it to fallthrough. No new station
names, no schema change, no station-enum work.

## Requirements

- REQ-01: Following the documented plan-mission steps verbatim performs the board writes they
  promise — the kickoff Plan write and the post-signature Ready write both succeed instead of being
  refused by the tool.
- REQ-02: A feature's own plan record advances to the building station when build dispatch begins,
  so the plan alone shows a feature is being built.
- REQ-03: The written contract states what `gh-sync.py status <dir> building` does to the board, so
  the behaviour is a stated decision rather than an unremarked fallthrough.
- REQ-04: The reference that says who writes each station names the writer that actually writes the
  feature-level building station.
- REQ-05: Reintroducing a capitalized station argument into an instruction file fails a test rather
  than shipping silently.
- REQ-06: The station vocabulary, the plan schema, and `gh-sync.py`'s observable behaviour are
  unchanged by this fix.

## Constraints

- **Scope, from the issue (BLOCKS):** production surfaces are instruction and documentation text
  only — no station-enum work, no schema change, no new station names, no change to the frozen six.
- **The DoD's "no extra manual command needed" is read as reading (a)** (plan D-01): the documented
  signature STEP already contains the `gh-sync.py status` call, so fixing its spelling satisfies the
  bullet. `sign-approval` is NOT changed to trigger a board write — that is a code change to the
  signature path and the issue's scope line excludes it. If the operator wants reading (b), this
  brief is the wrong shape and needs re-scoping before signature.
- **DEC-203 SUPPLIES** the authority this fix leans on: `plan.yaml`'s top-level `status` is the
  record of a feature's station.
- **FEAT-41 / D-14 SUPPLIES** the lowercase CLI contract (`gh-sync.py:114-117`). This feature
  completes a migration that decision already designed and that missed two files.
- **`plan-merge.py`'s verbs SUPPLY** the only write route to `plan.yaml`; the `building` instruction
  is spelled `plan-merge.py set-feature-station --station building`, matching `SKILL.md` segment 4's
  existing style for `review`.
- `.agents/skills` is a symlink to `../.claude/skills` and only the `.claude/...` paths are tracked.
  Every path in this feature is spelled `.claude/...`.
- **Disclosed scope addition, strikeable at signature:** `harness-plan.md:11`'s
  `board-station.py <issue-number> Plan` is the same defect one line group above the enumerated one
  and is measured dead (exit 2 at 4b5dbb23). The issue does not enumerate it. It is included, under
  REQ-01. Striking it costs three things, not two: SC-02 and SC-03 cannot go green as scoped,
  because that occurrence sits inside the swept scope; and **T-01's own `verify:` cannot go green
  either** — it requires both station arguments in `harness-plan.md` to be lowercase
  (`len(m)==2 and all lower`), so leaving `Plan` at line 11 makes the task red by its own gate. A
  strike therefore also means rewriting T-01's `verify:` to assert one argument instead of two.
- **Disclosed limit — what this fix does NOT deliver, and it is half of a Definition-of-Done
  bullet.** The DoD asks that a card at Ready always means signed, and that nothing else puts one
  there. This fix delivers that for the **parent** card only: `derive_station` never returns `ready`
  for a parent (`gh_board.py:120-124`, verified at 4b5dbb23), so no reconcile can park a parent at
  Ready. It does **not** deliver it for **task** cards: `gh_board._task_statuses` reads a task
  status that is absent, or already `ready`, as `ready` (`gh_board.py:192-202`), and `project()`
  places those cards, so an ordinary reconcile (`board_lifecycle.py:1080-1083`) can put a task card
  at Ready with no signature anywhere in the picture. Closing that half is **code work** —
  station-derivation logic in `gh_board.py` — and the issue's scope line for this ticket is
  "documentation/instruction only, no station enum work, no schema change", which excludes it. So
  it is disclosed here rather than silently omitted: **if you want the task-card half closed too,
  widen the scope at signature** and this brief needs a further REQ and a code task.

## Success Criteria

- SC-01: Following `/harness-plan`'s documented signature step verbatim performs the ready write on
  this feature AND the recorded task cards are then seen at Ready. The actor is the **main session**,
  itself, immediately after it writes the signature; pm grades this criterion at the goal-check from
  the transcript the main session records under `notes/`. Three observations, all required:
  (a) `gh-sync.py status <feature-dir> ready` exits 0 and prints
  `gh-sync: plan.yaml station -> ready`; (b) this feature's `plan.yaml` then reads `status: ready`;
  (c) the T-NN sub-issue cards recorded for this feature are observed **in the board's Ready
  column**, listed by number in the transcript. Exit 0 does not discharge (c): with no recorded
  sub-issues the ready branch prints `no sub-issues recorded, nothing to move` and still returns 0
  (`gh-sync.py:1353-1356`), and at 4b5dbb23 this feature's `feature.json` carries no `github` key at
  all. **In that zero-recorded case the criterion is never graded `met`:** the transcript must state
  "zero sub-issues recorded, zero cards moved" and the verdict is `partial`, carrying (a) and (b)
  only. Authoritative copy for the step being followed is the **worktree's**
  `.claude/commands/harness-plan.md` (T-01's output); the control-plane checkout's copy still reads
  `Ready` until this branch merges, so on this build the main session performs the step **by hand
  from the worktree file** rather than from the command it loaded. Graded POST-SIGNATURE, on this
  feature's own run.
  verify: inspection
- SC-02: Every station argument in the instruction scope — `.claude/commands/*.md` and
  `.claude/skills/**/*.md`, read with whitespace collapsed so a line-wrapped command is still seen —
  names a station the invoked tool accepts, checked against `factory_config.MANDATED_STATIONS` (plus
  the terminal marker for `gh-sync.py status`) rather than a spelled-out list. The sweep must find at
  least the six occurrences measured at 4b5dbb23 and must name `harness-plan.md`, `github-mirror.md`
  and `SKILL.md` among the files it saw, so an empty or narrowed sweep cannot pass.
  verify: automated      evidence: integration
- SC-03: The sweep reddens when a capital is reintroduced. The permanent proof is a negative control
  in the suite: it copies the instruction files into a scratch root, restores one capitalized
  argument, runs the sweep against that root, and requires the sweep to report that occurrence as an
  offender by path, tool and token — with an unmutated copy of the same root reporting no offender
  as the anti-false-red control. **How the sweep is invoked against the scratch root is the
  implementation's choice**: nothing here mandates a subprocess, and nothing here mandates an
  environment variable that repoints the sweep's scope (BUG-1507 plan panel cycle 0, finding
  `PF-4d48a7518cc7333294cad13b27fdaed6` — a scope override read at import time makes the positive
  controls conditional).
  verify: automated      evidence: integration
- SC-04: `SKILL.md`'s build phase instructs the orchestrator to record the feature's station as
  `building` with `plan-merge.py set-feature-station --station building` when the eng segment starts
  dispatching, read at `git show <review_sha>:.claude/skills/harness/SKILL.md`.
  verify: inspection
- SC-05: This feature's own `plan.yaml` reads `status: building` once its build dispatch begins. The
  actor is the **orchestrator**, itself, at the moment the eng segment starts dispatching: it runs
  `plan-merge.py set-feature-station --station building` on this feature's `plan.yaml` and records
  the observed `status:` line under `notes/`; pm grades the criterion from that record at the
  goal-check. Authoritative copy of the instruction being followed is the **worktree's**
  `.claude/skills/harness/SKILL.md` (T-03's output), read at
  `git show <review_sha>:.claude/skills/harness/SKILL.md`. The orchestrator's own loaded `SKILL.md`
  comes from the control-plane checkout and does not carry T-03's instruction until this branch
  merges, so on **this** build the write is performed **by hand from the worktree copy** — this
  feature cannot demonstrate the instruction being obeyed automatically, only the station being
  recorded. Graded POST-SIGNATURE.
  verify: inspection
- SC-06: `github-mirror.md`'s "who writes each station" Building row names the feature-station
  writer alongside `start-task`, and says which of the two writes the card and which writes the plan,
  read at `git show <review_sha>:.claude/skills/harness/references/github-mirror.md`.
  verify: inspection
- SC-07: `cmd_status`'s docstring STATION WRITES list carries a Building entry stating that the plan
  station is recorded and no card is written, read at `git show <review_sha>:.claude/skills/harness/bin/gh-sync.py`.
  verify: inspection
- SC-08: `gh-sync.py`'s executable lines are untouched:
  `git diff 4b5dbb23 <review_sha> -- .claude/skills/harness/bin/gh-sync.py` shows changes confined to
  the `cmd_status` docstring, and both the early-return tuple line
  (`if board is None or station in ("plan", "done", factory_config.TERMINAL_MARKER):`) and the ready
  approval refusal at `:1327-1331` are byte-identical.
  verify: inspection
- SC-09: `tests/integration/test-gh-sync.py` and `tests/integration/test-board-station.py` both still
  pass at `review_sha`.
  verify: automated      evidence: integration
- SC-10: No station vocabulary or schema change:
  `git diff 4b5dbb23 <review_sha> -- .claude/skills/harness/bin/factory_config.py .harness/harness.json .claude/skills/harness/bin/plan-merge.py .claude/skills/harness/bin/gh_board.py`
  is empty.
  verify: inspection

## Verification notes and gaps

- **The DoD's grep bullet is SC-01 plus SC-05, and nothing more.** `plan.yaml` records only the
  CURRENT station; the history lives in `STATE.md` log entries. So "grep the corpus and see
  `status: ready` and `status: building`" is two moment-in-time observations on this feature — one
  immediately after its signature, one immediately after its build dispatch begins — not a standing
  property of the corpus. Both are recorded under `notes/` as they happen. An SC asserting the corpus
  holds both stations at once is unmeetable by construction and is deliberately not written.
- **SC-01 and SC-05 are graded post-signature and by no task deliverable.** The `ready` write is
  performed by the main session after it signs; the `building` write by the orchestrator at build
  start. The deliverable is the instruction; the evidence is what this feature's own run does with
  it. Each criterion now names its own actor and says which COPY of the instruction file that actor
  follows — on this build, the worktree copy, by hand, because neither actor's loaded copy carries
  the fix until merge. pm grades both at the goal-check from the recorded transcripts.
- **Why the doc tasks are typed `bugfix` and how the matrix is satisfied.** `harness.json`'s
  `test_matrix` maps `bugfix` with `fix_confined_to_tests_and_contract_docs` to `integration`. T-01
  and T-02 change tokens that a tool validates, so a machine-checkable contract exists and T-05's
  witness is that integration evidence. T-03 and T-04 are typed `docs` (matrix: nothing required)
  because no machine contract exists for them — a test asserting their wording would pin source text,
  which is not a contract, so they are graded by inspection instead.
- **No criterion rests on a null-runner kind.** `integration` is active
  (`.claude/skills/harness/bin/run-unit-tests.sh --kind integration`) and its detect glob
  `tests/integration/**` matches the file T-05 adds. `component`, `ui`, `typecheck` and `eval` are
  null or excluded here and no criterion touches them.
- **Residual, stated rather than hidden:** nothing proves the orchestrator OBEYS the new `building`
  instruction on a later feature. SC-05 grades one feature's own run; a standing gate would have to
  read a feature's station history against its dispatch record, which does not exist and is not
  built here.
- **The witness's scope is deliberately narrow** (plan D-05): `.claude/commands/*.md` and
  `.claude/skills/**/*.md` only. `gh-sync.py:116` quotes the old capitalized spelling as history and
  `.harness/harness/features/**` are immutable records — widening the sweep would redden on text that
  must not change.
- **The pre-fix demonstration is a one-off, deliberately not an assertion.** Running the sweep
  against `git show 4b5dbb23:<path>` copies of the two files is real red evidence and T-05 requires
  it in the doer's receipt, but it stays out of the suite: `tests.yml` checks out shallow, so a
  pinned historical sha is unreachable in CI and a permanent assertion on it would be unmeetable
  there.
- **The witness task is a judgement, visible here so it can be struck.** FEAT-41 / D-14 fixed this
  capitalization class once and it regressed into these two files, and the issue's scope line says
  "documentation/instruction only". T-05 is included (plan D-03) on the reading that the scope line
  bounds PRODUCTION surfaces and that `bugfix` + `fix_confined_to_tests_and_contract_docs` already
  obliges an `integration` test — so the witness is the matrix's own requirement, not added scope.
  Strike T-05 at signature and four things go with it, not three: SC-02, SC-03 and REQ-05, and the
  `integration` evidence the test matrix demands of T-01, T-02 and T-05 themselves, all three of
  which are typed `bugfix`. With T-05 struck, three `bugfix` tasks would carry no matrix evidence at
  all and the qa gate should FAIL the feature. So a strike is only executable together with its
  remedy: **retype T-01 and T-02 as `docs`** (the matrix requires nothing of `docs`, and they are
  graded by inspection like T-03 and T-04). Struck and retyped, the fix is protected by nothing but
  the next reader's memory.
- **Verified at draft time, at 4b5dbb23:** every task's `verify:` command was run against the
  unbuilt tree and each exits non-zero for its own reason, and T-01 through T-04 were each run
  against a scratch copy carrying the intended fix and each exits 0. T-04's `verify:` also reddens
  if `building` is added to the early-return tuple, which is what pins plan D-02.

## Approval

status: pending
approved-by:
date:
