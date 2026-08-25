# Grilling — the harness writes Done, and a parent closes on no open children — 2026-08-25

## Destination

One shipped change: a board card never misreports finished work, the harness moves cards to `Done`
itself, and a parent ticket closes when it has no open children. Nobody closes a tracked issue by
hand again.

## Settled

- **What "open" means** → a ticket is open while its card is **not at the `Done` station**. Station is
  the authority, not the issue's own open/closed field.
- **Who writes `Done`** → the harness, by writing the `Done` station. GitHub's own workflow then
  closes the issue. This reverses today's direction, where a close moves the card.
- **When** → at `gh-sync.py ship`.
- **Which cards ship moves** → every recorded card: the task sub-issues, the `source_issues`, and the
  parent. **Skip any card that still has an open child**, and print one line naming the child that
  held it open.
- **The parent rule** → a parent closes when it has no open children. **Origin stops mattering
  entirely** — who created the ticket is no longer part of the decision.
- **DEC-196 is struck** under DEC-188, and **DEC-138 amendment 7's parent table is struck in the same
  act**. That table restates DEC-196 inside DEC-138; striking DEC-196 alone leaves the tree
  contradicting itself.
- **Where the replacement rule lives** → **one new decision**, absorbing **DEC-192 and DEC-186 as
  well**, all three rewritten together. The operator's words: "less concise, less wordy, but clear."
  Read as: plain readable prose, clarity over compression — the dense style of the current entries is
  the thing being replaced. Confirm this reading before writing.
- **The `Closes` machinery is removed** — `cmd_closes` and its `source_issues` rendering. Ship's Done
  writes replace it.
- **`parent_origin` is deleted** — the field, `open`'s recording of it, and every branch on it.
  **Abandon reports what it would close and asks the operator**, rather than deciding from origin.
- **Sub-issues hold `Review`** from validate entry until the panel returns clean. That is a
  requirement, not an accident of ordering. D-23's claim that a closed sub-issue *cannot* sit at
  Review is false and must not be relied on.
- **The guardrail** → a `PreToolUse:Bash` gate refuses every `gh issue close` **except abandon's**,
  identified by an environment marker `gh-sync.py` sets. It names the sanctioned command in its
  refusal.
- **`core.hooksPath` on the harness's own clone is set as part of this fix**, not before and not
  after.
- **Execution route** → `/harness-plan` produces the brief and signed plan; the **main session
  executes every task directly**. DEC-174 permits planning enforcement work through the harness and
  forbids executing it that way.
- **#728 is the end-to-end acceptance test.** It stays open until this change closes it.

## Not yet specified

- How the gate recognises abandon's own call without creating a marker anyone can set by hand. An
  environment variable is the shape; whether that is sufficient is not settled.
- Whether `check-state.sh` gains an invariant for a tracked card that is closed but not at `Done` —
  the leak the gate cannot see, such as a close made in the GitHub web interface.
- What `ship` does when a card's board write fails partway through a batch. Today's station writes
  are best-effort per card (DEC-146); whether a terminal Done write may be best-effort is untested.

## Out of scope

- Removing the `absorbs:` machinery from `gh-sync.py`, `plan.yaml` and the suite. The rule is struck
  in the docs (#840, merged as `cc84b29`); the code removal is its own change with tests.
- Repairing FEAT-34's 14 stranded cards. The operator ruled: fix the cause first, repair after.
- Issue #806, a source issue of FEAT-34, still open at `Backlog`. It closes through this change, not
  before it.

## Facts I verified (so pm does not re-derive them)

Measured at `cc84b29` unless stated.

- **Nothing instructs the main session to close a task sub-issue.** `.claude/commands/harness.md:95`
  says run `gh-sync.py ship` "(closes the milestone)" and nothing more.
  `references/github-mirror.md:30` says sub-issues close from the PR's `Closes` lines. The hand
  closes were an undocumented habit.
- **Every sub-issue close on record was by hand.** FEAT-33 (#756, #777), FEAT-34 (#818, #830) and
  FEAT-35 (#798, #802) all read `by mruangutai reason=null`. `close-task` always passes
  `--reason completed` (`gh-sync.py:855`), so a null reason proves it was not `close-task`.
- **`gh-sync.py closes` is a documented main-session step**, not dead code
  (`references/github-mirror.md:36`). It works: `Closes #840` in PR #841's body closed #840 and the
  board moved it to `Done`. It emits only `source_issues` — never the task sub-issues.
- **PR #837 carried no `Closes` lines at all.** The step was skipped.
- **The board is bidirectional.** A close moves the card to `Done`; probe #807 recorded that moving a
  card to `Done` closes the issue in under 10 seconds. That second direction is **not re-verified in
  this session** — verify it before depending on it.
- **The post-merge sweep does not fire on the harness's own clone.**
  `core.hooksPath = /Users/molchairuangutai/GitHub/harness/.git/hooks`, and `.git/hooks` holds only
  samples. `post-merge-sweep.sh:174` is what runs `gh-sync.py ship`.
- **Only FEAT-34's cards are stranded.** #616, #642, #701, #756 and #798 are all `CLOSED` at `Done`.
  #818 is `CLOSED` at `Review`, because its hand close landed *before* validate entry wrote `Review`
  over the top. Whichever ran last won; nothing says which should.
- **`_apply_parent_rule` already carries a terminal exemption for this exact failure**
  (`gh-sync.py:218-221`), but only for the parent. `cmd_status`'s `Review` branch
  (`gh-sync.py:955-958`) has no state check at all.
- **`parent_origin` across 26 features with a parent:** 15 `created`, 7 `adopted`, 2 present-and-null
  (FEAT-34, FEAT-35), 2 key-absent (FEAT-08, FEAT-09). The two nulls are the **two most recent**
  features, both from hand-recorded parents — the same leak as the hand closes.
- **21 shipped features carry a parent; only #728 is still open.** Nine non-created parents were
  closed by hand.
- **DEC-186 is not mainly a station rule.** It bounds read-back to five purposes, of which stations is
  one; it also carries the ban on a read-back value entering `BRIEF.md`, `plan.yaml` or an approval
  block.
- **A `PreToolUse:Bash` gate can bind the main session.** `branch-create-gate.sh` refused two branch
  names in this session.
- **DEC-174 does not conflict with building this gate** (`DECISIONS.md:4808`): enforcement-layer
  changes are made directly by the main session; only *dispatching* them through the harness is
  forbidden.

## The one ordering constraint the plan must carry

`ship` becomes the only thing that closes tickets, and the post-merge sweep is the only thing that
runs `ship` — and that sweep does not currently fire. **The task that deletes `cmd_closes` must depend
on the task that proves the sweep fires.** Reversed, a merge would close nothing, silently.
