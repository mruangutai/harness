# BRIEF — FEAT-40 The harness writes Done

## Problem

Three mechanisms decide whether a board card reads true and none of them owns the answer, so the
board misreports finished work and nobody is told. Measured at `cc84b29`: every sub-issue close on
record for FEAT-33, FEAT-34 and FEAT-35 reads `by mruangutai reason=null`, which no document
anywhere instructs — `close-task` always passes `--reason completed` (`gh-sync.py:855`), so a null
reason proves the harness did not do it. FEAT-34's 13 sub-issues are closed and sitting at `Review`
because the hand close landed before validate entry wrote `Review` over the top; whichever ran last
won and nothing says which should. The post-merge sweep that would have run `gh-sync.py ship` has
never fired on this clone, because `core.hooksPath` resolves to
`/Users/molchairuangutai/GitHub/harness/.git/hooks`, which holds only samples. And nothing closes a
task sub-issue automatically at all: `gh-sync.py closes` emits `Closes #N` for `source_issues` only.
The cost is that the operator reads a board that is wrong and cannot tell which of the three
mechanisms lied.

## Goal

The harness itself lands every card of a shipped feature at `Done`, and GitHub's own workflow closes
the issue behind it. A ticket is open while its card is not at `Done` — the station is the authority,
not the issue's open/closed field. Who created a ticket stops mattering; whether it still has an open
child starts mattering. A `gh issue close` made through the Bash tool is refused, and the refusal
tells the operator what to do instead of typing it. That is a gate on agents, not a seal on the
repository: a human at a terminal, or in the GitHub web UI, can still close a tracked issue. The
compensating control for that leak is `board_lifecycle.py audit`'s STATION finding class, which
already detects a closed card that is not at `Done`. What it lacked was a runner: `ship` now runs
it, once per feature. And no harness command in the mirror closes an issue directly any more except
`abandon`, which reports what it would close and asks first.

## Requirements

- REQ-01: A tracked ticket's open state is decided by its card's station — it is open while that card
  is not at the `Done` station.
- REQ-02: `gh-sync.py ship` lands every card the feature records — task sub-issues, `source_issues`
  and the parent — at the `Done` station, and issues no close of its own.
- REQ-03: `ship` does not land a `source_issues` card or a parent card whose ticket still has an
  open child, and prints one line naming the child that held it open. A task sub-issue is exempt:
  the harness creates each one flat and attaches it to the parent, never to another task issue, so
  the child set is empty by construction and reading it would cost one network call per task to
  prove nothing (D-10).
- REQ-04: Which agent or person created a ticket no longer affects whether the harness closes it.
- REQ-05: `abandon` reports which tickets it would close and asks the operator, instead of deciding
  from a recorded origin.
- REQ-06: A `gh issue close` **made through the Bash tool** is refused, and the refusal routes the
  operator by intent: do nothing if the work is finished, run `gh-sync.py abandon` if it is being
  dropped, use the web UI if the issue is not tracked. This is the whole of what the gate can
  deliver — a `PreToolUse:Bash` hook sees only `tool_input.command`, so a close typed in a terminal
  or made in the GitHub web UI is out of its reach and REQ-06 does not claim otherwise. What the
  gate cannot reach is reported instead: once per feature, the harness reports every tracked issue
  that is closed while its card is not at `Done`.
- REQ-07: `gh-sync.py closes` no longer exists, and nothing composes closing keywords for a pull
  request body.
- REQ-08: The decision record carries exactly one live rule for closing and station authority; no
  surviving entry contradicts it.
- REQ-09: A clone whose merge hook is not installed is reported by the harness's own state check,
  on every run, on every clone.
- REQ-10: A task sub-issue's card holds `Review` from validate entry until the validation panel
  returns clean.
- REQ-11: Every document describing who closes a ticket, and when, matches the code shipped beside
  it.
- REQ-12: Inside the GitHub mirror, `abandon` is the only command that closes an issue directly,
  and it reports what it would close and asks first. `gh-sync.py close-task` no longer exists.

## Success Criteria

- SC-01: `ship` writes the `done` station for every recorded card — each task sub-issue, each
  `source_issues` entry, and the parent — and executes no `gh issue close` and no
  `state=closed` PATCH on any of them. Each card gets its own assertion, not a count.
  verify: automated      evidence: integration
- SC-02: `ship` given a parent with one child whose card is not at `Done` leaves that parent's card
  where it is and prints one line beginning `gh-sync: HELD — ` and naming that child's issue number.
  A child that is not on the board at all counts as open and produces the same line, distinguished
  only by its parenthetical.
  verify: automated      evidence: integration
- SC-03: `ship` writes the children's cards before it evaluates a parent, so a parent whose only open
  children are cards this same run lands at `Done` reaches `Done` in that run. Demonstrated failing
  first against the pre-change order.
  verify: automated      evidence: integration
- SC-04: `gh-sync.py closes` exits non-zero with an unknown-subcommand message, and no function
  renders a `Closes #` line anywhere in `.claude/skills/harness/bin/`.
  verify: automated      evidence: integration
- SC-05: `parent_origin` appears in no file under `.claude/skills/harness/bin/`, in no
  `.harness/harness/features/*/feature.json`, and in no live rule of
  `.claude/skills/harness/references/github-mirror.md`; `feature-schema.json` rejects a `github`
  block that carries it.
  verify: automated      evidence: integration
- SC-06: `abandon` prints the issue numbers it would close, naming the parent as the parent, and
  exits without closing anything, when the operator has not confirmed. With the operator's
  confirmation it closes exactly the set it printed, in the order it printed. `--yes` before the
  feature directory and `--yes` after it behave identically, and neither fails on the argument.
  verify: automated      evidence: integration
- SC-07: With the gate registered, a Bash call containing `gh issue close` is denied, and the denial
  text carries all three routes: doing nothing when the work is finished, the runnable
  `gh-sync.py abandon` command when it is being dropped, and the web UI when the issue is untracked.
  The `gh api` `state=closed` denial returns the identical text. A Bash call running
  `gh-sync.py abandon` is not denied. Every assertion fails against the tree without the gate.
  verify: automated      evidence: integration
- SC-08: `check-state.sh` reports a violation naming `core.hooksPath` when it does not resolve to
  `.claude/skills/harness/hooks`, and a second, distinct violation when `post-merge` in that
  directory is missing or not executable. It is clean when both hold. All three states are exercised
  by fixtures.
  verify: automated      evidence: integration
- SC-09: On this clone, `git config --get core.hooksPath` prints `.claude/skills/harness/hooks`, and
  a real merge in a scratch clone configured the same way produces the post-merge sweep's own stdout
  line. The recorded probe names the scratch path and quotes the line.
  verify: inspection
- SC-10: Moving a card to the `Done` station closes its issue on this board, re-measured this
  feature: the recorded probe names a throwaway issue number, the time the card was moved, and the
  time GitHub closed it. `board_lifecycle.py audit` additionally reports no WORKFLOW finding against
  `Auto-close issue`.
  verify: inspection
- SC-11: Running `gh-sync.py ship` on FEAT-34's feature directory, with no `gh` command typed by
  hand, lands #728 at `Done` and leaves it CLOSED on GitHub. #728 carries 13 children, all of whose
  cards read `Review` before the run, so this exercises SC-03's ordering rather than the trivial
  path.
  verify: inspection
- SC-12: After `gh-sync.py status <dir> Review`, the parent's card and every recorded sub-issue's
  card read the `review` station, and no code path other than `ship` writes the `done` station.
  The second clause is asserted over the whole of `gh-sync.py`, not over one function.
  verify: automated      evidence: integration
- SC-13: `.claude/skills/harness/references/github-mirror.md`, `.claude/commands/harness.md` and
  `.claude/skills/harness-init/SKILL.md` carry no surviving sentence stating that GitHub writes the
  `Done` column, that `ship` closes the milestone as its purpose, that `closes` is a step, or that a
  closed sub-issue cannot sit at `Review`. Graded by reading `git show <review_sha>:<path>` for each
  of the three, not the working tree.
  verify: inspection
- SC-14: `DECISIONS-INDEX.md` regenerates byte-identical from `DECISIONS.md`, every index row is
  within the 30-word cap, and DEC-186, DEC-192 and DEC-196 each carry a strike record pointing at the
  new entry, with DEC-138 amendment 7's parent table struck in the same act.
  verify: automated      evidence: integration
- SC-15: A `ship` run in which a card's `Done` write failed prints a line beginning
  `gh-sync: FAILED ` naming that card, and `post-merge-sweep.sh` leaves the feature's worktree
  standing. A run in which cards were only held prints no `FAILED` line and the worktree is removed.
  No output of any `ship` run contains the substring `gh-sync: SKIP` unless `ship` genuinely skipped.
  verify: automated      evidence: integration
- SC-16: `gh-sync.py close-task` exits non-zero with the unknown-subcommand message, the string
  `close-task` survives nowhere in `gh-sync.py`, and `abandon` is the only function in that file
  that issues a `gh issue close` or a `state=closed` PATCH against an issue. Every behaviour the
  suite asserted through `close-task` — the parent-station derivation, the loud pair, the
  no-board precondition — is still asserted, through `start-task`, and the assertion count for
  those does not fall.
  verify: automated      evidence: integration
- SC-17: `ship` runs `board_lifecycle.py`'s audit exactly once per run, after its own station
  writes, and prints each finding on its own line prefixed `gh-sync: audit — `. A card this same
  run moved to `Done` produces no `STATION` finding, demonstrated failing first against an
  implementation that audits before it writes. An audit that cannot run leaves `ship`'s exit
  status 0 and prints one line saying so, and no audit line carries `gh-sync: SKIP` or
  `gh-sync: FAILED`.
  verify: automated      evidence: integration

## Verification gaps

- No automated test reaches a live GitHub board: `test-gh-sync.py` stubs the `gh` binary, so every
  SC above marked `automated` proves the harness ISSUES the right calls, never that GitHub honours
  them. SC-09, SC-10 and SC-11 carry the live half, and all three are `inspection` over a recorded
  probe. If the probe in SC-10 comes back negative, the entire change has no close path at all —
  which is why it is planned before the deletion of `cmd_closes`, not after.
- `component`, `ui` and `eval` carry `cmd: null` in `.harness/harness.json`. This feature touches
  none of those surfaces, so no criterion rests on them.
- `test-gh-sync.py` is detected by both the `unit` and `integration` globs and is run from the
  `integration` bucket by `run-unit-tests.sh`. Every `verify:` in the plan runs `--kind all` so the
  bucket split cannot silently skip an assertion.

## The failure mode this brief settles, and the premise it had wrong

`ship` writes many cards in one run. Today every station write in `gh-sync.py` is best-effort per
card: a `BoardError` prints one stderr line, the run continues, and the exit status is still 0
(DEC-146; `references/github-mirror.md:59-70`). A half-written terminal batch therefore means some
tickets close and some silently do not.

**An earlier draft of this brief said that had "no gate downstream". Measured, that was wrong.**
`post-merge-sweep.sh:180-195` already declines to remove the worktree when `ship`'s combined output
contains the literal `gh-sync: SKIP`, on its own stated reason that an exit code is never positive
evidence the write ran and that the standing checkout is "the only remaining evidence". A downstream
reader exists; it was simply not reading anything this feature emits.

The architecture review settled it and the plan now carries it (D-05, D-11): keep the per-card
posture and exit 0 — no transaction spans N field writes and git ignores a `post-merge` hook's exit
status — and extend that same string gate. `ship` prints two distinct literals, `gh-sync: HELD` for
a card deliberately not moved and `gh-sync: FAILED` for a write that failed, and the sweep declines
the worktree removal on `FAILED`. It does not decline on `HELD`: a held parent is a healthy outcome
and worktrees would otherwise accumulate in normal operation. No new line may contain
`gh-sync: SKIP`, which would silently change worktree behaviour on a healthy run. The cost is that a
partially failed ship leaves a worktree for the operator to clear — visible and reversible, against
a card that silently misses `Done` with its only signal one line inside the output of a `git merge`.

## What this feature does NOT do, and why

- It does not remove the `absorbs:` machinery from `gh-sync.py`, `plan.yaml` or the suite. The rule
  is already struck in the docs (#840, merged as `cc84b29`); the code removal is its own change with
  its own tests. Operator-ruled.
- It does not add a `check-state.sh` invariant for a card that is CLOSED but not at `Done`.
  `board_lifecycle.py` already detects exactly that, as its STATION finding class
  (`board_lifecycle.py:_audit_findings`, class 2 of six). What was missing was not a detector but a
  runner — nothing scheduled `audit`. A second detector in `check-state.sh` would be two rules for
  one fact, and wiring `audit` into the pre-commit gate would cost four network calls on every run.
  **This is the same defect as the gate's limited reach, seen from the other side**: the Bash gate
  cannot see a close typed in a terminal or made in the web UI, and the one thing that catches such
  a close after the fact is that detector. REQ-06 stays narrowed to what the gate can deliver, and
  the compensating control is now settled rather than open — the operator ruled it on 2026-08-25.
  `ship` runs the audit, once per feature, and nowhere else: `ship` already reads GitHub for the
  open-child check, so the audit's four calls are a small increment on a read already happening.
  Running it at each station write was rejected, because the leak happens when the harness is *not*
  writing a station — a human closing an issue in the web UI triggers nothing — so a station-change
  trigger catches it no sooner in practice, at several times the cost. **The cost this accepts,
  stated:** a card closed outside the harness can sit wrong for the whole build and is only caught
  at ship. That is tolerable because ship is where the open-child decision is made — the moment the
  wrongness would otherwise cause harm.
- It does not repair FEAT-34's stranded cards as a goal. SC-11's acceptance run does move them, as a
  consequence of shipping FEAT-34's own recorded set — that is the same act, not extra scope.
- It does not close the same leak outside the mirror. `wayfind.py resolve` runs a `gh issue close`
  on a wayfinding ticket (`wayfind.py:318`), and the Bash gate is blind to that subprocess exactly
  as it was to `close-task`. Wayfinding tickets are not feature tickets and are out of this
  feature's scope; raised as a separate question rather than silently absorbed.

## Constraints

**These SUPPLY the mechanism:**

- DEC-138 and its amendments — the mirror contract, the owner table, and the write-only posture.
  Amendment 7 already carries the replacement rule in prose ("a ticket is open while its card is not
  at the `Done` station, and a parent closes when it has no open children"); its ship/abandon parent
  table still states the origin rule and is struck by this feature.
- DEC-146 — station writes are best-effort per card. This is the posture the terminal `Done` write
  inherits unless the architecture review changes it.
- DEC-186 — the read-back bound, currently five purposes. Reading a card's children is a sixth, and
  the replacement decision carries it.
- DEC-188 — a decision the tree flatly contradicts is STRUCK, never marked stale.
- DEC-192 — one `status` field whose six values are the board's column names. Its substance must
  survive inside the replacement entry; striking it without restating it would delete the status
  contract.
- DEC-196 — the harness moves any card it is pointed at and closes only cards it created. This is the
  rule being reversed.

**These BLOCK:**

- DEC-174 — the harness may PLAN its own enforcement-layer work but must not EXECUTE it through the
  enforcement path being changed (`DECISIONS.md:4808`). `check-state.sh`, the new Bash gate and
  `.claude/settings.json` are enforcement layer.
- DEC-164 — the grilling artifact is step zero and its facts are a floor, not a ceiling.
- The operator's route ruling: the main session executes every task directly.

## Corrections to the record this feature makes

- **#728 has 13 children, not none.** Measured 2026-08-25:
  `gh api repos/mruangutai/harness/issues/728/sub_issues` returns #818 through #830, all closed, and
  FEAT-34's `feature.json` records #728 as its `parent` with `parent_origin: null`. The acceptance
  test therefore exercises the open-child path, and SC-03's ordering requirement is what makes it
  pass rather than skip.
- **DEC-138 amendment 7's D-23 reasoning is false.** It says a closed sub-issue cannot sit at
  `Review` because the native `Item closed` workflow moves it. FEAT-34's 13 sub-issues are closed and
  at `Review` right now.
- **A `PreToolUse:Bash` gate cannot see `gh-sync.py`'s own `gh` calls.** The hook is handed
  `tool_input.command` and nothing else (`branch-create-gate.sh:47`), and `gh-sync.py` reaches `gh`
  through `subprocess`, which never traverses the tool. An environment marker set inside `gh-sync.py`
  therefore cannot reach the gate at all. The gate can and should refuse every `gh issue close`
  unconditionally — abandon keeps working because its close is a subprocess, not a Bash call. This
  changes the mechanism the source ticket names while delivering the outcome it names. Raised as an
  open question so the operator can overrule it.

## Approval

status: pending
