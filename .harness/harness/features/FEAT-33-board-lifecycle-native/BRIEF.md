# BRIEF — FEAT-33 The board's whole lifecycle, native-first

Source ticket: #675. Sub-issues #673 and #674 are absorbed here (see *Scope calls*); #453 is closed
carrying a defect its own title names, and this feature closes that defect.

## Problem

The operator reads the GitHub board to know what the factory is doing, and the board lies in four
distinct ways. A card can sit at `Plan` only because a human typed the word: the harness declares five
stations and `plan` is not one of them, so no tool can name that column. `start-task` walks a **closed**
card back to `Building` — measured on #642 and #643, and it is the cause of every board error on this
project. A ticket the harness closes carries `state_reason: null`, so shipped and abandoned are the same
thing to anything reading the API, and #349, #357 and #358 sit at `Done` indistinguishable from work
that landed. And when a repository joins the fleet nothing creates its board at all, so its correctness
is whatever the operator happened to click. The cost is that the one surface the operator trusts is the
one surface nobody verifies.

## Goal

In the operator's own framing: *"i'd hate to reinvent the wheel here, if we can use github's native
features to attach a PR, set the ticket/issue station to Done, and close the ticket."* A repository
joins the fleet and its board is correct from that moment — the project exists, the Status field carries
every station the harness uses, the repository is linked, and the operator is told plainly which native
workflows they must switch on by hand because no API can. Cards then move without a human, a shipped
ticket closes `completed` and an abandoned one closes `not_planned` and wears a visible `abandoned`
label. The two existing projects are brought to that same shape — harness board 3 first as the proving
ground, then kaya-ai board 2.

## Requirements

- REQ-01: A repository joining the fleet finishes `/harness-init` with a Projects v2 board that exists,
  is linked to the repository, and carries a Status field whose options include every station the
  harness declares — created by the harness where the API allows it.
- REQ-02: `/harness-init` reports, for that board, which of the three native workflows the harness
  depends on (`Item closed`, `Auto-close issue`, `Pull request merged`) are enabled, and names each one
  that is not, together with the fact that only a human click can enable it.
- REQ-03: Every station the harness can write is declared in the board's own configuration, and a
  declaration that disagrees with its board is a loud failure rather than a silent one.
- REQ-04: The harness never moves a closed ticket's card backwards.
- REQ-05: A ticket the harness closes carries an explicit reason — `completed` when it shipped,
  `not_planned` when it was abandoned — and an abandoned ticket carries a visible `abandoned` label a
  human sees without opening a field.
- REQ-06: For either served project, the operator can ask whether its board matches the harness's
  expectations and receive a finite list of exactly the cards and tickets that do not.
- REQ-07: Both existing projects reach a zero-finding state on that list, including cards already
  sitting on the wrong station.
- REQ-08: Every station the harness writes is written by the act that causes it, so no station is
  left to a rule that never fires and none is left to an agent remembering a line of prose.
- REQ-09: A feature's card reaches the right station whatever the execution mode of the work — a
  feature built entirely by the main session moves its cards for the same cause as a team-built one.
- REQ-10: `Ready` holds task sub-issues on every served board and never a parent, so the harness lane
  and the factory lane agree — and the human promotion signal board 2 loses by that change is
  recorded where a reader of that board finds it.
- REQ-11: A task ticket identifies the feature it belongs to from its title alone — for every ticket
  the harness creates from now on, and for every task ticket already on the board.

## Success Criteria

- SC-01: Running the provisioner against an owner with no board creates the project, creates the Status
  field carrying all six declared station option names byte for byte, and links the repository; running
  it against an existing board adds only the options that are missing.
  verify: automated      evidence: unit
- SC-02: The station declaration and the board agree: the declared key set is exactly the six the board
  columns carry, and a declaration naming a key with no matching option on the board is reported as a
  finding naming both the key and the board.
  verify: automated      evidence: unit
- SC-03: A shipped ticket closed by the harness reads `state_reason: completed`, an abandoned one reads
  `not_planned` and carries the `abandoned` label, and both assertions fail against the pre-change code.
  verify: automated      evidence: integration
- SC-04: The harness project (board 3) reports zero findings from the audit after reconciliation, and
  the captured report is committed under this feature's `notes/`.
  verify: inspection
- SC-05: `start-task` against a task whose issue is closed, or whose card already reads the `done`
  station, writes no station and prints one line naming the issue and the refusal — demonstrated failing
  first by replaying #642's shape (closed, card at `Done`, harness asked for `Building`).
  verify: automated      evidence: integration
- SC-06: Widening the required station keys is caught rather than assumed: a five-key declaration is
  REJECTED by the single board validator with a message naming `github.board.stations`, and a six-key
  declaration is accepted.
  verify: automated      evidence: unit
- SC-07: Provisioning is non-destructive and idempotent — no code path renames, deletes or reorders an
  existing Status option, and a second run reports "nothing to do" rather than writing.
  verify: automated      evidence: unit
- SC-08: No board gains an `Abandoned` Status option and no declared station key set contains
  `abandoned`; DEC-192's refusal of a seventh column stands unstruck.
  verify: automated      evidence: unit
- SC-09: Workflow detection is honest about its own blind spot — a workflow whose name does not match is
  reported as MISSING rather than assumed present, and the report says detection is by name because the
  API exposes neither trigger nor action.
  verify: automated      evidence: unit
- SC-10: Nothing already guarded is weakened: the full unit and integration suites pass, and
  `check-state.sh` exits 0 on the harness checkout after the migration — with no edit to
  `check-state.sh`, `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py` or
  `check-plan-routes.py` in this feature's diff.
  verify: automated      evidence: integration
- SC-11: The kaya-ai project (board 2) reports zero findings from the audit run against remote `master`,
  executed by the operator, and the operator confirms board 2 reads correctly to their own eye.
  verify: uat
- SC-12: The record does not contradict itself: at `review_sha`, `git show <review_sha>:.harness/harness/docs/DECISIONS.md`
  contains a DEC-196 amendment recording that `plan` is now declared and why that reverses amendment 1's
  clause without striking it, and `DECISIONS-INDEX.md`'s DEC-196 row reflects it.
  verify: inspection
- SC-13: Recording a feature's phase status and performing that event's station writes are ONE act:
  recording `Ready` moves EVERY `T-NN` sub-issue to the ready column and writes nothing to the
  parent; recording `Review` moves the PARENT to the review column; recording `Done` or `Abandoned`
  writes no column at all. Each of the four is asserted separately — a per-status count is satisfied
  by the conformers alone — and each fails against the pre-change code, where the recorder wrote no
  station whatsoever.
  verify: automated      evidence: unit
- SC-14: No parent card ever reaches the ready column: asking the recorder for `Ready` on a feature
  with zero recorded sub-issues writes NOTHING rather than falling back to the parent, and no code
  path in the diff passes the declared `ready` station together with a recorded `github.parent`.
  Demonstrated by a fixture asserting the exact set of issue numbers written.
  verify: automated      evidence: unit
- SC-15: The station-writer map exists once and names one writer per station: at `review_sha`,
  `git show <review_sha>:.harness/harness/docs/DECISIONS.md` carries a six-row map naming exactly one
  writer for each of `Backlog`, `Plan`, `Ready`, `Building`, `Review`, `Done`; `DECISIONS-INDEX.md`'s
  row reflects it; and `git show <review_sha>:.claude/skills/harness/SKILL.md` names the **main
  session** as the owner of `start-task` and `close-task` for a `main-session-direct` task, which at
  `e3c9187` it names for nobody.
  verify: inspection
- SC-16: The audit reports a feature whose recorded status disagrees with its parent card, naming the
  feature, the recorded status, the column that status means and the column actually read —
  demonstrated on THREE measured shapes, each as its own assertion: FEAT-32 (`status` `Review`, parent
  `#700` at `Building`), FEAT-08 (`status` `Done`, parent `#85` **open** at `Backlog`) and FEAT-09
  (`status` `Done`, parent `#98` **open** at `Backlog`), all observed 2026-08-22 at `f5f5185`. The
  second and third are the cases INV-26 skips on its terminal exemption and the existing `STATION`
  class skips because it keys on closed issues, so a `Done`-status exemption in this class would
  reproduce exactly the blindness it exists to remove. Each returns no finding under the pre-change
  audit.
  verify: automated      evidence: unit
- SC-17: A task ticket the harness creates names its feature before its task id, using the same
  separator `gh-sync.py`'s parent title already uses, and the assertion fails against the
  pre-change generator.
  verify: automated      evidence: unit
- SC-18: The backfill never writes a feature id it did not read off the ticket's own milestone: a
  ticket with no milestone is refused and named rather than renamed, and a ticket already carrying
  its feature id is skipped — both demonstrated failing first.
  verify: automated      evidence: unit
- SC-19: Every task ticket on `mruangutai/harness` names its feature: the captured backfill report
  under this feature's `notes/` shows 188 tickets renamed or already correct with zero refused, a
  second run reports nothing to do, and the report records the GraphQL points spent against the
  5000/hour budget.
  verify: inspection

## Verification gaps

- **FIVE test kinds carry `cmd: null` in `.harness/harness.json` `test_kinds`, and they split into two
  different mechanisms.** `functional` (`:113`) is `status: excluded` with a signed DEC-187 and its own
  `excluded_because` — that is the *only* soft skip this config allows. `component` (`:127`), `ui`
  (`:134`), `eval` (`:141`) and `typecheck` (`:148`) are `status: unresolved`, and `harness.json:102`
  states in terms that a null cmd is **BLOCKED in the qa gate, never a skip**. No criterion here rests
  on any of the five. The reason is **not** that this feature touches none of those surfaces — that is
  not the matrix's test. The reason is that none of the five is **selected** by this feature's change
  types: `config` and `docs` are `always: []`; `logic`, `api` and `bugfix` require `unit`; `feature`
  requires `unit` and `integration`; the one conditional kind that could reach `ui` is gated on
  `has_interaction_flow`, which is false here. Re-derived at `e3c9187`.
- **The `integration` kind is active but its `detect` is a closed filename list, and that dictated where
  the new tests go.** `test_kinds.integration.detect` (`harness.json:119`) is `tests/integration/**`
  plus six explicit filenames, and `run-unit-tests.sh:18` `INTEGRATION_SCRIPTS` is a matching 14-name
  array — re-derived at `e3c9187`, and byte-identical to `main` at `d065b3b`, so FEAT-31 has landed
  nothing here. A new `test-board-lifecycle.py` therefore can **never** be selected as
  `integration`, and the qa gate does not accept an unrelated passing test as coverage
  (`harness-qa-gate` SKILL.md: *"Presence is not satisfied by an unrelated existing test"*). Every
  task whose change type requires `integration` therefore carries its end-to-end cases in
  **`test-factory-integration.py`** — already in both lists, and already the tree's only file that
  forks a real process against a stub `gh` (D-12). No edit to the runner's kind arrays and no edit to
  the matrix is planned to close this. What is therefore NOT proven: nothing — but the integration
  evidence for the new bin lives in a file named for a different tool, so a later reader looking for
  `test-board-lifecycle.py` in `INTEGRATION_SCRIPTS` will not find it, by design.

- **No runner can reach a live GitHub board.** Every automated criterion above proves *logic* against a
  fake `gh` binary injected through BOTH `FACTORY_GH` and `GH_SYNC_GH` (the fake-binary trap documented
  at the top of `gh_board.py` — a fake set through one variable alone leaves the other calls hitting the
  real board). The live outcome on board 3 is carried by SC-04's captured report (inspection) and on
  board 2 by SC-11 (uat). What is therefore NOT proven by any runner: that the real GitHub API accepts
  the provisioning mutations, and that the reconciliation moved the cards the operator sees.
- **Cross-repo verification is asymmetric on purpose.** `factory_config.product_config` reads a served
  repo's `.harness/harness.json` from the REMOTE at `default_branch` and never from a checkout, so no
  harness-side test can see kaya-ai's configuration until it is merged to `master`. SC-11 is `uat` for
  that reason, not for want of trying.

## Scope calls, argued rather than assumed

**#673 (board workflow detection) is IN.** It shares the file, the step and the network read with
REQ-01: the provisioner already resolves the project and the Status field at `/harness-init`, and the
workflow read is one further query on the same node. The alternative — leaving it a separate feature —
costs a second approval cycle, a second edit to `harness-init/SKILL.md` (a **main-session-direct** path,
so the two edits cannot be parallelised), and one thing worse than either: a board this feature creates
that nobody checks the workflows on. The whole destination is *native-first*, and the native chain **is**
those three workflows — a correct Status field with `Item closed` switched off produces a board that
looks provisioned and moves nothing. The operator's ruling that detection lives at `/harness-init` and
not in `check-state.sh` is untouched and not revisited.

**#674 (start-task drives a closed card backwards) is IN** — it is the single largest source of the
wrong stations REQ-07 has to reconcile, and reconciling a board while the bug that dirtied it is still
live means migrating twice.

**FEAT-26's subject is EXCLUDED BY THE OPERATOR'S CHOICE, not overlooked.** The `pr` field, recording
source tickets, and rendering `Closes #N` lines are planned in FEAT-26 and one round from signable. The
split was made deliberately so that FEAT-26's value does not wait behind a cross-repo migration. This
feature does not touch the `pr` field or the `Closes` renderer, even though the measurement on PR #491 —
`Closes` **is** the automation, not a convenience over it — is the reason the native chain works.

**Also out of scope:** enabling the three workflows (impossible, not a scope call — there is no
`ProjectV2` mutation that creates or enables one), any repository other than harness and kaya-ai, and
unifying the three `ensure_labels` implementations.

## The two contradictions, resolved

**Contradiction 1 — the `plan` omission.** I re-derived it and I **confirm** that
`gh_board.derive_station` (`gh_board.py:88`) returns only the `building` station, the `review` station,
or `None`. DEC-196 amendment 1's reasoning is therefore **not falsified** and no DEC-188 strike is
sought: declaring `plan` would not have made `derive_station` return it, and am.1's claim that an
undeclared name is still writable is independently true — `board-station.py` passes the station as a
plain string and the option resolves by name at the board.

I **overturn** the framing that the defect is a missing derivation. `Plan` is not a function of task
statuses; it is the state before tasks have issues, written once at kickoff by `board-station.py` per
DEC-196. An all-pending → `Plan` branch would fire on every mirror call while tasks are pending and
would overwrite a card the operator promoted to `Ready` — and `Ready` carries a documented, load-bearing
meaning on board 2 (`Backlog` = filed-and-untriaged, `Ready` = promoted for the factory, stated in
kaya-ai's own `harness.json`). That would be a new backwards-move bug of exactly the #674 class this
feature exists to close. So: `plan` is declared for **parity** — DEC-192's six values, and a named key
at the kickoff call site instead of a case-sensitive literal — and **no derivation is added for it**.
Because that reverses one clause of amendment 1, DEC-196 gains an amendment (SC-12); it is not struck.

**Contradiction 2 — `Abandoned`.** Resolved as the artifact's Settled section states and DEC-192
requires: **`Abandoned` is carried by the ticket, never by a sixth or seventh column.**
`state_reason: not_planned` plus a visible `abandoned` label. No board gains an `Abandoned` Status
option, so DEC-192's "a second value to express it would be a seventh column the board does not have"
stands unstruck and needs no strike-or-amend record. This is not a compromise: the tree already agrees
with it — `feature-schema.json`'s `status.enum` carries `Abandoned` and its own description states it is
"the one value with NO board column", and `gh-sync.py:187` already treats it as terminal alongside
`Done`. The dispatch's paraphrase of constraint 2 ("add `Abandoned` to the station map") is the outlier,
and the operator's own settled record outranks it.

**The `abandoned` label is CREATED BY THE HARNESS**, by `gh-sync.py`'s own `ensure_labels` — the
implementation already used at `open` to create `harness` and the change-type labels, whose
swallow-errors policy is the mirror-never-gates posture DEC-138 requires. `abandoned` gains an entry in
that function's colour map. The three implementations are **not** unified: `factory_gh.ensure_labels`
uses `--force` and would overwrite the colour, and that collision is recorded here rather than fixed.

## The five previously-unspecified items, each closed

1. **Create or only validate?** **CREATE, guarded.** The harness creates the project when absent,
   creates the Status field when absent, adds missing options to an existing field, and links the
   repository — then reports what it cannot do. Reason: the six option names are case-sensitive board
   column names (DEC-192, byte for byte), and a human typing six of them is a silent-drift generator the
   operator only discovers when INV-26 fires. Provisioning is never destructive (SC-07).
2. **The canonical station map.** **Six keys — `backlog`, `plan`, `ready`, `building`, `review`,
   `done`** — one per DEC-192 status value, spelled as that board's own column names. Measured
   2026-08-22: board 3 and board 2 both already carry exactly `Backlog | Plan | Ready | Building |
   Review | Done`, so this makes the declaration match a board that is already right.
3. **How a migration proves it finished.** The right station for a card whose feature is long done is
   the `done` station with the ticket closed and an explicit `state_reason`. Proof is a single audit run
   returning **zero findings**, where a finding is any of: a declared station key with no matching board
   option; a closed issue not at the `done` station; a closed issue with `state_reason: null`; an issue
   with `state_reason: not_planned` and no `abandoned` label; or one of the three required workflows not
   enabled. Zero findings and exit 0 is the definition of finished (SC-04, SC-11).
4. **Must kaya-ai match harness exactly?** **It must satisfy the same contract, not copy the set.** The
   contract: the declaration names exactly the six keys, and each value is an option that board actually
   carries. Their sets coincide today because both boards carry the same six English names — that is a
   measurement, not the requirement. kaya-ai's board and station rationale stay in its own
   `.harness/harness.json` on `master`; nothing is restated in `fleet.yaml`.
5. **Who creates the `abandoned` label?** The harness, via `gh-sync.py`'s `ensure_labels` — see
   Contradiction 2 above.

## The station lifecycle is EVENT-DRIVEN (operator ruling, 2026-08-22, later)

Every station is written at the moment something happens, by whatever performs that act. The map,
with what the tree does today measured at `f5f5185` on board 3 across 539 items:

| # | Event | What moves | Writer | Items today |
|---|---|---|---|---|
| 1 | the ticket is filed | the source ticket to `Backlog` | whoever files it | 304 |
| 2 | `/harness-plan` opens | the source ticket to `Plan` | `board-station.py`, once, at the door | 2 |
| 3 | **the plan is signed** | **every `T-NN` sub-issue to `Ready`** | the signature step | **0** |
| 4 | a task starts | that sub-issue to `Building` | `gh-sync start-task` | 5 |
| 5 | **the panel kicks off** | to `Review` | the panel dispatch | **0** |
| 6 | a task's commit is recorded | `close-task` closes that sub-issue; GitHub moves it to `Done` | `gh-sync close-task` + the native `Item closed` workflow | 228 |
| 7 | the PR merges | `Closes #<parent>` closes the parent | **GitHub** | — |

**`Ready` holds a feature's TASK SUB-ISSUES, so the team can pick them up. The parent is never a
claim candidate.** Sub-issues then move individually through `Ready` → `Building` → `Done`.

**The precedent is already shipped, and nothing about the factory queue changes.**
`factory_decompose.py:393` carries the comment *"The parent is NEVER added"* — on a served-repo board
only task issues get cards. So `factory_claim.py:302`'s `Status:"<stations.ready>" is:open` poll
contains only tasks **by construction**, and always has. What is wrong is the **harness lane**, which
does the opposite: board 3 carries parents as cards (22 recorded parents measured at `f5f5185`; `#700`
sits at `Building`). The work is therefore to make the harness lane behave the way the factory lane
already does about `Ready`, not to move any queue.

**`Ready` and `Review` both hold zero.** `Ready` has no harness-lane writer in the tree at all.
`Review` is reachable in principle — `close-task` on the final task derives it — and has never
fired, because the last `close-task` runs while later tasks are still `pending` and nothing calls
`gh-sync` again until ship. A station that is never written is the same shape as an assertion that
cannot go red.

**Step 6 needs no new code — it needs to actually run.** `gh-sync close-task` already closes exactly
that task's sub-issue and nothing else (`SKILL.md:192`, DEC-138 am.7). It never ran for **any**
FEAT-32 task. That is this feature's hole, not a missing feature.

**Step 7 is a change from current practice, stated rather than discovered.** FEAT-31's PR body carried
`Closes` for all 19 sub-issues **and** parent `#598` in one go. Under this lifecycle the sub-issues
close as they complete and the parent closes once at merge. The two are not equivalent: the old way
makes every sub-issue's `Done` depend on the merge, and **that is the measured reason board 3 has
never had a card at `Review`** — they all jumped to `Done` at once.

## The parent's card — kept, and derived

The parent **keeps a card** on the harness lane. Its station is **derived from its sub-issues**:
`Building` when any sub-issue is building. `#700` and every other parent card stay; nothing is
removed from the board.

**`gh_board.derive_station` (`gh_board.py:88`) already implements this, and it must not be
"fixed".** It returns the `building` station if any task is `building`, the `review` station if there
is at least one task and every task is `done`, otherwise `None`. It reads `plan.yaml` task statuses
rather than the children's board stations. **Those are the same answer with one fewer board read** —
the plan is the source the children's stations are written from — and the cheaper source is the right
one, because a per-parent children read would spend GraphQL points on every mirror call. The
equivalence is by construction; do not convert this into a board read.

> **INFERRED, NOT RULED — visible here so it is overturnable in one edit.** The operator ruled on
> `Building` only. A parent with a rule for one of six stations is not a lifecycle, so the completion
> is drafted and marked:
>
> 1. **The parent reads `Ready`** when sub-issues exist and none has started, and **`Review`** when
>    the panel is running. Inferred.
> 2. **`Ready` on the parent is forbidden on a served board**, because `factory_claim.py:302` polls
>    that station for pickable work. On the harness lane no `factory_claim` runs, so the constraint
>    is latent there — but a rule that is true on one board and not the other is the per-repo meaning
>    this feature exists to forbid. **The safe reading, applied in the plan: the parent never reads
>    `Ready` on any board**, and inference 1's `Ready` clause is therefore NOT built.
> 3. **`Review` on a SUB-ISSUE is unreachable under this lifecycle, and steps 5 and 6 are mutually
>    exclusive for sub-issues.** Step 6 closes a sub-issue as its commit lands, and GitHub moves a
>    closed card to `Done`; the panel kicks off strictly after the last commit. So a sub-issue is
>    already `Done` before step 5 could write `Review` to it — the station dies again, one level down,
>    for the same structural reason. Two readings: **`Review` is a PARENT-only station** (sub-issues
>    run `Ready` → `Building` → `Done`), which is what the plan drafts; or `close-task` stops closing
>    sub-issues so they can hold `Review`, which reverts to FEAT-31's close-everything-at-merge
>    pattern the step-6 ruling just replaced.
> 4. **An ordering question between step 5 and the derivation.** If the parent derives `Review` from
>    all-tasks-done, it reaches `Review` when the LAST task closes — before the panel finishes and
>    before the PR exists. The two writers agree on the value and disagree on the moment. Left as
>    drafted; not silently picked.
>
> Surfaces resting on this block: **REQ-08**, **REQ-10**, **T-13**, **T-15**, **T-19**, **T-20**.

**The hole: a station write is REMEMBERED, not caused.** The only thing in the repo that moves a
card mid-build is one row of a markdown table — `.claude/skills/harness/SKILL.md:191` — addressed to
the **orchestrator**. `main-session-direct` tasks are forbidden to the orchestrator by DEC-174, and
nothing anywhere instructs the main session to move their cards; the only mention of
`main-session-direct` in that file is `:131`, about run counting. FEAT-32 carries **9 of 17** tasks
in that mode. Its cards read correctly today only because the merge's `Closes #N` closed the issues
and GitHub's own `Item closed` workflow moved them — **the only station that self-heals is the one
GitHub writes.** Its parent `#700` still reads `Building` while its `feature.json` status reads
`Review`.

**The ceiling on "caused", stated rather than sold as solved.** Two things in this system cause a
write without an agent choosing to: GitHub's own workflows, and a Claude Code hook. Hooks are the
enforcement layer, which DEC-174 forbids this feature from executing, and a board read inside
`PostToolUse Write|Edit` would fire on every edit in every session against a measured 490–506
GraphQL points per board read — the waste the operator already refused for `check-state.sh`, an
order of magnitude worse. So the design folds each station write into a command that is **already
mandatory at that moment**, so that forgetting the station requires forgetting the whole act:

- **The phase transition is the moment, and `feature.json`'s own `status` is the record of it.** That
  needs **no new vocabulary** — `check-state.sh:494` already declares the closed set
  `Backlog | Plan | Ready | Building | Review | Done | Abandoned`, the schema already enforces it, and
  `gh-sync.py`'s `_record_status` already writes it at ship and abandon. Recording the status and
  performing that event's station writes become one act, so forgetting the cards requires forgetting
  the phase record.
- **The parent's own station keeps its existing writer and gains no second one.**
  `derive_station` plus `_apply_parent_rule` remain the only thing that writes a parent card from task
  statuses. `feature.json.status` is not a second source for it — two writers for one card is the drift
  this feature exists to remove.
- Absence is therefore detectable **offline and for free** — the audit compares `feature.json.status`
  against the parent card using the board read it already performs, with no new derivation and no
  extra network call. **Measured at `f5f5185`, that comparison finds two live cards nothing else
  sees:** `#85` (FEAT-08) and `#98` (FEAT-09) are **OPEN** parents whose `feature.json.status` reads
  `Done` and whose cards read `Backlog`. INV-26 skips them on its terminal exemption; the audit's
  existing `STATION` class keys on **closed** issues and skips them too. Both features shipped; both
  parents were left open because no `parent_origin` was recorded, so `ship` declined to close them.

## `Ready`'s one meaning — SETTLED, and the collision dissolved rather than traded off

**The ruling: `Ready` holds a feature's TASK SUB-ISSUES, so the team can pick them up.** One meaning
on every served board. Board 2's documented "promoted for the factory" meaning survives in substance —
`Ready` still means *available to be picked up* — and what changes is **who puts a card there**: the
signature, mechanically, instead of a human promoting a ticket by hand.

**No branch of the earlier collision is taken, and nothing about the factory queue changes.** The
apparent conflict existed only while the ruling was read as applying to the **parent**. It does not:
`factory_decompose.py:393` records *"The parent is NEVER added"*, so `factory_claim.py:302`'s poll has
only ever contained tasks. Both re-derived at `f5f5185`.

**The stated cost, narrowed to what is actually lost: board 2 loses the HUMAN promotion signal, not
the column.** kaya-ai's own `.harness/harness.json` on `master` documents `Ready` as the human
pick-up point; after this, a card arrives there because a plan was signed, and nothing on board 2
records that a human chose to promote a ticket. A visible label is the route if that signal turns out
to be needed — the same shape as the `abandoned` label already chosen — and it is **NOT** built here.

**What the harness lane must stop doing:** it must never write `Ready` to a **parent** card, on any
board. That is the one thing it copies from the factory lane.

## Constraints

**These SUPPLY the mechanism this feature builds on:**

- **DEC-186 + am.1** — GitHub Issues and one board per repository served are the control plane, and
  read-back is bounded to three purposes. Reading a Status field's option set is the same read
  `factory_gh.project_field_set` already performs to resolve a name to an option id, so nothing here
  widens that bound. Reading a project's `workflows` for the init-time report is a **configuration**
  read, not a control-flow read, and writes nothing into any approval-gated artifact.

  > **UNRESOLVED — THE OPERATOR'S RULING IS OUTSTANDING.** The architecture review rejects the
  > paragraph above. DEC-186 (`DECISIONS.md:5528-5533`) bounds GitHub read-back to *"exactly THREE
  > purposes, and the set is closed"*, and am.1 (`:5600-5603`) states it *"neither widens nor narrows
  > it"*; the precedent for the third purpose was an explicit operator ruling recorded as a widening by
  > one item. Re-categorising a fourth read as *configuration* is not that. **The operator must choose
  > one of two branches: amend DEC-186 to widen the set to four, bounded to `/harness-init`; or drop
  > REQ-02.** Neither branch is pre-applied here, because applying the wrong one costs a cycle. The
  > surfaces that rest on the unresolved question, left EXACTLY as drafted: **REQ-02**, **T-03's fifth
  > primitive `project_workflows`**, **T-05's finding class 5 (WORKFLOW)**, **T-10** and **SC-12**.
  > The `project_field_options` read is unaffected — resolving an option name to an option id *is*
  > DEC-186's second purpose.
- **DEC-138** — the mirror is write-only, orchestrator-executed, and **never a gate**. So `gh-sync.py`,
  `board-station.py` and the new board tool are all ordinary dispatchable code.
- **DEC-146** — the station flip stays best-effort by design. Nothing here converts a board failure into
  a gate.
- **DEC-196 + am.1 + am.2** — the harness MOVES any card it is pointed at and CLOSES only cards it
  created. Unchanged: both close paths stay gated on `parent_origin == "created"`.
- **DEC-192** — the six case-sensitive status values ARE the board's column names, and a seventh column
  was declined on the record. Both upheld.
- **DEC-133** — this id is coined once and is immutable. **DEC-130** — this feature's notes live under
  `features/FEAT-33-board-lifecycle-native/notes/`. **DEC-182** — the plan is real `plan.yaml`.
  **DEC-164** — the grilling artifact is this brief's mandatory input.
- **DEC-187** — every test kind in the matrix is `active` or `excluded` with a signed decision; see
  *Verification gaps*.

**These BLOCK or bound the work:**

- **DEC-174 + am.1 + am.4 — the enforcement-layer carve-out.** The harness plans but does not execute
  changes to its own hooks, validators or gate scripts, and the list is non-exhaustive. This feature is
  designed to need **no** edit to any of them: `check-state.sh`'s INV-26 indexes only the `building`,
  `done` and `backlog` station keys (`check-state.sh:1184-1185`, `_EXPECT`), so a sixth key is inert
  there — re-derived at `e3c9187`. Worth
  recording: `check-domain.sh --resolve` grants `check-state.sh` to `harness-dev-ops` while DEC-174
  forbids dispatching a change to it. The carve-out wins; this plan avoids the disagreement by not
  editing the file.
- **`mruangutai/harness` is deliberately ABSENT from `fleet.yaml`** (DEC-174 am.1) and is not added.
- **Five paths in this feature have no dispatchable owner** and are declared
  `main-session-direct` in the plan: `.claude/skills/harness-init/SKILL.md`,
  `.claude/skills/harness/SKILL.md`, `.claude/commands/harness-plan.md` and kaya-ai's own
  `.harness/harness.json` all resolve to NOBODY — re-derived with
  `check-domain.sh --resolve` at `f5f5185` — and a generic file under this feature's `notes/`
  resolves to `harness-orchestrator`, which is not a task executor.
- **No hook is added, changed or registered.** DEC-174's carve-out forbids executing a change to the
  enforcement layer, and the only genuinely *caused* write available there — a `PostToolUse`
  `Write|Edit` hook firing a board read — costs a measured 490–506 GraphQL points per fire on board 3
  and would fire on every edit in every session. SC-10's list of five untouched enforcement files
  therefore **stands unchanged** with the station-lifecycle work added: nothing in it edits
  `check-state.sh`, and INV-26's existing task-level comparison is neither weakened nor duplicated.
- **A cross-repo ordering cost, stated rather than discovered.** The one board validator in the tree
  tests the declared station keys for **exact set equality** (`factory_config.py:134`). So widening the
  required set to six and updating kaya-ai's `master` cannot be atomic, and between the two merges
  `board_for('mruangutai/kaya-ai')` raises `FleetError` naming `github.board.stations`. The breakage is
  **latent, not live** — nothing calls it unless a `factory_*` command is run against kaya-ai — and the
  failure is loud and names its own fix. Accepted, and the plan orders the kaya-ai config change first
  so the window closes in the direction of correctness. This is the one place the plan departs from
  "harness first"; the harness-first ordering the operator set governs the **migration**, which is
  unchanged.
- **Concurrency, re-derived rather than assumed.** FEAT-31, FEAT-26 and FEAT-32 are live.
  `run-unit-tests.sh`, `check-state.sh`, `check-domain.sh`, `harness.json` and `DECISIONS.md` all have
  other writers. **Measured at this feature's HEAD `e3c9187`:** `git diff --name-only d065b3b..e3c9187`
  returns only files under `features/FEAT-33-board-lifecycle-native/`, so *none* of those features has
  landed anything on any surface this plan reads, and `d065b3b` is still `main`'s tip. Every code
  anchor in `plan.yaml` is therefore re-pinned to `e3c9187` and unchanged in content. What this plan
  still touches with another writer, and must rebase against: **one line of `run-unit-tests.sh`**
  (registering `test-board-lifecycle.py` in `UNIT_SCRIPTS`, which the drift detector at `:41-55` makes
  mandatory — an unregistered `test-*.py` exits 2 `MISCONFIGURED` and breaks every `verify:` in this
  plan at once), `DECISIONS.md`, and `harness.json` — but `harness.json` is now touched by **T-02
  alone**, and only to add `"plan": "Plan"` under `github.board.stations`. T-04 no longer lists it: the
  `test_kinds.unit.detect` glob `.claude/skills/harness/bin/test-*.py` already matches the new test file
  (`harness.json:105`), so the `detect` entry T-04 was going to consider adding is redundant, and a
  listed-but-unwritten path in a three-writer file only invites a gratuitous edit.

## Approval

status: pending
