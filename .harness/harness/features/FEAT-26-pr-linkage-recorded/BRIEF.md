# BRIEF — FEAT-26 PR linkage recorded

Source ticket: #492 (split out of #277 on 2026-08-18; #277's board half shipped in FEAT-18). Not
part of effort #336, no unit number.

## Problem

A merged feature and an unmerged one look identical on disk. `feature.json` carries a `pr` field
that FEAT-14 made **required to be present, not required to be true**, and nothing in the harness
writes it for a harness feature — the only `pr create` in the tree is
`.claude/skills/harness/bin/factory_land.py:67`, the product-repo path. The field was filled by
hand, and the hand stopped: **eleven of the twenty-two `Done` features carry `pr: null`**
(FEAT-01, 02, 03, 04, 05, 08, 10, 20, 21, 22, 23 — measured at `ada8e99`). To find the PR that
shipped a feature the operator searches GitHub by hand.

The second symptom is the closing keyword. `Closes #N` in a PR body is what moves the source
tickets to `Done`, and it is typed every time — PR #491 carried `Closes #417. Closes #430.
Closes #453.` because the operator typed them. It cannot be otherwise today: **the source ticket a
feature was planned from is recorded nowhere machine-readable.** `feature.json`'s `github:` block
holds `milestone`, `parent`, `parent_origin`, `attached` and `issues`, and none of them is the
ticket the plan came from. Verified on FEAT-23: its sources #417, #430 and #453 appear only in
prose.

A field maintained by habit reports success while doing nothing.

## Goal

A feature that ships records the pull request that shipped it, without anyone remembering to type
the number; and the tickets a feature was planned from become data the harness can read, so the
closing keywords for a PR body are produced from the record rather than recalled. The harness still
does not open the PR — that seat stays the operator's (DEC-153) — and it does not post or close
anything on the operator's behalf.

## Requirements

- REQ-01: A shipped feature's pull request number is present in its execution state without any
  person having supplied the number.
- REQ-02: The GitHub tickets a feature was planned from are readable from that feature's own files
  by a program, and they are what the operator signed at plan approval.
- REQ-03: The closing keywords for a feature's source tickets are produced from the recorded data
  rather than recalled, in a form the operator can put into the pull request body they open.
- REQ-04: A shipped feature whose pull request number is missing is visible to the operator instead
  of silent.
- REQ-05: The eleven already-shipped features whose pull request number was never recorded carry
  it, and the eleven that already carried one are unchanged.
- REQ-06: A feature that genuinely has no source ticket, and a feature planned before this
  mechanism existed, continue to work — nothing new is required of them.

## Success Criteria

- SC-01: Running the recording seat against a shipped feature whose recorded branch has exactly one
  merged pull request writes that number into `feature.json`'s `pr`, with no number supplied by the
  caller.
  verify: automated      evidence: integration
- SC-02: When the recorded branch resolves to zero merged pull requests, or to more than one, the
  seat leaves `pr` unchanged, prints one line naming which case it hit, and exits 0. Both cases are
  exercised; `feat/harness-native-foundation` really does carry two.
  verify: automated      evidence: integration
- SC-03: A `pr` that already holds an integer is never overwritten by the seat, on any path,
  including when a different number would be derived.
  verify: automated      evidence: integration
- SC-04: The source tickets recorded in `feature.json` survive a full `open` run — every
  `save_recorded` call the run makes, not just the last one. The test drives more than one save.
  verify: automated      evidence: integration
- SC-05: The schema ACCEPTS a `feature.json` carrying the new source-tickets key as a list of
  integers, and REJECTS a non-integer member of that list, and REJECTS an undeclared sibling key
  next to it. All three fixtures exist, and the two rejecting ones are shown to fail before they are
  shown to pass.
  verify: automated      evidence: unit
- SC-06: The renderer emits exactly one `Closes #N` line per recorded source ticket, in the recorded
  order, and emits nothing at exit 0 when the list is absent or empty. It never posts anything to
  GitHub.
  verify: automated      evidence: integration
- SC-07: A `Done` feature with a null `pr` produces its own named line from `check-state.sh`, and a
  `Done` feature with an integer `pr` produces none. The fixture proves the line can appear before
  it proves it can be absent.
  verify: automated      evidence: integration
- SC-08: After the backfill, each of the twenty-three features this plan enumerates carries exactly
  the expected `pr` value, asserted **one feature id at a time** — the eleven backfilled to their
  named numbers, the eleven already-recorded to the numbers they already held, and FEAT-19
  (`Abandoned`, never built) still null. A count or a whole-file search does not satisfy this.
  Features still in flight when this plan was written are deliberately outside the assertion:
  another orchestrator owns them and their state moves under this feature.
  verify: inspection
- SC-09: A run of `check-state.sh` on the shipped tree reports no line from the new invariant
  naming any of the features this plan enumerates.
  verify: inspection
- SC-10: This feature's own plan records #492 as its source ticket, its own `feature.json` carries
  it after `open` runs, and the renderer emits `Closes #492` for it — the mechanism's first
  consumer is itself.
  verify: inspection
- SC-11: A feature planned before this mechanism existed, whose plan carries no source tickets at
  all, still syncs and still ships: nothing new is required of it and no new failure appears.
  verify: automated      evidence: integration

## Verification gaps

None. Both kinds these criteria rest on — `unit` and `integration` — are `status: active` with a
real `cmd` in `.harness/harness.json` `test_kinds`, and all three test files this feature touches
are already registered in `run-unit-tests.sh`'s explicit lists. No surface here is covered only by
a `cmd: null` kind.

## Constraints

- **The harness does not open the pull request.** DEC-153 (`DECISIONS.md:3660-3662`): the commit pen
  is the orchestrator's, and merge, PR and deploy stay user-gated. This feature designs the
  **recording** seat only. Whether the harness should open its own PRs is a question for the
  operator, raised and not answered here.
- **The harness posts nothing and closes nothing it did not create.** DEC-138 amendment 6 forbids
  the mirror composing its own text at post time; DEC-196 limits closing to cards the harness
  created. `Closes #N` is therefore rendered for the operator, never posted.
- **`feature-schema.json` is closed** (`additionalProperties: false` at every level, DEC-191), so the
  new key is a schema edit and ships fixtures that pass **and** fixtures that fail — issue #288
  recorded an assertion with no failing fixture, and that is not repeated here.
- **`check-state.sh` is a DEC-174 carve-out.** Any task touching it is executed by hand by the
  operator, never dispatched.
- **`gh_board.py` and `load_board` are read-only here.** `gh-sync.py:139` imports and calls them, and
  that surface belongs to #493. No task changes them, their signature or their behaviour, and no
  task adds a `harness.json` key.
- **Out of scope, deliberately:** #277's already-closed board work; the `pr` field's use in the
  factory lane; anything about product repositories. Issues #283 and #287 are factory-lane findings
  and are not absorbed. Issue #289 **is** absorbed, because the fix lands inside a function this
  feature already edits and the two writers in that one file currently disagree with each other.

## Approval

status: pending
