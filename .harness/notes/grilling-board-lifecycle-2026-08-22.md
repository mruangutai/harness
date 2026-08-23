# Grilling — the board's whole lifecycle, native-first — 2026-08-22

## Destination

A repository joins the harness fleet and its GitHub board is correct from that moment: the project
exists, the Status field carries every station the harness uses, cards move to the right station
without a human, and a shipped ticket closes with the right reason. Existing projects — harness
first, then kaya-ai — are brought to that same shape. Wherever GitHub already does the job natively,
the harness uses it rather than reimplementing it.

## Settled

- **Native features first, everywhere they reach.** The operator's framing: "i'd hate to reinvent the
  wheel here, if we can use github's native features to attach a PR, set the ticket/issue station to
  Done, and close the ticket."
- **Four things this effort owns.** Creating the board and its Status field when a repo joins the
  fleet; repairing the station map and adding an `Abandoned` station; native closing end to end; and
  migrating the two existing projects, **harness first as the proving ground, then kaya-ai**.
- **Board workflow detection belongs at `/harness-init`, once — NOT in `check-state.sh`.** Operator's
  ruling, with the reason: `check-state.sh` runs at every `/harness*` door and before every commit, so
  a network call there fires dozens of times per build, which is the waste FEAT-29 exists to remove. A
  workflow being switched off later is a real risk and a near-zero one, so a one-time configuration
  check belongs at the one-time configuration step. **Accepted cost, stated rather than discovered:
  between one init run and the next, a switched-off workflow is invisible.**
- **`Abandoned` is carried by the ticket, not by a sixth column.** Operator chose to read
  `state_reason` rather than add a station — *and* to apply a visible `abandoned` label, "for visible
  clarity", so a human reading the board sees it without opening a field.
- **This is FEAT-33, not an expansion of FEAT-26.** FEAT-26 keeps its own subject — the *record*: the
  `pr` field, the source tickets, and the `Closes` renderer. Offered as one feature and declined, so
  that FEAT-26's nearly-signable value does not wait behind a cross-repo migration.

## Not yet specified

- Whether the harness should CREATE a board for a repo that has none, or only validate one the
  operator made. `createProjectV2` exists, so both are possible; which is right is a product call.
- What the station map should be canonically. The board carries six options and `harness.json`
  declares five — so "correct" needs defining before it can be asserted.
- How a migration proves it finished. Reconciling cards already sitting on the wrong station needs a
  definition of the right station for a card whose feature is long done.
- Whether kaya-ai's board should match harness's station set exactly, or only satisfy the same
  contract. Its board and station rationale live in its own `.harness/harness.json` on `master`,
  deliberately not restated in `fleet.yaml`.
- Whether the `abandoned` label is created by the harness or expected to exist. `ensure_labels` has
  three separate implementations with three different error policies today.

## Out of scope

- **FEAT-26's subject.** The `pr` field, recording source tickets, and rendering `Closes #N` lines.
  Already planned there, one round from signable.
- **Enabling the three Projects v2 workflows.** Not a scope decision — see Facts. It is impossible.
- **Any repository other than harness and kaya-ai.** `fleet.yaml` declares only kaya-ai, and harness
  is deliberately absent from it (DEC-174 am.1) because it develops itself in its own checkout.

## Facts I verified (so pm does not re-derive them)

Measured at `d065b3b` unless stated.

- **There is NO API to enable a Projects v2 workflow.** All 32 `ProjectV2` GraphQL mutations include
  `deleteProjectV2Workflow` and nothing that creates or enables one. `copyProjectV2` accepts only
  `projectId`, `ownerId`, `title`, `includeDraftIssues` — no workflow argument. `ProjectV2Workflow`
  exposes `enabled`, `name`, `number`, `createdAt`, `updatedAt`, `id`, `fullDatabaseId`, `project` —
  **not its trigger and not its action**, so the harness cannot even read what a workflow does. Board 3 carries EIGHT
  workflows, seven enabled and one off (`Pull request linked to issue`); the ones that matter here
  were enabled by hand through the web UI because clicking is the only way. Filed as
  **#673**.
- **Almost everything else IS reachable by API**, which is what makes this effort worth doing:
  `createProjectV2`, `createProjectV2Field` and `updateProjectV2Field` both take
  `singleSelectOptions`, plus `linkProjectV2ToRepository`, `addProjectV2ItemById` and
  `updateProjectV2ItemFieldValue`. Field and option creation, board creation, repo linking and card
  movement are all automatable. Only the workflow toggles are not.
- **The station map is already wrong.** Board 3's `Status` field carries six options — `Backlog`,
  `Plan`, `Ready`, `Building`, `Review`, `Done`. `harness.json`'s `github.board.stations` declares
  five and **omits `plan`**. So `gh_board.derive_station` can never return `Plan`; only a literal
  `board-station.py <n> Plan` reaches it, because that tool passes the station string straight to
  `set_station` without consulting the map. Two paths to a station, one mapped and one not.
- **A closed ticket did not fix its own subject.** #453 is titled "The board never shows Plan: the
  station is unmapped and no workflow…" and its `state_reason` is `COMPLETED`. The mapping is still
  missing.
- **The native chain works where it is enabled.** 512 board items; after a repair I made today, **226 of 226** closed items sit at `Done`. `Item
  closed` and `Auto-close issue` produce that — and ONLY those two, because the board holds no pull
  request at all, so `Pull request merged` cannot be the cause.
  Measured on PR #491: its body carried `Closes #417/#430/#453`, GitHub's `closingIssuesReferences`
  returned exactly those three, and all three closed within two seconds of the merge at 12:54:54Z.
  **So the keyword is not a convenience over an automation — it IS the automation.**
- **The harness enables none of it.** `grep` for `projectV2Workflow` across every script in
  `.claude/skills/harness/bin/` returns zero, and `harness-init/SKILL.md` installs eight
  prerequisites with no board workflow among them. **Therefore the harness's own station write is
  load-bearing on a served repo** — deleting it would freeze those boards silently. I nearly argued
  for removing it on reliability grounds; that argument generalised from a hand configuration the
  harness does not create.
- **`Abandoned` already reaches GitHub, but not the board.** `gh-sync.py:674` and `:688` close with
  `state_reason=not_planned`. Three items carry it (#349, #357, #358) and **all three sit at station
  `Done`**, indistinguishable from a shipped ticket.
- **`start-task` drives a closed card backwards, and it caused every board error on this project.**
  `gh-sync.py:615` guards only `if tid not in rec["issues"]` and never checks issue state. Timeline
  of #642: closed 01:37:47, `github-project-automation[bot]` set `Done` at 01:37:48, then the harness
  set `Building` at 02:34:21. #643 identical. Filed as **#674**; a guard is owed.
- **`ensure_labels` has three implementations** — `factory_gh.py:186` (`--force`, propagates),
  `gh-sync.py:520` (swallows errors, own colour map), `wayfind.py:99` (lists first, honours dry-run).
  `factory_gh`'s `--force` overwrites whatever colour `gh-sync` set. Relevant because the
  `abandoned` label has to be created by something.
- **There is no `gh project field-edit`.** The CLI offers `field-create` and `field-delete` only, so
  creating a Status field with every station option is one call while ADDING an option to the existing
  field is unreachable from the CLI — that needs raw `gh api graphql` with `updateProjectV2Field`,
  because delete-and-recreate drops every card's value. `gh project` has no workflow command at all,
  a second surface agreeing that enablement is not automatable.
- **Of four merged PRs sampled, only #491 carried a closing keyword.** #452, #451 and #415 return
  empty `closingIssuesReferences` — three merges that closed nothing. That is the forgetting this
  effort's sibling FEAT-26 exists to end, measured rather than asserted.

## Operator rulings on the station lifecycle — 2026-08-22, later

The whole map becomes EVENT-DRIVEN, not derived. Every station is written at a moment something
happens, by whatever performs that act. That is the same conclusion the day's other finding forced:
a station write must be CAUSED, never remembered.

1. **`Backlog`** — the ticket is filed and untriaged. Written at creation.
2. **`Plan`** — written ONCE at the `/harness-plan` door by `board-station.py`. NOT derived.
   Deriving it from all-pending would fire on every mirror call and overwrite a promoted card.
3. **`Ready` — OPERATOR RULING: written when the PLAN IS SIGNED.** Not a human promotion, and not
   derived. The signature is the event. This REPLACES the "promoted for the factory" meaning the
   board-2 rationale documents, and that conflict is real rather than cosmetic — see below.
4. **`Building`** — derived today from `plan.yaml` (any task `building`), written by
   `gh-sync start-task`, which then re-derives the parent.
5. **`Review` — OPERATOR RULING: written when the VALIDATION PANEL KICKS OFF.** Not derived from
   all-tasks-done. This is strictly better than the current rule because the current rule never
   fires: measured 2026-08-22, board 3 holds ZERO items at `Review` across 539 items, because cards
   reach `Done` at merge before an all-done derivation is ever consulted. An unreachable station is
   the same shape as an assertion that cannot go red.
6. **`Done`** — GitHub writes it. `Closes #N` closes the issue at merge and the native `Auto-close
   issue` workflow sets the station. Verified on PR #698: 20 of 20, no harness write involved.

`Abandoned` remains NOT a station: `state_reason: not_planned` plus a visible `abandoned` label.

### The conflict ruling 3 creates, stated rather than discovered later

`Ready` currently carries a DIFFERENT documented meaning on board 2 — `Backlog` = filed-and-untriaged,
`Ready` = promoted for the factory — and that rationale lives in kaya-ai's own `.harness/harness.json`
on `master`, deliberately not restated in `fleet.yaml`. Making `Ready` mean "plan signed" on board 3
either diverges the two boards or re-defines board 2's column under it. **Which of those is intended
is not settled here.** It is the first question of the migration half.

### What still has no writer

`Building` is the only derived station left, and its writer is `gh-sync start-task` — which the
orchestrator is instructed to run, in prose, in a markdown table. Nine of FEAT-32's seventeen tasks
are `main-session-direct`, forbidden to the orchestrator by DEC-174, and NOTHING instructs the main
session to move their cards. All five of the ones built on 2026-08-22 sat at `Backlog` while
`plan.yaml` said `done`; `check-state.sh` INV-26 caught it only after the fact. A station write that
depends on an agent remembering a table row is not a mechanism.

### The `Ready` conflict is SETTLED: one meaning, both boards

**Operator ruling: `Ready` means THE PLAN IS SIGNED, everywhere.** Board 2's "promoted for the
factory" meaning does not survive, and its promotion signal keeps no column.

The reason is the one FEAT-33 exists for: two boards using the same column name for different states
is how a migration silently corrupts a card, and REQ-02's subject is the harness asserting ONE
correct station map. A per-repo meaning makes that assertion impossible by construction.

**The cost, stated: kaya-ai loses a signal it currently has.** Its own `.harness/harness.json` on
`master` documents `Ready` as the human pick-up point. After this, nothing on board 2 records that a
human promoted a ticket. The migration half has to say so out loud rather than let the column change
meaning under whoever reads it next. If that signal turns out to be needed, a visible label is the
route — the same shape as the `abandoned` label already chosen — but that is NOT being built here.
