# BRIEF — FEAT-30 Worktree per feature

Promoted from #572 on operator instruction, 2026-08-20. Direction chosen by the operator from the
three the issue offered: **build DEC-95's machinery.** The alternatives — restoring DEC-88's
one-feature constraint, or gating `HEAD` alone — were considered and declined; restoring DEC-88
would forbid what the operator explicitly asked for, which is two features building at once.

## Problem

Concurrent feature runs share one checkout, and nothing stops them colliding. DEC-88 stated the
operating constraint plainly — one feature in flight at a time. DEC-95 superseded it with one
feature per worktree. **DEC-95's machinery was never built**, so the constraint that made
concurrency safe was removed and its replacement does not exist.

Measured at `b4659cd` and re-confirmed 2026-08-20:

    grep -c worktree .claude/agents/harness-orchestrator.md   -> 0
    grep -c worktree .claude/commands/harness.md              -> 0
    git worktree list                                        -> one tree

What protects concurrent runs today is convention. Against `agent_type: harness-orchestrator`,
`git checkout main` and `git add -A` both **exit 0**. DEC-153 tells the orchestrator to stage by
explicit pathspec; that is a rule an agent follows, not a gate that stops it.

**The cost is already paid, twice.** On 2026-08-19 the main session created a branch mid-run,
moving `HEAD` out from under a live orchestrator, whose next commit landed on the wrong branch —
recovery took a stash, a checkout, a cherry-pick and a stash pop. Note the agent behaved
CORRECTLY: it committed to the current branch. That is only safe when `HEAD` is not shared mutable
state. And on 2026-08-20, PR #599 rescued 22 files of planning work for two paused features that
existed **only** inside a third feature's working tree; FEAT-28's plan had zero commits anywhere.
One `git clean` would have destroyed it.

## Goal

A feature run gets its own working tree, so two features can build at once without either being
able to touch the other's files, branch, or `HEAD`. Isolation replaces discipline: the 2026-08-19
incident becomes impossible rather than recoverable, and no feature's artifacts can become
hostages in another's checkout.

## Requirements

- REQ-01: The dispatch path creates a worktree per feature run under `.claude/worktrees/<id>/`,
  cut from `main`, and the orchestrator works inside it.
- REQ-02: A worktree is cut from `main`, never from another feature's branch.
- REQ-03: The worktree is removed when its feature reaches a terminal state, and its artifacts
  reach `main` before removal.
- REQ-04: A governed agent that switches branch, or otherwise moves `HEAD`, during a live run is
  refused rather than trusted not to.
- REQ-05: The orchestrator's own instructions state where it works. It reaches an agent by
  preload, not by being told to go read a file.

## Success Criteria

- SC-01: With two feature runs live, each orchestrator's commits land only on its own branch, and
  neither working tree contains the other's files. Proven by running two features concurrently and
  inspecting both trees and both branch histories.
  verify: inspection
- SC-02: A worktree created for a feature run is cut from `main`. Asserted against the merge-base,
  not against the branch name.
  verify: automated      evidence: integration
- SC-03: An attempt by a governed agent to move `HEAD` during a live run is REFUSED and says why.
  The test drives the refusal and proves it can pass when it should — a guard that never fires is
  indistinguishable from a guard that is broken.
  verify: automated      evidence: integration
- SC-04: A feature's artifacts are on `main` before its worktree is removed. The check names the
  paths it verified rather than reporting a count.
  verify: automated      evidence: integration
- SC-05: `check-domain.sh` grants the same paths inside a worktree as outside it, for every one of
  the 16 agents. DEC-143 already strips the worktree prefix before matching; this asserts it,
  because nothing currently does.
  verify: automated      evidence: integration
- SC-06: The orchestrator's and `harness.md`'s instructions name the worktree it works in.
  `grep -c worktree` on both returns non-zero, and the text is a rule an agent can follow, not a
  mention.
  verify: inspection
- SC-07: Removing a worktree cannot delete uncommitted work silently. Either the removal refuses
  on a dirty tree, or it reports exactly what it would discard and refuses without confirmation.
  verify: automated      evidence: integration
- SC-08: No test that passed before this feature fails after it, and the full unit and integration
  suites pass.
  verify: automated      evidence: integration

## Verification gaps

- `functional`, `component`, `ui`, `eval` and `typecheck` all have `cmd: null` — no runner. No SC
  above rests on any of them. Every automated criterion is pinned to `integration`, which runs.

## Constraints

- **DEC-193 binds the location.** Exactly two places hold code under harness authority:
  `.claude/worktrees/<id>/` and `workspace_root/<product>`. Any other checkout cannot be created,
  written into, or host a governed session. A worktree outside `.claude/worktrees/` is refused,
  and this feature does not relax that.
- **DEC-174's carve-out applies.** `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`,
  `check-state.sh` and `check-plan-routes.py` are the enforcement layer. A squad may write a
  library a gate calls; **the cutover that makes a gate use it is main-session-direct.** REQ-04's
  refusal lands in that layer, so plan its cutover accordingly.
- **DEC-95's honest residue is inherited, not solved.** Committed Expertise files diverge across
  worktrees and will conflict, and the right merge is usually the union, which no tool chooses for
  you. This feature does not fix that. Say so rather than discovering it on the second concurrent
  run.
- **Out of scope, deliberately.** #280 (interrupting a lead does not stop its children) and the
  shared GitHub API budget are the same single-writer root failing from other directions. Neither
  is solved by isolation. Operator ruling, 2026-08-20: worktrees only.

## Approval

status: pending
