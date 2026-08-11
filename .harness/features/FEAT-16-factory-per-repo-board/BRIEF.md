# BRIEF — FEAT-16 Factory per-repo board

## Problem

A factory run against `mruangutai/kaya-ai` reads the wrong board and finds nothing. The fleet
declares one board for the whole fleet (`.harness/factory/fleet.yaml` `board.number: 3`), board 3
is *Harness*, and the fleet's only repository is kaya-ai, whose 211 issues live on board 2. DEC-174
am.1 removed `mruangutai/harness` from `repos:` and left the station board pointing at a repository
the fleet no longer contains; that amendment records the gap as owed and not deferrable. Factory
runs against kaya-ai are the stated primary use case, and that is the run that fails today.

The defect is not the number 3. It is the assumption that one board serves every member: retargeting
`board.number` to 2 fixes kaya and re-opens the same hole the moment a second product repository
joins.

## Goal

The fleet stops assuming one board. Each repository the fleet declares carries its own board —
number, station field and station names together — so a factory run against any declared repository
reads that repository's own board, moves its station there, and the move is verified on that board.
Kaya's board already carries the factory's vocabulary — the six station names, applied by the
operator on 2026-08-11 without relabelling a single finished issue — and this feature confirms that
state rather than creating it, then teaches the fleet and every reader to address it per repository.

## Requirements

- REQ-01: A factory run against a repository the fleet declares reads and writes that repository's
  own station board.
- REQ-02: Every repository the fleet declares carries its own board declaration. No repository
  inherits a board from the fleet or from another repository.
- REQ-03: A fleet declaration in which a repository carries no board is rejected when the fleet is
  loaded, naming the repository, rather than falling back to a shared board.
- REQ-04: Kaya's board offers the three factory stations, and every issue already finished on it
  keeps its finished status.
- REQ-05: The test suite asserts which board each declared repository is paired with, so the two
  cannot drift apart without a test failing.
- REQ-06: The decision record no longer describes the fleet's board as a single shared block or the
  DEC-174 am.1 board loose end as open.

There is deliberately no requirement of the form "a live run moves a station on kaya's board". That
is REQ-01 observed on the live system, and it is carried by SC-06 (`verify: uat`) rather than by a
second requirement no task can serve.

## Success Criteria

- SC-01: `load_fleet` accepts a fleet whose every `repos:` entry carries its own `board:` block with
  `number`, `station_field` and `stations`, and rejects a fleet in which any entry has none, with an
  error naming that repository.
  verify: automated      evidence: unit
- SC-02: `load_fleet` rejects a fleet that carries a top-level `board:` key, with an error that names
  `board` and says to move it under each `repos:` entry. A pre-change fleet file therefore fails
  loudly instead of being silently ignored.
  verify: automated      evidence: unit
- SC-03: At T-07's capture — taken when the board precondition is confirmed and before any live
  factory run (`notes/board2-capture.md`) — `mruangutai` project 2 reports 118 items in `Done` and 0
  items in `Review`, and its `Status` field still offers option ids `f75ad846`, `47fc9ee4` and
  `98236657`. Those three ids are **history**: they were measured on board 2 at sha `d97f5ea` on
  2026-08-11, when the board offered three options named `Todo`, `In Progress` and `Done` and the
  item distribution was 118 `Done`, 82 `Todo`, 11 `In Progress`. Re-measured on 2026-08-11 by
  `gh api graphql` over `projectV2(number:2){field(name:"Status"){options{name id}}}`, all three
  survive under new names — `f75ad846` is now `Backlog`, `47fc9ee4` is now `Building`, `98236657` is
  still `Done` — which is exactly what proves the change was a rename and not a delete-and-recreate,
  and that no item was moved. The id anchor is **within board 2, across time**, and is never used to
  compare board 2 with board 3 (see SC-07). Any item whose status changes after that capture,
  including the issue SC-06's live run moves, is outside this criterion.
  verify: inspection
- SC-04: With a fleet declaring two repositories on two different boards, `factory_claim`,
  `factory_decompose` and `factory_land` each address the board of the repository being acted on:
  the recorded gh calls carry that repository's board number and its own station option names, and
  no gh call names the other repository's board.
  verify: automated      evidence: unit
- SC-05: The suite asserts the declared pairing between each fleet repository and its board number,
  including that `mruangutai/kaya-ai` is paired with board 2, and fails if either side is changed
  alone.
  verify: automated      evidence: unit
- SC-06: A live factory claim run against a kaya-ai issue that is **not one of the 118 items sitting
  in `Done`** — the run moves a station, so it must not touch a finished issue — moves that issue's
  `Status` on project 2 from `Ready` to `Building`, and the new value is read back with a board query
  rather than inferred from the tool's exit code. The run's issue may finish at any station, `Review`
  included, and its status is outside SC-03.
  verify: uat
- SC-07: Board 2's `Status` field offers exactly six options, **by name and in this order**:
  `Backlog`, `Plan`, `Ready`, `Building`, `Review`, `Done` — no seventh, and board 3 offers the same
  six names in the same order. Order is part of the assertion, so the check must not sort: sorted
  output is `Backlog,Building,Done,Plan,Ready,Review`, a different string that would pass while the
  pipeline was scrambled. The cross-board half of this criterion compares **names only, never option
  ids** — `Backlog`, `Building` and `Done` carry identical ids on both boards because they are
  GitHub's default template ids, so an id-based cross-board check is vacuous. Measured on 2026-08-11
  by `gh api graphql` on each project's `Status` field; T-07's verify runs the same assertion through
  `gh project field-list`, whose actual output for either board is
  `Backlog,Plan,Ready,Building,Review,Done,` (trailing comma from `tr`, run and pasted, not
  constructed).
  verify: inspection
- SC-08: `.claude/skills/harness/bin/run-unit-tests.sh --kind unit` exits 0 on the finished feature.
  verify: automated      evidence: unit
- SC-09: `.claude/skills/harness/bin/run-unit-tests.sh --kind integration` exits 0 on the finished
  feature.
  verify: automated      evidence: integration
- SC-10: The feature's diff changes none of the four DEC-174 carve-out scripts. Mechanically:
  `git diff --name-only a29ad06..HEAD` intersected with `check-domain.sh`, `bash-write-guard.sh`,
  `validate-digest.py` and `check-state.sh` (all under `.claude/skills/harness/bin/`) is empty.
  Base `a29ad06` is HEAD at plan time, at which `git status --porcelain` reports all four clean —
  so a non-empty intersection is this feature's doing and nobody else's.
  verify: inspection
- SC-11: No file under `.claude/skills/harness/bin/` indexes a fleet-level board — source, comment
  or fixture — and `factory_config.station` no longer exists. Mechanically, both of these return
  nothing:
  `grep -rnE "fleet[A-Za-z_]*\[['\"]board['\"]\]|fleet[A-Za-z_]*\.get\(['\"]board['\"]\)"` over that
  directory, and `grep -n 'def station(' .claude/skills/harness/bin/factory_config.py`. The first
  pattern matches **18 lines across 7 files** at `a29ad06` (`factory_claim.py`,
  `factory_decompose.py`, `factory_land.py`, `factory_config.py`, `test-factory-config.py`,
  `test-factory-decompose.py`, `test-factory-integration.py`), and matches none of the
  post-migration idioms — `entry["board"]`, `fleet["repos"][0]["board"]`, `board_for(...)` — so it
  is both discriminating and satisfiable.
  verify: inspection
- SC-12: The record no longer states what this feature falsifies. All four hold: `DECISIONS.md`
  carries a second DEC-174 amendment, headed in that entry's own style so the heading contains the
  literal string `DEC-174 amendment 2` (`grep -c "DEC-174 amendment 2"` is 0 at `a29ad06`);
  `DECISIONS.md` carries a DEC-186 amendment restating the read-back cost model as one ready-station
  query `per repository served` (that phrase is 0 at `a29ad06`, and it is what proves the amendment
  itself landed rather than only its index row); the `DEC-174` row **and** the `DEC-186` row of
  `DECISIONS-INDEX.md` each carry the phrase `per-repository board`, grepped per row rather than
  counted file-wide (0 at `a29ad06`); and `SPEC.md` no longer lists
  `factory_config` as exposing `station` nor describes `fleet.yaml` as carrying "the `board:` the
  factory reads work from" (each matches once at `a29ad06`). DEC-186's ORIGINAL "one Projects v2
  board" sentence stays standing — amendments append and supersede, they never rewrite — so its
  absence is deliberately not asserted.
  verify: inspection
- SC-13: A claim run scoped to a fleet repository whose `ready` station is empty **reports** that it
  found nothing rather than exiting 0 in silence. Mechanically, and this is REQ-01 observed at the
  per-repository loop T-02 introduces: with a fleet declaring two repositories on two different
  boards and `--repo` naming the one whose ready station returns no items, `factory_claim` writes
  nothing to stdout, writes `no work available` to stderr, and exits 1 (`factory_cli.EXIT_NOTHING`).
  **It is not already green.** The global case is closed — `factory_claim.py` calls
  `factory_cli.nothing_to_do` when the candidate list is empty, and `test-factory-claim.py`'s case
  labelled C1 asserts empty stdout, the message on stderr and exit 1. But C1 hands its recorder an
  empty item list for the whole run against a single-repository fixture, so it exercises only the
  global case. The mutant this criterion exists to kill is specific to the new loop: a loop that
  treats a repository with an empty `ready` as a `continue` and falls off the end of the served set
  into a normal exit 0. C1 passes on that mutant. Verified at source on 2026-08-11 by reading
  `factory_claim.py`'s `nothing_to_do` call site, `factory_cli.py`'s `EXIT_NOTHING = 1` and
  `nothing_to_do`, and C1's recorder setup.
  verify: automated      evidence: unit

## Decisions recorded here, with the reasoning

### (a) The contradiction between the 118 and the live run — resolved by pinning the measurement point

Ruling 3 asserts 0 in `Review`; ruling 4 requires a live run and `review` is a factory station. The
resolution has two independent halves, either of which alone would do:

1. **SC-03 is evaluated at a named capture** — the capture T-07 writes when it confirms the board
   precondition, before any live run. There is no board edit to take it after: the option work was
   already performed by the main session on 2026-08-11, so T-07 reads and confirms rather than
   editing. A criterion with a measurement point cannot be falsified by a later event, and the
   measurement point is now the precondition read.
2. **SC-03 carries an explicit exclusion clause** and SC-06 carries its mirror. Read literally against
   the world "the live run's issue ends in `Review`": SC-03 is about the capture, in which the live
   issue has not moved, and it excludes any item that changes afterwards — true. SC-06 asserts a
   `Ready`→`Building` read-back and explicitly permits the run to finish at `Review` — true. Both
   hold at once.

The alternative considered and rejected was scoping the assertion to "the 118 finished issues" alone.
It is jointly satisfiable too, but it loses the whole-board check: a scoped criterion says nothing
about the 82 unstarted issues, so deleting the option they sit in and creating a fresh one would
strand them with no status and pass. Pinning all three surviving option ids catches that.

**The option ids are the anti-migration anchor, and they survived the rename.** Renaming an option in
Projects v2 keeps its id; deleting and recreating one does not. Re-measured on 2026-08-11 by
`gh api graphql` on project 2's `Status` field, all three ids recorded at `d97f5ea` are still present:
`f75ad846` (then `Todo`, now `Backlog`), `47fc9ee4` (then `In Progress`, now `Building`) and
`98236657` (`Done`, unchanged). That is the positive evidence that the 2026-08-11 change was a rename
at zero item writes. The wrong implementation the operator forbade — rename all three, then migrate
118 items back into a freshly created `Done` — would have reached the same counts with a different
`Done` id, and SC-03 would fail on it. An end-state count alone could not tell the two apart.

**And the ids do exactly one job.** They anchor board 2 against its own past. They are *not* how
board 2 is compared with board 3: `Backlog`, `Building` and `Done` carry the same ids on both boards,
because those are GitHub's default template ids, so a cross-board id check passes no matter what
either board says. SC-07 therefore compares names. Two rules, adjacent in the same task, deliberately
not merged.

### (b) Neither unit of external-state work gets a task with an invented file

`files: []` is illegal (`harness_yaml.py` REQUIRED_TASK_FIELDS treats an empty list as missing, and
`check-plan-routes.py` turns the resulting PlanSchemaError into exit 2). Dropping the second capture
was therefore checked against that floor before it was made: T-07 retains `.harness/factory/fleet.yaml`
and one capture, so its `files:` holds two entries and never approaches empty. The two units are
resolved differently:

- **Board 2's option state: a PRECONDITION CHECK, folded into T-07 alongside the fleet declaration.**
  T-07 no longer edits a board. The rename was applied by the main session on 2026-08-11 and applied
  differently from what this plan originally specified — `Todo` became `Backlog`, not `Ready`, and
  both boards ended at six options, not four — so an edit task would re-do finished work and fight
  live state. What remains is a read that confirms both boards carry the six station names in order
  and stops if either disagrees, and it never edits.
  T-07's `files:` are `.harness/factory/fleet.yaml`, which it genuinely rewrites, and **one** capture
  artifact. **One, not two, and the reason changed.** The old justification — a before-capture is
  unrecoverable once an option is renamed — dies with the edit: with nothing mutating between them, a
  before-capture and an after-capture are two identical files. The single capture survives on a
  different and narrower ground: it is the named measurement point SC-03 is evaluated at, taken before
  any live factory run, and no runner anywhere in CI ever re-reads a GitHub board, so if T-07 does not
  write that reading down, nothing else ever will. The precondition, the capture and the declaration
  stay one ordered unit under one owner because the declaration must not land against a board whose
  vocabulary it does not match. (`factory_claim` does refuse on a station mismatch — true at source —
  but no factory run is a task in this plan, so that window is one nothing enters.)
- **The live factory run: no task at all — SC-06 only.** It writes nothing in this repository, it
  mutates a product repository (a git ref in `mruangutai/kaya-ai`) and a live board, and only the
  operator can consent to that. `verify: uat` is the honest method; it stays `not_met` until the user
  runs it.

### (c) The pairing assertion lives in `test-no-distribution.py`, not `check-state.sh`

`check-state.sh` is a DEC-174 carve-out file, **and** it is granted to `harness-backend-dev` and
`harness-dev-ops` by `check-domain.sh --resolve`. Declaring a task on it `main-session-direct`
therefore emits a `DEVIATION` line from `check-plan-routes.py` on every future run of a required CI
check — permanent noise that never clears — and the task cannot be done by the team at all. Against
that, `test-no-distribution.py` resolves to the same two agents on the ordinary team lane, is already
the file that asserts fleet membership (`case3_absence_harness_is_not_a_fleet_member`, DEC-174 am.1),
and runs in `UNIT_SCRIPTS`, so SC-05 gets real `unit` evidence.

Two measured facts settle the rest of the carve-out question, and both say the gate scripts are not
touched at all:

- `check-domain.sh` calls `factory_config.load_fleet` and then reads only `workspace_root` and
  `repos[].name`. It never reads `board`. The schema change does not reach its source.
- `check-state.sh`'s INV-24 reads the fleet with `harness_yaml.load_file`, not `load_fleet`, and
  reads only `repos[].name`. It is untouched, and its fixture at `test-check-state.py:836` keeps
  working.

What the schema change *does* reach is `test-check-domain.py`'s `good_repos` fixture, which must load
cleanly for case (d) to exercise the success path. **That task takes the ordinary team lane** (T-06),
because DEC-174 names four gate scripts and this task is forbidden from touching any of them: it
rewrites fleet YAML strings inside fixtures and changes no assertion, no expected exit code and no
case name. The cost of that choice, stated: a team agent is editing the test of the guard that
governs its own writes, and a weakened assertion there would not be caught by the assertion itself.
The mitigations are that the task's intent forbids assertion edits and that the diff is small enough
to read. The alternative — main-session-direct, as FEAT-10 chose for `test-check-state.py` and
FEAT-15 for `test-check-domain.py` — buys that safety for a permanent `DEVIATION` line. The
difference from both precedents is that they edited the gate script in the same task and this one
does not.

### (d) Blast radius, re-derived at sha a29ad06 = HEAD (the grilling's anchors were measured at e057525 and are stale)

- `factory_config.py`: `load_fleet` :72-159 (the one place fleet shape is enforced), `repo_entry`
  :166, `station` :179 (`fleet["board"]["stations"]` at :181 — the grilling's `:158` is stale),
  `_main --show` :205.
- `factory_claim.py` :207-210 board reads, :215-222 station validation against the real board,
  :224-247 the board read. **This is the only reader whose shape genuinely changes:** in poll mode
  (`--issue` absent) it queries one board before knowing which repository, so its board reads and its
  station validation move inside a per-repository loop. Every other reader already holds `args.repo`.
- `factory_decompose.py` :354-357 plus `factory_config.station(fleet, "ready")` at :423; `args.repo`
  is required.
- `factory_land.py` :85-88, including `stations["review"]` read directly; `args.repo` is required.
- `factory_workspace.py` :113-114 — `load_fleet` + `repo_entry`, no board read. The **source** is
  untouched; its **test fixture** is not (see below).
- `factory_gh.py` takes owner and number as arguments. Already clean.
- Fixtures carrying a fleet board — **seven files, not six**: `test-factory-config.py`,
  `test-factory-claim.py`, `test-factory-decompose.py`, `test-factory-land.py`,
  `test-factory-integration.py`, `test-check-domain.py`, and **`test-factory-workspace.py`**, whose
  `good_fleet_dict` builds a top-level `board:` with a `repos:` entry carrying none and is in
  `UNIT_SCRIPTS` — the exact shape T-08 rejects twice. It is T-11. Not `test-check-state.py`
  (see (c)).

### (e) The four items the grilling left open

- **Per-repo board is REQUIRED on every entry; there is no fleet-level default.** A default is
  friendlier and is exactly how this bug got in: kaya-ai inherited a board nobody chose for it, and
  nothing failed. REQ-03 makes the absence loud. Stronger than that, SC-02 makes a *leftover*
  fleet-level `board:` an error rather than an ignored key — an unknown top-level key is accepted
  silently by `load_fleet` today, which would recreate the same silence one level up.
- **`stations:` moves per-repo, inside the same board block as the number.** Station names are option
  names on a specific board, and identical names are not identical options. Measured on 2026-08-11 by
  `gh api graphql` on each project's `Status` field, board 2 and board 3 now carry the **same six
  names in the same order** on different board numbers, and three of those names — `Plan`, `Ready`,
  `Review` — carry **different option ids per board**, while `Backlog`, `Building` and `Done` share
  GitHub's default template ids across both. A board number split from its station mapping is
  precisely the pair that can drift, and `factory_claim`'s pre-flight validation compares the two
  against each other. That the two boards agree on names today makes the pairing *easier to get
  wrong silently*, not safer: a station name that resolves on the wrong board no longer fails loudly.
- **The live run uses a purpose-created throwaway issue in `mruangutai/kaya-ai`**, not a real one.
  It cannot be one of the 118 by construction, it needs no station restored afterwards, and it
  carries no feature label so the blocker gate stays out of the measurement. The run stops after
  `factory_claim` (station `Building`) rather than continuing to `factory_land`, so no pull request
  is opened against kaya's `master`. See Constraints for the full protocol.
- **The pairing assertion lives in `test-no-distribution.py`.** See (c).

### (f) The migration is three-phase, and the ordering is not tidiness

`check-domain.sh:214` calls `load_fleet` on every governed write and prints "BLOCKED — the fleet
declaration does not load … Enforcement is CLOSED rather than partial" on any exception.
`test-check-domain.py` case (c) fires exactly that path against a *harness* path and asserts exit 2,
so a fleet that does not load refuses harness writes, not only product ones. Both naive orderings
brick the guard, including the write that would fix it:

| order | what happens |
|---|---|
| fleet.yaml migrated first | the old `load_fleet` still demands a fleet-level `board:` → raises → every governed write blocked |
| `factory_config.py` tightened first | the unmigrated fleet.yaml still carries the fleet-level `board:` → rejected → every governed write blocked |

And one task cannot land both halves: `.harness/factory/fleet.yaml` resolves to NOBODY and
`factory_config.py` resolves to the team, and there is no split execution mode. So: T-01 makes the
fleet-level block **optional** and adds per-repo support; the readers migrate; T-07 rewrites
fleet.yaml and the board together; T-08 then tightens to required-and-rejecting. Needing the
one-session bootstrap escape here would be the exact circularity smell DEC-174 names.

## Constraints

- **Binding operator rulings, not pm choices.** The board becomes per-repository rather than being
  retargeted to 2. **Six is the intended end state**, and it is already applied: board 2 and board 3
  both carry `Backlog` → `Plan` → `Ready` → `Building` → `Review` → `Done`, the same vocabulary in
  the same order, so the file and the board cannot drift apart on names. Board 2 reached it by
  renaming `Todo` to `Backlog` and `In Progress` to `Building`, retaining `Done`, and adding the
  rest — zero item writes against the 118, because renaming a single-select option preserves every
  assignment. This feature therefore **confirms** that state; it does not create it. Done means a
  live run with the station move read off the board, never inferred from exit 0.
- **`Ready` is the factory's intake station, and an empty `Ready` is CORRECT.** `Backlog` means
  filed-and-untriaged; `Ready` means the operator has decided the factory may take it. Kaya's 82
  unstarted issues are correctly in `Backlog`, so a claim run against kaya finds nothing — and that
  is the truth, not a defect. **The gap this exposes is recorded and explicitly out of scope:**
  promotion from `Backlog` to `Ready` is a human decision with no recorded step anywhere in the
  harness. This feature does not close it and must not silently absorb it. The only thing it owes
  the gap is SC-13 — a claim run that finds nothing must say so rather than exiting 0 in silence.
- **The live-run protocol.** Create a throwaway issue in `mruangutai/kaya-ai` titled so it is
  identifiable as factory verification — it must not be one of the 118 items in `Done`, since the run
  moves a station; leave it unlabelled, open and unassigned; add it to board 2 at `Ready`; run
  `factory_claim` against it; read `Status` back off board 2 and confirm `Building`.
  Clean up by deleting `refs/heads/factory/issue-N`, removing the `factory:claimed` label and closing
  the issue.
- **DEC-174 carve-out.** No task changes `check-domain.sh`, `bash-write-guard.sh`,
  `validate-digest.py` or `check-state.sh`. Measured: none needs to.
- **`harness.json`'s `github.repo` is out of scope.** It still names `mruangutai/harness` for the
  issue mirror; that is a different mechanism from the station board.
- **Out of scope, from the grilling.** Moving kaya's issues to board 3 or harness's to board 2; board
  6 and `harness-factory-smoke-a1` (retained fixtures); re-adding `mruangutai/harness` to `repos:`
  (its absence is DEC-174 am.1 and is asserted).
- **Poll-mode board scanning stays as it is** apart from becoming per-repository. Its
  `project_items` query shape is not this feature's business.

## Verification gaps

- No runner reads a GitHub board. SC-03, SC-06 and SC-07 rest on live `gh` reads and on the operator,
  never on a test; nothing in CI will ever re-check them, so a later board edit that breaks the
  pairing is caught only by SC-05's static assertion in `test-no-distribution.py`.
- `component`, `ui`, `eval` and `typecheck` have `cmd: null` in `.harness/harness.json`. This feature
  touches none of those surfaces, so no criterion rests on them.
- Concurrency is not exercised. DEC-186 already records that serialised ref creates are inferred and
  unmeasured; this feature does not change that and does not close it.

## Approval

status: approved
approved-by: operator
date: 2026-08-11
