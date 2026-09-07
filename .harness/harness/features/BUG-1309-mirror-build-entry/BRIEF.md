# BRIEF — BUG-1309 mirror build entry

## Problem

FEAT-55 was planned, approved, built, reviewed and merged with `github.sync: true` and never opened
its GitHub mirror. Nothing refused it. At the merge, `post-merge-sweep.sh` ran `gh-sync.py ship`
against the main-checkout feature directory, `cmd_ship` hit `skip("no recorded milestone — nothing
to close")` before `_record_pr` and the `done` station write, and the sweep read that SKIP as "not
proof the terminal status was recorded" and kept the worktree. The feature reached its merge with
no mirror, no terminal local station and no PR recorded, and the only remaining evidence was a
worktree the operator had to reason about by hand. The operator's workaround — a late
`gh-sync.py open` — has since RUN: measured today, `FEAT-55-issue-types-created-work`'s
`feature.json` records milestone 52, parent 1289 and twelve task sub-issues (#1391–#1402), every
one created after the work was finished (issue #1390). FEAT-55 is therefore unreported and
unterminalized rather than unmirrored — it still records no terminal station and no PR, and the
historical task sub-issues this feature exists to prevent were created once already, unseen by any
gate. The cause is known and stated: the mirror act was doctrinally attached to "mission
ship, right after the approval gate passes" (`references/github-mirror.md`, originating at
`ab4d2fdc`), which reads as the terminal Ship phase, while the orchestrator playbook's build phase
names no mirror act at all; and `check-state.sh` INV-26 exempts terminal features and
all-status-absent plans, which is exactly the shape FEAT-55 presented.

## Goal

Split the two acts by name and by enforcement. The mirror is opened at **Build entry** — the
transition immediately after signed plan approval that starts execution — and **Ship** means only
post-merge terminal finalization. Build entry leaves a durable local receipt of what happened, Build
refuses to start without one, a merge is refused while that receipt says recovery is still owed, and
an already-merged feature that lost its mirror can be recovered to a terminal receipt without
inventing historical task issues. Identical for `FEAT-*` and `BUG-*` flows.

## Requirements

- REQ-01: Build entry is the transition immediately after signed plan approval that starts
  execution and opens the GitHub mirror; it is never called Ship, and it reads the same way for
  `FEAT-*` and `BUG-*` flows.
- REQ-02: Ship is only post-merge terminal finalization — finalize merged code, record terminal
  local state, perform any recorded mirror transition, release the worktree.
- REQ-03: Build entry leaves a durable local outcome that a later reader can act on without asking
  GitHub anything.
- REQ-04: With GitHub sync enabled, that outcome distinguishes a mirror that was fully opened from
  one stopped by a temporary environmental failure.
- REQ-05: With GitHub sync disabled or unconfigured, the outcome records an approved no-mirror
  delivery mode that gates nothing.
- REQ-06: Build refuses to start when the required Build-entry outcome is absent, and may proceed
  after a recorded temporary environmental mirror failure. A local configuration or contract error,
  and a partial remote write, leave no outcome recorded and therefore block Build.
- REQ-07: A feature carrying a recovery-owed outcome cannot be merged: the merge action is refused
  until a normal mirror receipt is recorded, and re-running the mirror open is idempotent.
- REQ-08: An already-merged sync-enabled feature whose mirror was never opened can be recovered by
  an explicit operator-approved action that creates a terminal receipt only — milestone plus the
  parent and source issues — and never historical task sub-issues.
- REQ-09: A legacy recovery attempted while GitHub is unavailable leaves the feature non-terminal
  and keeps its worktree until both the recovery and Ship succeed.
- REQ-10: A sync-enabled feature that reaches a terminal state with no recorded mirror receipt is
  refused by a gate rather than silently skipped.

## Constraints

- SUPPLIES — DEC-138: GitHub is a mirror and never a gate, and the mirror act belongs at
  `plan approved -> create`. This feature does not make GitHub a gate: every refusal here reads a
  LOCAL receipt, never the remote.
- SUPPLIES — DEC-179: routing is resolved at plan time by `check-domain.sh --resolve`, which is how
  each surface below received its lane.
- SUPPLIES — DEC-146 / DEC-203: the mirror's failure posture (best-effort per card, `ship` is the
  sole writer of the done station) is unchanged by this feature.
- BINDS — DEC-174: hooks, validators and gate scripts, and their tests, are never executed by the
  harness itself. Every refusal this feature adds is main-session-direct work.
- BINDS — DEC-191: `feature.json` has a closed key set, `additionalProperties: false` at every
  closed level, and carries no `status` and no `phase`. Any new key must be DECLARED in
  `feature-schema.json` or every write of it becomes a schema error.
- BINDS — DEC-213: harness tests live under `tests/unit/**` and `tests/integration/**`; the
  directory selects the kind.
- BINDS — DEC-217: a bugfix touching runtime code carries the `unit` floor; a fix confined to tests
  and contract docs requires `integration`. The runtime surfaces here are Python and Bash under
  `.claude/skills/harness/bin/`, whose standing beds are all in `tests/integration/`.
- Out of scope, on the operator's word: requiring GitHub sync for projects that set
  `github.sync: false` or leave GitHub unconfigured; creating task-level historical mirror records
  after work completes; changing the user-gated merge policy — the merge stays the user's act, and
  this feature only refuses it while a receipt is owed.

## Success Criteria

- SC-01: With sync enabled and the mirror fully created, `gh-sync.py open` leaves a Build-entry
  outcome of `opened` in `feature.json`; with `github.sync` false or absent it leaves
  `not-applicable`; with `github.sync` enabled and `github.repo` unpinned it records NOTHING — the
  key stays ABSENT, asserted as key absence rather than a falsy or `not-applicable` value, which is
  the state that makes Build refuse (an opted-in mirror project with an unpinned repo is a local
  configuration error, not an approved no-mirror mode); and when the run stops on a temporary
  environmental no-go before any remote-mutating call it leaves `recovery-required`. Re-running
  `open` on an already-`opened` feature creates nothing new and leaves the outcome `opened`.
  verify: automated        evidence: integration
- SC-02: A run that fails after at least one remote object has been created, and a run that exits
  on a caller or contract error, leave NO Build-entry outcome recorded — the field stays absent
  rather than reading `recovery-required`.
  verify: automated        evidence: integration
- SC-03: For a feature NOT in `feature_schema.BUILD_ENTRY_ERA_EXEMPT`, Build refuses to start a task
  when no Build-entry outcome is recorded, naming the command that fixes it — and which command it
  names is chosen by the feature's own recorded station, so a feature whose work is already under
  way or finished is sent to `recover-terminal` and never to a bare `open` — and starts normally
  when the outcome reads `recovery-required`. For a feature that IS in that set, the same absent
  outcome refuses nothing: Build CONTINUES at exit 0. The refusing assertion must be demonstrated
  failing against the pre-change copy of the script before the fix is accepted.
  verify: automated        evidence: integration
- SC-04: A merge command issued for a feature NOT in `feature_schema.BUILD_ENTRY_ERA_EXEMPT` whose
  Build-entry outcome reads `recovery-required`, or is absent under enabled sync, is denied with a
  reason naming the feature and the re-run command; the same command for a feature reading
  `opened`, `not-applicable` or `recovered-terminal` is allowed, and for a feature that IS in that
  set the merge is ALLOWED at exit 0 with no permission decision emitted. Every deny is earned by
  the LOCAL receipt: when `gh` is unavailable and the head branch cannot be resolved remotely, a
  merge that no local record condemns is ALLOWED, with one line on stderr saying the gate could
  not verify.
  verify: automated        evidence: integration
- SC-05: The operator-approved recovery of an already-merged feature creates the milestone and the
  parent and source issues and ZERO task sub-issues — asserted as an exact count of the recorded
  `github.issues` map and of the fake `gh` binary's create calls, not as a substring search.
  verify: automated        evidence: integration
- SC-06: `post-merge-sweep.sh` retention keys on the RECORDED Build-entry value and never on era
  membership, over two graded features: one that RECORDS `recovery-required` — the state a recovery
  attempted while GitHub is unavailable leaves behind, which keeps that feature non-terminal — has
  its worktree KEPT after the merge, with the sweep naming the recorded receipt, and that holds even
  when the feature IS in `feature_schema.BUILD_ENTRY_ERA_EXEMPT`; while a feature in that set whose
  Build-entry key is ABSENT could never have written a receipt and is SWEPT normally, announcing
  that it predates the receipt. Both halves are graded by the cases T-07 declares —
  `T-07 era-exempt recovery-required keeps the worktree` and
  `T-07 era-exempt absent build_entry is swept`.
  verify: automated        evidence: integration
- SC-07: `check-state.sh` reports a violation for a sync-enabled feature that carries no Build-entry
  outcome even when its station is terminal AND every task status is absent — the exact FEAT-55
  shape — and reports nothing for the same fixture once the outcome is recorded. The violating
  fixture must be shown passing `check-state.sh` before the invariant lands.
  verify: automated        evidence: integration
- SC-08: `feature-schema.json` declares the Build-entry field with its closed value set, a
  `feature.json` carrying a legal value validates, and one carrying an illegal value or a
  neighbouring misspelling is refused with the schema's undeclared-key or enum message.
  verify: automated        evidence: integration
- SC-09: At `review_sha`, `git show <review_sha>:.claude/skills/harness/references/github-mirror.md`
  and `git show <review_sha>:.claude/skills/harness/SKILL.md` both name the mirror act as Build
  entry, tied to the signed approval, and neither describes it as happening at ship; the
  orchestrator playbook's build phase names the act in its own sequence.
  verify: inspection
- SC-10: The operator, on a real sync-enabled feature recorded `recovery-required`, attempts their
  normal merge command and sees it refused with a message they can act on without reading the
  source; after re-running `gh-sync.py open` the same command is allowed.
  verify: uat

## Verification gaps

- `component`, `ui` and `typecheck` carry `cmd: null` in `.harness/harness.json`. This feature
  touches no browser or component surface, so no criterion rests on them. The one TypeScript
  surface it touches, `.omp/extensions/harness-hooks.ts`, is executed by
  `tests/unit/test-omp-hooks.py`, which shells out to `bun test tests/unit/omp-hooks.test.ts` and IS
  discovered by the `unit` runner's `tests/unit/test-*.py` glob.
- Every automated criterion here drives `gh` through the fake-binary seam (`GH_SYNC_GH`, `GH_BIN`),
  never a live repository. What is therefore NOT proven automatically: that a real `gh pr merge`
  against GitHub is refused in the operator's own session. SC-10 carries that, by hand.
- The Build-entry outcome for the legacy already-merged corpus is not backfilled. The new
  `check-state.sh` invariant binds features created from this change onward, through a frozen
  era-exempt set; the existing corpus stays exempt and is recovered case by case on the operator's
  say-so. Concretely, 17 sync-enabled feature directories record no milestone at all (FEAT-01,
  FEAT-02, FEAT-03, FEAT-04, FEAT-05, FEAT-10, FEAT-15, FEAT-17, FEAT-19, FEAT-28, FEAT-36,
  BUG-1030, BUG-1055, BUG-1071, BUG-1080, BUG-1128, BUG-1157): they are KNOWINGLY UNRECOVERED, the
  guarantee here is forward-only, and each is recovered only by an explicit operator-approved
  `recover-terminal`, never automatically. This is a deliberate scope boundary, not an oversight.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-09-06
