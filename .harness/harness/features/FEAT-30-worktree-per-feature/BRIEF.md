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

- REQ-01: The dispatch path creates a worktree per feature run at
  **`<harness root>/.claude/<repo>/worktrees/<id>/`** — one slot per repository, under THIS
  checkout, whichever repository the work belongs to. Harness's own features use the `harness`
  slot. A repo the factory serves uses its own. Two features for harness and two for another repo
  run at the same time: four worktrees, four branches, one root, one place to look.
- REQ-02: A worktree is cut from its own repository's default branch, never from another feature's
  branch. For harness that is `main`; for a served repo it is the `default_branch` its `fleet.yaml`
  entry declares, since that value exists precisely because it is read before the checkout exists.
- REQ-07: A served repo's PRIMARY CLONE stays at `fleet.yaml`'s `workspace_root/<repo>` and is not
  moved. `git worktree add` requires an existing clone, so worktrees are additional to a checkout
  and never a replacement for one. The clone is what `.claude/<repo>/worktrees/<id>/` are worktrees
  OF; nothing works in the clone directly.
- REQ-08: Legality is computed against the HARNESS root's `.claude/<repo>/worktrees/` rather than
  against the owning repository's root, and a location outside it is refused. This is a change in
  what legality MEANS, not a widened glob.
- REQ-03: The worktree is removed when its feature reaches a terminal state, and its artifacts
  reach `main` before removal.
- REQ-04: A governed agent that switches branch, or otherwise moves `HEAD`, during a live run is
  refused rather than trusted not to.
- REQ-05: The orchestrator's own instructions state where it works. It reaches an agent by
  preload, not by being told to go read a file.
- REQ-06: Two features closing out at the same time cannot silently lose Expertise entries.
  Whatever the merge policy is, a lost entry is DETECTED rather than trusted not to happen.

## Success Criteria

- SC-01: With FOUR feature runs live — two on harness, two on a repo the factory serves — each
  orchestrator's commits land only on its own branch, and no working tree contains another's files.
  This is the operator's stated goal in full: two features at once for harness AND for other repos
  simultaneously. Proven by running them concurrently and inspecting every tree and branch history.
  verify: inspection
- SC-02: A worktree created for a feature run is cut from its own repository's default branch.
  Asserted against the merge-base, not against the branch name.
  verify: automated      evidence: integration
- SC-02b: A worktree at `.claude/<repo>/worktrees/<id>/` whose owner is a clone under
  `workspace_root` is accepted, and one outside that layout is REFUSED with a message naming where
  worktrees belong. Both directions are asserted: today's code refuses the accepted case, so the
  positive half must be shown to fail before the change and pass after.
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
- SC-08: Two simulated concurrent close-outs writing the same Expertise file lose NO entry, or the
  loss is reported as an error. Proven by driving both writes and asserting the union survives —
  and by showing the assertion FAILS against the current last-writer-wins behaviour, because a
  test that passes before the fix proves nothing.
  verify: automated      evidence: integration
- SC-09: No test that passed before this feature fails after it, and the full unit and integration
  suites pass.
  verify: automated      evidence: integration

## Verification gaps

- `functional`, `component`, `ui`, `eval` and `typecheck` all have `cmd: null` — no runner. No SC
  above rests on any of them. Every automated criterion is pinned to `integration`, which runs.

## Constraints

**Nothing here blocks this feature.** An earlier draft of this brief listed the two items below as
constraints, which read as obstruction. They are not: both are already-built mechanisms this
feature uses, and the operator's challenge to that framing is why they now read as what they are.

- **DEC-193 MUST BE AMENDED, and an earlier draft of this brief was wrong about that.** That draft
  claimed multi-repo needed no enforcement change. It is true only if a served repo's worktrees sit
  under that repo's own root, which is not the shape the operator chose and not the shape that
  gives one place to look.

  `harness_boundary.py:33` defines `WORKTREES_SEGMENT = ".claude/worktrees"` as a relative path, and
  `worktree_owner()` computes `legal_home = owner_root + WORKTREES_SEGMENT` where `owner_root` comes
  from the worktree's own `.git` pointer. **Measured both directions, 2026-08-20:** a throwaway
  second repository with a worktree under its own `.claude/worktrees/FEAT-01` returned
  `legitimate=True`; a sibling outside it returned `legitimate=False`.

  That mechanism REFUSES the chosen shape. A kaya-ai worktree at
  `harness/.claude/kaya-ai/worktrees/FEAT-01` has its owner at `workspace_root/kaya-ai`, so
  `legal_home` resolves elsewhere and the write is refused. REQ-08 is therefore a change in what
  legality means, and it lands in the enforcement layer — main-session-direct under DEC-174.
- **Nested product state does NOT collide with harness's own discovery**, which was the main risk
  and is checked rather than assumed. `check-state.sh:38` sets `H = <root>/.harness` and discovery
  globs `H/*/features/*`. A worktree under `.claude/` carries its own repository's `.harness/`, which
  sits outside that glob. Harness will not read a served repo's features as its own.
- **DEC-143 already strips the worktree prefix** before matching domain globs, so an agent inside
  `.claude/worktrees/<id>/` writes exactly what its domain grants. SC-05 asserts this, because
  nothing currently does — the behaviour exists and is unpinned.
- **DEC-174's carve-out routes one step, it does not stop it.** REQ-04's refusal lands in the
  enforcement layer, so the cutover that makes a gate use it is main-session-direct. That belongs
  in the plan's lane column, not here.

**Out of scope, deliberately.** #280 (interrupting a lead does not stop its children) and the
shared GitHub API budget are the same single-writer root failing from other directions. Neither is
solved by isolation. Operator ruling, 2026-08-20: worktrees only.

**REQ-06 was added after the constraints were challenged.** DEC-95's honest residue — Expertise
files diverging across worktrees — had been recorded here as a disclosure standing in for a
decision, in the words "this feature does not fix that". It is now in scope. The reason: this
feature is what makes the residue REACHABLE. FEAT-29's close-out wrote 34 entries across 14
Expertise files; two of those running concurrently means competing edits to files injected into
every agent spawn, where the right answer is usually the union and no tool chooses it. Shipping
isolation without it means the first two concurrent features can delete each other's learning
with nothing detecting the loss.

## Approval

status: pending
