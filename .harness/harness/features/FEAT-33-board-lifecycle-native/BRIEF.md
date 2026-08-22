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
- **Three paths in this feature have no dispatchable owner** and are declared
  `main-session-direct` in the plan: `.claude/skills/harness-init/SKILL.md` and kaya-ai's own
  `.harness/harness.json` both resolve to NOBODY, and a generic file under this feature's `notes/`
  resolves to `harness-orchestrator`, which is not a task executor.
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
