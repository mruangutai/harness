# BRIEF — FEAT-18 Board truth during a build

## Problem

The board is the operator's view of what the factory is doing, and during a build it is the one
surface that stops telling the truth. FEAT-14 spent its entire build with nine finished tasks
sitting in `Backlog` beside the two that were running; the columns were corrected by hand on
2026-08-12 and nothing prevents the next feature from repeating it. The failure points the
safe-looking way — every issue exists, every title is right, the columns simply never move — and it
is invisible from the outside, because a mirror that never ran and a mirror that ran cleanly are
indistinguishable. Measured: `gh-sync.py` contains no station-writing code at all, and every card
the harness has ever landed in `Done` was moved by GitHub's own `Item closed` workflow, not by the
harness.

## Goal

During a build, the harness board says what is actually happening: a task in flight shows
`Building`, a finished task shows `Done`, and the feature's own card follows its tasks. A sync that
does not happen is loud rather than silent, and a board that has drifted out of agreement with the
plan on disk is reported at the start of the next session rather than discovered by hand.

## Requirements

- REQ-01: A task that is in flight is distinguishable, on the board, from one nobody has started.
- REQ-02: A task's card moves at the moment its status changes, not replayed after the build.
- REQ-03: The feature's own parent card shows the feature's station, and that station is computed
  from its tasks rather than tracked as a second record.
- REQ-04: A station or status write that fails says so loudly, and the run it is part of continues.
- REQ-05: A board that disagrees with the plan on disk is reported at session entry, naming the
  feature, the task and the two values that disagree.
- REQ-06: Exactly one place in the harness moves a card on the harness board.
- REQ-07: No text the harness composes into a pull request body closes a GitHub issue. The tie
  between a build branch and its feature's issue is not something the harness writes.
- REQ-08: Every sync point in the orchestrator's own table names the actor that fires it.

## Success Criteria

- SC-01: Marking a task `building` moves that task's sub-issue card to the `Building` column.
  Proven against a recorded fake `gh` that captures the field-set call, so the column name and the
  item id are both asserted, not merely the fact that a call happened.
  **Amended 2026-08-13, at operator re-signature.** The clause originally also read "and closing
  the task lands its card in `Done`" under the same proof standard. That half was unprovable by its
  own signature: D-03 and T-03 forbid the harness from writing a `Done` station, so no field-set
  call exists for a fake `gh` to capture. The card reaches `Done` through GitHub's own `Item closed`
  workflow, which this feature neither owns nor asserts. The criterion now claims only the half the
  harness performs. This is a correction to the text, not a weakening of delivery — the behavior
  never changed.
  verify: automated      evidence: integration
- SC-02: The parent card's station is a function of task statuses alone — any task `building` gives
  `Building`, all tasks `done` gives `Review` — and changing a task's status in the plan changes the
  parent's target column with no other file edited. A feature whose `feature.json` records
  `status: Done` is exempt and gets no parent write.
  verify: automated      evidence: integration
- SC-03: With a working `gh`, a station write that the API rejects prints a line on **stderr**, the
  invocation carries on to its remaining writes, and the process still exits 0; with `gh` absent or
  unauthenticated the invocation prints one `SKIP` line and exits 0 as it does today. Both halves
  are asserted from one fixture, because the failing half alone is satisfied by a tool that has
  stopped writing anything.
  verify: automated      evidence: integration
- SC-04: No station write, issue write or board read is re-attempted after a failure, anywhere on
  the `gh-sync.py` path. Retry was dropped deliberately; a single re-attempt counts as a violation.
  verify: inspection
- SC-05: A feature whose plan records a task `done` while that task's sub-issue card still sits in
  `Backlog` is reported as a violation at session entry, naming the feature, the task, the plan's
  status and the column found. **Proven non-vacuous by a deliberately mis-columned fixture:** the
  same fixture, with only that one card's column corrected to `Done` and nothing else changed, makes
  the check report clean — so the check is failing on the disagreement and not on the fixture. A
  check that fired on both, or on neither, fails this criterion.
  verify: automated      evidence: integration
- SC-06: A plan task carrying a status outside `pending | building | done` — including `Building`
  with a capital B, which is the board's spelling and therefore the likely typo — is a violation of
  `check-plan-routes.py`, and every one of the live plans still passes it.
  verify: automated      evidence: integration
- SC-07: `branch-create-gate.sh` no longer contains board-moving code or any read of the four board
  config keys, and it still denies a branch naming a flow that does not exist on disk. The second
  half is checked by running the gate, not by reading it: a deletion that also disabled the gate
  would pass an absence check on its own.
  verify: inspection
- SC-08: **STRUCK 2026-08-13, before signature** (DEC-188 shape — the entry stays so a citation
  still lands). It asserted that this feature's own build branch appears as a linked branch of its
  parent issue, read back with the `linkedBranches` query. The build branch is now created the
  ordinary way, `git checkout -b feat/FEAT-18-board-truth`, and nothing links it to the issue — so
  the criterion is false by design rather than unmet. Two measured breaks forced it: the
  `gh issue develop` route bypasses `branch-create-gate.sh` entirely, and a linked-branch PR closes
  its parent issue on merge with no closing keyword, which with board 3's enabled `Auto-close issue`
  and `Item closed` workflows would land the parent card in `Done` mid-build. Both were measured, not
  predicted — `notes/answers-2026-08-13-revision.md`.
  verify: none — struck
- SC-09: The orchestrator's sync-point table lists every `gh-sync.py` subcommand the harness has,
  each with a named owner, and states how the build branch is created.
  verify: inspection

## Verification gaps

- **`functional` has no runner** (`cmd: null`, excluded by DEC-187). This feature crosses a process
  boundary on every path it adds — it shells out to `gh`. Every `automated` criterion above
  therefore runs against a **fake `gh` binary**, not against GitHub. What is NOT proven: that the
  GraphQL queries, the field name `Status`, the six option names and the item-id lookup behave as
  measured when run against the live API. What carries it instead: the measurement recorded in
  `.harness/notes/research-FEAT-18-board-truth.md` (board 3's six options read back at `2ccd7f0`),
  and the operator's own eyes on the board during the first build after this ships.
- **What striking SC-08 costs, stated rather than dropped.** SC-08 was the only criterion in this
  feature that touched the live GitHub API, so after the strike **no criterion here observes GitHub
  at all** — the roster above went from three carriers to two, and one of the two is a human looking
  at a board. That is the honest loss. It is smaller than it reads, and the reason is checkable:
  SC-08 read back `linkedBranches` on an issue, which is a different query surface from the
  `projectV2` field-set the automated criteria fake. It never proved the field name `Status`, the six
  option names, or the item-id lookup — the three things the gap above actually names. So the strike
  removes a live-API criterion without removing coverage of any behaviour this feature still has: the
  linked-branch behaviour it graded no longer exists to be graded. No replacement criterion is
  invented, because there is nothing left for one to observe.
- `component`, `ui`, `eval` and `typecheck` all have `cmd: null`. None of them covers a surface this
  feature touches; no criterion rests on them.

## Constraints

- **Scope is the HARNESS board only** — board 3, `github.repo: mruangutai/harness`.
- **Retry stays dropped.** Not reintroduced in any form, including a single re-attempt.
- **`feature.json`'s schema is CLOSED** — eleven keys, `additionalProperties: false` (DEC-191). No
  new key. Everything needed to compute a mis-columned card already exists offline, in `plan.yaml`'s
  task statuses and `feature.json`'s `github.issues` map.
- **Read-back is bounded** (DEC-186): reading a card's station is the second of that decision's
  three closed purposes, and nothing read back is written into `BRIEF.md`, `plan.yaml` or any
  approval block.
- **`check-state.sh` is a DEC-174 carve-out.** The session-entry check is not built through a team
  run whose gates are the thing being changed.
- Changes to the orchestrator's own procedure land in `.claude/skills/harness/SKILL.md`, which no
  agent domain grants — a declared main-session step (DEC-179).

## Out of scope — a hard fence

- **Product boards.** `factory_claim.py` has the same failure shape, and it is inside FEAT-16's
  signed plan. Two features editing the same station code in sequence is the split-then-collide
  shape. Tracked as **#278**, waiting on FEAT-16. Nothing in this feature touches
  `factory_claim.py`, `factory_decompose.py`, `factory_land.py` or `fleet.yaml`.
- **Composing `Closes #N` into a PR body.** Declined by the operator, and it stands on his standing
  preference alone — which is what it always stood on. Nothing replaces it: the build branch is now
  created the ordinary way and is not linked to the issue either. The parent issue is closed by
  `gh-sync.py ship`, which already closes it and already posts the ship review on it, so no
  harness-composed closing text is needed and none is written.
- **Teaching `branch-create-gate.sh` to parse `gh` subcommands.** The gate covers four `git` forms
  and nothing else. Striking SC-08 closes that gap by not opening it — the build branch is created
  with a form the gate already extracts — so no parsing work is in this feature.

## Approval

status: approved
approved_by: Mike Ruangutai
date: 2026-08-13

Signed by the main session on the operator's instruction ("sign feat-18 when it comes back"), after
the revision that struck D-08 and SC-08. Three things were settled at signature and are recorded
here rather than left to be inferred.

**Q1 — answered, but not as it was asked.** The question was whether the operator's fence on
`branch-create-gate.sh`'s four config keys covers D-05's three. He did not rule on the fence. He
raised a larger objection instead:

> `harness.json` holds harness **runtime** metadata. Project, repo and GitHub data belongs with the
> product, and `fleet.yaml` is the more accurate place for project-level data. The two files hold
> redundant data today, and that redundancy is the defect.

**Ruling on placement: D-05 STANDS. The three board keys stay in `harness.json` for this feature**,
and their placement is knowingly temporary. `#206` moves `github`, `test_matrix` and `test_kinds`
together in one migration rather than this feature moving one key ahead of the rest. He declined a
`DECISIONS.md` entry for the principle on the ground that `#206`'s planning will state it more
precisely; it is recorded in `.harness/notes/grilling-central-product-config-2026-08-12.md` instead,
along with the obstacle it runs into — `mruangutai/harness` is deliberately absent from `fleet.yaml`
and the absence is the mechanism (DEC-174 am.1).

**Two of D-05's three keys were challenged at signature and survive only because the migration is
coming.** `owner` is derivable — `github.repo` is already `mruangutai/harness` and the owner is the
segment before the slash. `station_field: Status` pins a field *name* when DEC-192 already prescribes
the six *values*, which is the same silent-staleness shape FEAT-16's ship review flagged as
unguarded. Both are recorded in `#206`'s artifact with an instruction to decide **per key**. Neither
is a defect of this plan; both are reasons the migration should not be deferred indefinitely.

**Q3 — settled by the main session.** D-08's strike record stays in its own `struck:` key rather than
folded into `choice:`. Nothing reads `plan.yaml`'s `decisions:` block, so both forms are equally
inert; a separate key is the more legible of the two and does not bury the strike inside prose.

**REQ-07 restated rather than struck — accepted.** The orchestrator's own technical judgement, taken
without advisor review (the advisor was unavailable on both attempts). Its surviving half — no text
the harness composes into a pull request body closes a GitHub issue — is true, is the operator's
standing preference on `Closes #N`, keeps the plan at 8 REQ, and keeps T-06's `traces:` resolving.

**What this signature knowingly accepts.** No criterion in this feature observes GitHub. Every
`automated` criterion runs against a fake `gh` binary because `functional` has `cmd: null`
(DEC-187), and striking SC-08 removed the only live-API criterion. What carries it instead is the
board-3 measurement recorded at `2ccd7f0` and the operator's eyes on the board during the first build
after this ships. That is stated in `## Verification gaps` above and was read before signing.
