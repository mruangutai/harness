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
  left to a rule that never fires and none is left to an agent remembering a line of prose — and a
  task's ticket stays open long enough to be seen at every station it passes through, closing with
  its parent when the work merges rather than at its own commit.
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
  **NOTE appended 2026-08-23, on the operator's ruling — SC-01's text, `verify:` and `evidence:` above
  are BYTE-IDENTICAL to what was signed and are NOT amended.** SC-01 grades an END STATE, and that end
  state is met and was proven live on board 8 (`notes/live-provision-sc01.md`): after one run the
  project exists, the repository is linked, and the Status field carries all six declared station option
  names byte for byte. Only the mechanism verb is imprecise. On a fresh board the station field is not
  *created* — GitHub already ships a `Status` single-select carrying `Todo`, `In Progress` and `Done`,
  and `createProjectV2Field` answers *"Name has already been taken"* — so the field is brought to the
  declared options by REPLACEMENT instead (see SC-07 as amended). The note exists so the next reader
  does not write create-only code to match the verb, which is exactly the bug the live run found.
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
- SC-07: Provisioning is non-destructive on every ESTABLISHED board and is idempotent — no code path
  renames, deletes or reorders a Status option on a board that existed before the run, and a second
  run reports "nothing to do" rather than writing. **ONE exception, and it is the whole of the
  exception: a board the SAME RUN created.** There the option set is replaced with exactly the six
  declared stations, which deletes GitHub's defaults `Todo` and `In Progress`. **AMENDED 2026-08-23
  on the operator's express ruling; as signed it read** *"Provisioning is non-destructive and
  idempotent — no code path renames, deletes or reorders an existing Status option, and a second run
  reports 'nothing to do' rather than writing."* **What forced the exception is a MEASUREMENT, not a
  preference:** measured 2026-08-23 on project 7, owner `mruangutai`, a brand-new Projects v2 project
  ALREADY carries a `Status` single-select field whose options are `Todo`, `In Progress` and `Done`,
  so a fresh board cannot be provisioned without either replacing those options or leaving two
  columns nobody chose. The operator ruled to replace them. **The idempotence half is unchanged and
  still binds in full**, and so does non-destructiveness everywhere else — which is what this
  criterion was always protecting, since a destructive provisioner could erase a column the operator
  uses, and a same-run board holds no items and no card that could lose one. **TWO production call
  sites, not one** (cited by function, because this file is under concurrent edit and line anchors
  rot): `_fresh_board_station_field` in `.claude/skills/harness/bin/board_lifecycle.py` hands the
  mutation the bare declared list and is reachable only from `project_create`'s own return value in
  the same run; `_extend_to_union` in the same file computes `existing + missing` from its own read
  and serves every established board. Evidence: `test-board-lifecycle.py` case 5d (the fresh-board
  payload is exactly the six declared options, `Todo` and `In Progress` in no argv, the removal named
  on stdout) and provision case 1 (a complete board and a second consecutive run each perform zero mutations;
  the label is qualified because that file carries four separate "case 1" headers -- provision, audit,
  reconcile and retitle).
  Records: `plan.yaml` T-04's record entry 2 and D-07's amendment; `notes/live-provision-sc01.md`;
  `notes/research-FEAT-33-goal-check.md`.
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
  `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py` or `check-plan-routes.py` in this
  feature's diff. **The list is FOUR files, not five.** `check-state.sh` left it because ruling 1
  of 2026-08-23 makes INV-26 fire on every done task whose sub-issue is deliberately still open;
  the one bounded widening that fixes it is SC-20's, performed by the operator's own hand under
  the DEC-174 carve-out. **The drop from five to four is not this plan's choice: the operator
  ruled it** — ruling 4, 2026-08-23, `notes/rulings-2026-08-23.md` — **and accepted this cost by
  name when they ruled to fix the gate rather than reopen ruling 1.**
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
  parent; recording `Review` moves the PARENT **and every recorded sub-issue** to the review
  column; recording `Done` or `Abandoned` writes no column at all. Each of the four is asserted separately — a per-status count is satisfied
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
  session** as the owner of `start-task` and of `gh-sync.py status <dir> <Status>` for a
  `main-session-direct` task, which at `46ee87c` it names for nobody — `grep -c "main-session-direct"` on that file returns 1, at `:131`,
  about run counting.
  verify: inspection
- SC-16: The audit reports a feature whose recorded status disagrees with its parent card, naming the
  feature, the recorded status, the column that status means and the column actually read —
  demonstrated on THREE recorded shapes, each as its own assertion: FEAT-32 (`status` `Review`, parent
  `#700` at `Building`), FEAT-08 (`status` `Done`, parent `#85` **open** at `Backlog`) and FEAT-09
  (`status` `Done`, parent `#98` **open** at `Backlog`), all observed 2026-08-22 and recorded at
  `f5f5185`. **Re-derived at `46ee87c`: FEAT-32's shape is no longer live** — that feature shipped,
  its `feature.json` reads `Done` and `#700` is CLOSED as `COMPLETED`, so it is a written fixture
  and not a board state to go looking for. FEAT-08's and FEAT-09's parents are still **open** with
  `status` `Done` (`gh issue view`, 46ee87c); their card columns were not re-read. The
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

- SC-20: The one gate this feature does touch is widened exactly as far as the ruling forces and no
  further: at `review_sha`, INV-26 accepts a task whose recorded status is `done` and whose
  sub-issue card reads the `review` or `building` column **only while that feature's own
  `feature.json` status is `Review`**, and still reports the same card as a violation once the
  status is `Done`. Both directions are asserted in `test-check-state.py`, the second fails against
  an unconditional widening, and `check-state.sh`'s full finding list before and after the edit
  differs by nothing except the INV-26 station findings the change removes.
  verify: automated      evidence: integration

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
  `has_interaction_flow`, which is false here. Re-derived at `46ee87c`; every `test_kinds` line
  anchor above (`:113`, `:127`, `:134`, `:141`, `:148`) still resolves.
- **The `integration` kind is active but its `detect` is a closed filename list, and that dictated where
  the new tests go.** `test_kinds.integration.detect` (`harness.json:119`) is `tests/integration/**`
  plus **22** explicit filenames, and `run-unit-tests.sh:18` `INTEGRATION_SCRIPTS` is a matching
  **22**-name array — **re-counted at `46ee87c`, where the earlier draft said six and fourteen; both
  numbers were wrong and are corrected here.** `git diff origin/main -- run-unit-tests.sh` is empty
  against `main` at `e3392fd`, so FEAT-31 has still landed nothing here. A new `test-board-lifecycle.py` therefore can **never** be selected as
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
  board 2 by SC-11 (uat). **What NO RUNNER proves, and what captured live runs now do.** The runner
  clause above is unchanged and is still the bullet's whole point: no runner in this tree reaches a live
  board, and every automated criterion proves logic against the fake. **BOTH halves of what this bullet
  used to call unproven are now proven by captured live runs, and the captures are named here because
  two of them differ by one word.**
  *Provisioning* — `notes/live-provision-sc01.md`: project 7's read-back exposed GitHub's own default
  `Status` field carrying `Todo`, `In Progress`, `Done`; board 8 was then created, linked, and had its
  option set replaced with exactly the six declared stations in ONE run, removing `Todo` and
  `In Progress`; a re-run reported "nothing to do"; and a union re-run added exactly one option (`Done`)
  while the operator's undeclared `Icebox` column survived untouched.
  *Reconciliation* — it moved six cards, on board 2. `notes/migration-kaya-ai-reconcile-dry.txt`
  previews six `STATION` fixes (`#297`, `#296`, `#152`, `#83`, `#49`, `#31`, each reading `Building`
  where `Done` was expected), and `notes/migration-kaya-ai-audit-after.txt` reads `0 finding(s)`.
  Moving a card IS a thing `reconcile` does: `STATION` is in `_ALWAYS_FIXABLE_KINDS` in
  `board_lifecycle.py` and is fixed by `gh_board.set_station`.
  *Board 3 is the special case, and it is where a stale capture misled a reader.* Board 3 carried NO
  `STATION` findings, so `reconcile` moved no card there; its own two residual `Done`-status `STATUS`
  findings were resolved by hand-adding cards for `#25` and `#47`, after which GitHub's native
  `Item closed` workflow placed both at `Done` with no column write at all. **The live capture is
  `notes/migration-harness-audit-after.txt` and it reads `0 finding(s)`** (committed at `ace0b06`;
  see `notes/migration-harness.md`, *"SC-04's two residual findings, resolved by adding the cards"*).
  `notes/migration-harness-audit-after-2-accepted.txt` is the ARCHIVED EARLIER capture reading
  `2 finding(s)` — it is history, not the current state, and reading it as current is what produced a
  wrong number in an earlier draft of this very correction.
  *CORRECTED 2026-08-23 on the operator's ruling. As signed, this bullet ended:* "What is therefore NOT
  proven by any runner: that the real GitHub API accepts the provisioning mutations, and that the
  reconciliation moved the cards the operator sees." *Both halves were falsified, and both are
  corrected. An intermediate draft of this correction claimed only the first half was — that draft was
  wrong twice over, from reading the archived capture and from generalising board 3's absence of
  `STATION` findings into a claim about the tool.*
  **The general point this feature demonstrated: a verification-gap note is itself a claim, and it
  decays the moment the gap it names closes.** This one UNDERSTATED the evidence the feature holds
  rather than overstating it — the inverse of the usual failure, and the reason no reviewer flagged it.
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
feature exists to close. So: `plan` is declared for **parity** — DEC-192's six values — and **no
derivation is added for it**. The operator ruled on 2026-08-23 that the sixth station key belongs
(ruling 3, `notes/rulings-2026-08-23.md`), so the declaration is confirmed rather than inferred here,
and the parity argument is the ruling's own reasoning. Because that reverses one clause of
amendment 1, DEC-196 gains an amendment (SC-12); it is not struck.

The earlier claim that declaring the key also buys "a named key at the kickoff call site instead of a
case-sensitive literal" is **withdrawn as false** — arch-eng's B1, re-verified at `46ee87c`:
`board-station.py:74` takes `station` straight from `argv` and `:153` passes it unchanged to
`gh_board.set_station`, and no task in this plan changes that. The one call site declaring stations
does buy something is `gh-sync.py`'s hardcoded `"Building"`, which `T-07` de-hardcodes.

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

1. **Create or only validate?** **CREATE, guarded.** The harness creates the project when absent, and
   brings that board's Status field to the declared stations by ONE of three routes, chosen from what
   it reads — the third was missing from this item until 2026-08-23 and is the one the live run found:
   it creates the field when the field is absent; it adds only the missing options to an existing
   single-select field; and on a board the SAME RUN created — where GitHub has already shipped a
   `Status` field of the right type carrying the wrong options, so `createProjectV2Field` answers *"Name
   has already been taken"* — it replaces that option set with exactly the six declared stations. It
   links the repository, then reports what it cannot do. Reason: the six option names are case-sensitive
   board column names (DEC-192, byte for byte), and a human typing six of them is a silent-drift
   generator the operator only discovers when INV-26 fires.
   **Provisioning is non-destructive on every ESTABLISHED board (SC-07, as amended 2026-08-23), with
   one exception: a board the same run created, where GitHub's defaults `Todo` and `In Progress` are
   deleted. Safe there and only there — a brand-new board holds no items, so no card can lose its
   column.** *CORRECTED 2026-08-23 on the operator's ruling. As signed, this item ended:* "Provisioning
   is never destructive (SC-07)." *That sentence was falsified by the same measurement that amended
   SC-07 — project 7, owner `mruangutai`, 2026-08-23 — and it is corrected rather than ticketed because
   it sits in a scope-call, where a false line reads as reassurance and a reader who is reassured stops
   checking.*
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

**STATION and STATE are two different fields, and blurring them is what forced ruling 4.** An
issue's **state** is GitHub's own field and has two values, `open` and `closed`. A card's
**station** is the board's Status column and has six values. The lifecycle the operator confirmed
on 2026-08-23:

| Moment | Card station | Issue state |
|---|---|---|
| the plan is signed | `Ready` | open |
| work is underway | `Building` | open |
| **every sub-issue is done building** | **`Review`** | **open** |
| panel feedback resolved, the PR merges | `Done` | closed |

The issue stays open through `Review` for a mechanical reason, not a stylistic one: GitHub's native
`Item closed` workflow moves a closed issue's card to `Done` by itself, so closing at commit makes
`Review` unobservable. That is the measured reason board 3 has never held a card at `Review`.

Every station is written at the moment something happens, by whatever performs that act. The map,
with the item counts measured on board 3 across 539 items on 2026-08-22 and recorded at
`f5f5185`. Those are LIVE-BOARD readings, not tree anchors: they were not re-taken at `46ee87c`,
and board 3 has moved since — FEAT-32 shipped and `#700` is now CLOSED as `COMPLETED`.

| # | Event | What moves | Writer | Items today |
|---|---|---|---|---|
| 1 | the ticket is filed | the source ticket to `Backlog` | whoever files it | 304 |
| 2 | `/harness-plan` opens | the source ticket to `Plan` | `board-station.py`, once, at the door | 2 |
| 3 | **the plan is signed** | **every `T-NN` sub-issue to `Ready`** | the signature step | **0** |
| 4 | a task starts | that sub-issue to `Building` | `gh-sync start-task` | 5 |
| 5 | **the panel kicks off** | the parent **and every sub-issue** to `Review` | the panel dispatch, via `gh-sync.py status <dir> Review` | **0** |
| 6 | a task's commit is recorded | the task's status is recorded `done` in `plan.yaml`; **no ticket is closed and no card moves** | whoever records the commit | — |
| 7 | the PR merges | `Closes` closes **every sub-issue and the parent**; GitHub moves them to `Done` | **GitHub**, from the `Closes` lines in the PR body | 228 at `Done` today |

**`Ready` holds a feature's TASK SUB-ISSUES, so the team can pick them up. The parent is never a
claim candidate.** Sub-issues then move individually through `Ready` → `Building` → `Done`.

**The precedent is already shipped, and nothing about the factory queue changes.**
`factory_decompose.py:393` carries the comment *"The parent is NEVER added"* — on a served-repo board
only task issues get cards. So `factory_claim.py:302`'s `Status:"<stations.ready>" is:open` poll
contains only tasks **by construction**, and always has. What is wrong is the **harness lane**, which
does the opposite: board 3 carries parents as cards (22 recorded parents, measured 2026-08-22; `#700`
sits at `Building`). The work is therefore to make the harness lane behave the way the factory lane
already does about `Ready`, not to move any queue.

**`Ready` and `Review` both hold zero.** `Ready` has no harness-lane writer in the tree at all.
`Review` was reachable in principle — `close-task` on the final task derives it — and had never
fired, because the last `close-task` ran while later tasks were still `pending` and nothing called
`gh-sync` again until ship. A station that is never written is the same shape as an assertion that
cannot go red.

**Step 6 stopped being a close — the operator ruled it on 2026-08-23 and the ruling is binding.**
`gh-sync close-task` is **no longer run per commit**. A sub-issue stays OPEN through `Building` and
`Review` and closes with its parent at merge. The reason the earlier draft could not stand: a closed
card is moved to `Done` by the native `Item closed` workflow, so a sub-issue cannot hold `Review`
while it is closed — the per-commit close and the ruling that sub-issues reach `Review` were
mutually exclusive, and the operator chose `Review`. The command itself survives as the deliberate
way to close one task's ticket; only its per-commit invocation goes.

**The cost the operator accepted, recorded as they stated it.** This returns to FEAT-31's
close-everything-at-merge shape — its PR body carried `Closes` for all 19 sub-issues **and** parent
`#598` in one go — which is the shape the step-6 draft had been written to replace, because it makes
every sub-issue's `Done` depend on the merge. Under this ruling `Review` becomes reachable for a
different reason: the stations are written **explicitly**, by the act that causes them, instead of
falling out of a close.

**The one consequence that lands on a gate — RULED on 2026-08-23, not outstanding.**
INV-26 (`check-state.sh:1234`, re-derived at `46ee87c`) maps a task status of `done` to the `done`
column and compares every recorded sub-issue's card against it. That has always agreed because
`close-task` closed the ticket at commit and GitHub moved the card. With the ticket deliberately
open, **every `done` task of every in-flight feature becomes an INV-26 violation** in the gate that
runs at every `/harness` door and before every commit — this feature's own validate phase included.
There is no route around it that is honest: giving the task a status INV-26 does not map makes the
gate skip the comparison silently, and letting the violation stand teaches the operator to read
violations as noise. So the plan carries **one bounded widening of INV-26**, performed by the
operator's own hand under the DEC-174 carve-out (SC-20), and `SC-10`'s untouched-file list drops
from five to four. **That is the price of ruling 1, it was stated here rather than discovered
mid-build, and the operator ruled on it: ruling 4 fixes the gate, accepts `T-22`, `D-24` and
`SC-20` by name, accepts the four-file `SC-10`, and does not reopen ruling 1.**

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

**THE PARENT'S REMAINING STATIONS — SETTLED, 2026-08-23.** The four items below were drafted as
inferences and marked overturnable. Three are now ruled and one is rejected; nothing here is open.

1. **`Ready` on the parent is not built, on any board.** `factory_claim.py:302` polls that station
   for pickable work, so a parent sitting there is offerable work that does not exist. The operator
   ruled the parent is not a claim candidate. Settled; the `Ready` clause of the earlier inference 1
   is **not built**.
2. **`Review` on a sub-issue is REACHABLE, and the earlier reading is REJECTED.** The earlier draft
   made `Review` a parent-only station on the reasoning that a sub-issue is closed at its own commit
   and so already `Done`. The operator removed the premise instead: `close-task` no longer runs per
   commit, sub-issues stay open, and **the panel kickoff moves the parent and every sub-issue to
   `Review` together**. Every surface that rested on the parent-only reading — step 6, `REQ-08`,
   `REQ-10`, `T-13`, `T-15`, `T-19`, `T-20` — is rewritten to this shape.
3. **The ordering of the panel write and the derivation stands as drafted.** The parent derives
   `Review` when the last task finishes `Building`, which is what the operator ruled. The explicit
   write and the derivation agree on the value and differ only on the moment; the write is
   idempotent, so both are kept and neither is guarded against the other.

**The hole: a station write is REMEMBERED, not caused — AS MEASURED AT `46ee87c`, which is the
state this feature was written to fix and NOT the state today.** Pinned to a sha on purpose, and
this brief's one recorded lesson about record-keeping is why: SC-15 states the same baseline and is
still true because it says *"at `46ee87c`"*; the bare, timeless copy of that same baseline stood in
this paragraph until 2026-08-23 and had become false, falsified by this feature's own delivery. A
problem statement is a measurement, so it carries the sha it was taken at or it silently becomes a
lie the moment the problem is solved.

At `46ee87c`: the only thing in the repo that moved a card mid-build was one row of a markdown table
in `.claude/skills/harness/SKILL.md`, addressed to the **orchestrator**. `main-session-direct` tasks
are forbidden to the orchestrator by DEC-174, and nothing anywhere instructed the main session to
move their cards; the only mention of `main-session-direct` in that file was the one about run
counting — `grep -c` returned 1. FEAT-32 carried **9 of 17** tasks in that mode. Its cards read
correctly only because the merge's `Closes #N` closed the issues and GitHub's own `Item closed`
workflow moved them — **the only station that self-heals is the one GitHub writes.** Its parent
`#700` read `Building` while its `feature.json` status read `Review`.

**What is true at `8dfee3b`, re-derived 2026-08-23 rather than assumed:** `grep -c
"main-session-direct" .claude/skills/harness/SKILL.md` returns **3**, and two of those are the
subcommand-owner rows `T-14` added, which assign the owner **by `execution_mode`** and name the main
session explicitly — one for `start-task` on a `main-session-direct` task, one for a phase
transition it holds itself. So the hole this paragraph describes is CLOSED for the surface `T-14`
touched. FEAT-32's `9 of 17` still holds (re-counted from its `plan.yaml`), and its
`feature.json` status now reads **`Done`**, not `Review` — that feature shipped. Its parent card's
column is NOT re-read here: no live GitHub call is made from this brief, and the last recorded
reading is SC-16's, which records `#700` CLOSED as `COMPLETED` at `46ee87c`.

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
  extra network call. **That comparison finds two live cards nothing else sees, and both are still
  live at `46ee87c` — `gh issue view` reports each still OPEN and each `feature.json` still reads
  `Done`:** `#85` (FEAT-08) and `#98` (FEAT-09) are **OPEN** parents whose `feature.json.status` reads
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
only ever contained tasks. Both re-derived at `46ee87c`; `factory_decompose.py:393` and
`factory_claim.py:302` still resolve exactly as cited.

**The stated cost, narrowed to what is actually lost: board 2 loses the HUMAN promotion signal, not
the column.** kaya-ai's own `.harness/harness.json` on `master` documents `Ready` as the human
pick-up point; after this, a card arrives there because a plan was signed, and nothing on board 2
records that a human chose to promote a ticket. A visible label is the route if that signal turns out
to be needed — the same shape as the `abandoned` label already chosen — and it is **NOT** built here.

**What the harness lane must stop doing:** it must never write `Ready` to a **parent** card, on any
board. That is the one thing it copies from the factory lane.

## Constraints

**These SUPPLY the mechanism this feature builds on:**

- **DEC-186 + am.1 + am.2 — SETTLED, and it SUPPLIES the fourth read this feature needs.** GitHub
  Issues and one board per repository served are the control plane. The architecture review was right
  that reading a project's workflow list is a FOURTH read-back purpose and that re-categorising it as
  *configuration* was not a legitimate route; the operator ruled on 2026-08-23 to **widen rather than
  drop REQ-02**, and **amendment 2 is already written on `main`** — commit `e3392fd`, issue #724,
  pull request #725 — recording the bound as FOUR purposes, with the fourth being a board's native
  workflow list, read at `/harness-init` only and report-only. This branch **merges** that amendment;
  it authors none. **The merge has happened and amendment 2 is IN THIS TREE. Re-measured at `57e18ca`:** the main
  session merged `main` into this worktree (`e3392fd` PR #725 and `3ed95a4` PR #729 both arrived),
  `git rev-list --count HEAD..origin/main` is **0**, `DECISIONS.md` carries
  `### DEC-186 amendment 2 (2026-08-23) — the read-back bound widens to FOUR`, and
  `DECISIONS-INDEX.md:204` now reads `am.1-am.2 ... bounded to four purposes, am.2's being
  /harness-init's workflow read`. Nothing here authors an amendment. `T-09` and `T-19` amend
  **DEC-196**, not DEC-186, and both regenerate the index with `gen-decisions-index.py`, whose
  contract preserves everything right of ` :: ` verbatim — so neither collides with amendment 2 nor
  duplicates it. `REQ-02`, `T-03`'s `project_workflows` primitive, `T-05`'s WORKFLOW finding class,
  `T-10` and `SC-12` therefore all stand exactly as drafted. Reading a Status field's option set is
  unaffected either way — resolving an option name to an option id *is* DEC-186's second purpose.
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
  designed to need **one** edit to one of them, and exactly one: `check-state.sh`'s INV-26 indexes
  only the `building`, `done` and `backlog` station keys (`_EXPECT` at `check-state.sh:1234` —
  re-derived at `46ee87c`, where the earlier `:1184-1185` anchor had MOVED), so the sixth *station
  key* is inert there. What is **not** inert is the operator's ruling of 2026-08-23: a `done` task
  with a deliberately open sub-issue fails INV-26's per-task comparison, so INV-26 is widened, once
  and narrowly, by the operator's own hand (SC-20) — ruled 2026-08-23, ruling 4. Worth recording: `check-domain.sh --resolve`
  grants `check-state.sh` to `harness-backend-dev` and `harness-dev-ops` while DEC-174 forbids
  dispatching a change to it. The carve-out wins — no squad executes this edit.
- **`mruangutai/harness` is deliberately ABSENT from `fleet.yaml`** (DEC-174 am.1) and is not added.
- **Six paths in this feature have no dispatchable owner** and are declared
  `main-session-direct` in the plan: `.claude/skills/harness-init/SKILL.md`,
  `.claude/skills/harness/SKILL.md`, `.claude/commands/harness-plan.md`,
  `.claude/skills/harness/templates/harness.json` and kaya-ai's own `.harness/harness.json` all
  resolve to NOBODY — every one re-derived with `check-domain.sh --resolve` at `46ee87c` — and a
  generic file under this feature's `notes/` resolves to `harness-orchestrator`, which is not a task
  executor. `check-state.sh` is the seventh main-session path and the only one that resolves to a
  real agent; DEC-174 overrides the grant.
- **No hook is added, changed or registered.** DEC-174's carve-out forbids executing a change to the
  enforcement layer, and the only genuinely *caused* write available there — a `PostToolUse`
  `Write|Edit` hook firing a board read — costs a measured 490–506 GraphQL points per fire on board 3
  and would fire on every edit in every session. SC-10's untouched-file list is therefore **four,
  not five**: `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py` and
  `check-plan-routes.py` are untouched, and `check-state.sh` carries the single bounded INV-26
  widening ruling 1 forces (SC-20), performed by the operator and by nobody else.
- **A cross-repo ordering cost, stated rather than discovered.** The one board validator in the tree
  tests the declared station keys for **exact set equality** (`factory_config.py:134`). So widening the
  required set to six and updating kaya-ai's `master` cannot be atomic, and between the two merges
  `board_for('mruangutai/kaya-ai')` raises `FleetError` naming `github.board.stations`. The breakage is
  **latent, not live** — nothing calls it unless a `factory_*` command is run against kaya-ai — and the
  failure is loud and names its own fix. Accepted, and the plan orders the kaya-ai config change first
  so the window closes in the direction of correctness. This is the one place the plan departs from
  "harness first"; the harness-first ordering the operator set governs the **migration**, which is
  unchanged.
- **Concurrency, re-derived at HEAD rather than carried forward.** **Re-measured at `57e18ca`:**
  `main` was merged into this worktree, `git rev-list --count HEAD..origin/main` is **0** and
  `origin/main..HEAD` is 9. FEAT-31 and FEAT-32 have **shipped** (both `feature.json` `Done`).
  **FEAT-26 has NOT** — what merged was its plan's *signature* (`2c0a33c`); its `feature.json`
  reads `Ready`, its `plan.yaml` is `approved 2026-08-23` and **all eight of its tasks are
  `pending`**. Its `T-05` writes `check-state.sh` and `test-check-state.py` — the exact two files
  `T-22` writes — its `T-02`/`T-03`/`T-04` write `gh-sync.py` and `test-gh-sync.py`, its `T-08`
  writes `DECISIONS.md` and the index, and its `T-07` writes `.claude/skills/harness/SKILL.md`.
  Nothing about that makes either plan wrong, and the two build in separate worktrees; **whichever
  builds second re-derives its line anchors by symbol** — `T-22`'s intent now says so explicitly.
  Which of the two builds first is a scheduling call, not a change to either plan.
  `run-unit-tests.sh`, `check-state.sh`, `check-domain.sh`, `harness.json` and `DECISIONS.md` all have
  other writers. **Measured at `46ee87c`:** `git diff --name-only origin/main...HEAD` returns only
  files under `features/FEAT-33-board-lifecycle-native/`, and the same command at `57e18ca` returns
  the same set, so none of those merges landed on a surface this plan reads in a way this branch has
  not already absorbed. **What the merge actually changed, measured `git diff --stat 46ee87c
  57e18ca`: `feature-worktree.py`, `test-feature-worktree.py`, `DECISIONS.md` and
  `DECISIONS-INDEX.md`, and nothing else** — no anchor in this plan points into the first two, and
  `check-state.sh` and `test-check-state.py` were not touched at all, so every `T-22`, `D-24` and
  `SC-20` anchor re-derived at `46ee87c` still resolves byte for byte at `57e18ca`. Every code
  anchor in `plan.yaml` and in this brief was re-resolved at `46ee87c`, and the ones that had MOVED
  are corrected: INV-26's
  `_EXPECT` (`:1184` → `:1234`), `check-state.sh`'s `load_board` call (`:1147` → `:1197`),
  `factory_decompose.py`'s ready write (`:411` → `:414`), `_apply_parent_rule` (gh_board.py → 
  `gh-sync.py:177`), and the `integration` list counts (six/fourteen → 22/22). What this plan
  still touches with another writer, and must rebase against: **one line of `run-unit-tests.sh`**
  (registering `test-board-lifecycle.py` in `UNIT_SCRIPTS`, which the drift detector at `:41-55` makes
  mandatory — an unregistered `test-*.py` exits 2 `MISCONFIGURED` and breaks every `verify:` in this
  plan at once), `DECISIONS.md`, and `harness.json` — but `harness.json` is now touched by **T-02
  alone**, and only to add `"plan": "Plan"` under `github.board.stations`. T-04 no longer lists it: the
  `test_kinds.unit.detect` glob `.claude/skills/harness/bin/test-*.py` already matches the new test file
  (`harness.json:105`), so the `detect` entry T-04 was going to consider adding is redundant, and a
  listed-but-unwritten path in a three-writer file only invites a gratuitous edit.

## Approval

status: approved
