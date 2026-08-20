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

The location rule, settled by the operator 2026-08-20 and stated as three facts so nobody
re-derives it:

1. **`workspace_root` is for every repository EXCEPT harness.** `fleet.yaml` declares them and
   `workspace_root/<repo>` holds each one's checkout, outside this repository.
2. **`.claude/worktrees/` is for harness ONLY.** `fleet.yaml` excludes `mruangutai/harness` on
   purpose (DEC-174 am.1) so that this stays true, and the absence is what enforces it.
3. **The repository is NAMED in the path** — `.claude/worktrees/harness/<id>/` — so a reader can
   see which repository a working tree belongs to without inferring it.

**`workspace_root` and `<repo root>` are NOT the same thing, and conflating them loses the
isolation this feature exists to build.** `workspace_root` is the CONTAINER that holds served
repositories; a `<repo root>` is ONE repository's checkout. Measured 2026-08-20:

    workspace_root              /Users/molchairuangutai/GitHub/harness-factories
    <repo root> for kaya-ai     /Users/molchairuangutai/GitHub/harness-factories/kaya-ai
    <repo root> for harness     /Users/molchairuangutai/GitHub/harness      (NOT under workspace_root)

So the worktrees land at:

    /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/<id>/
    /Users/molchairuangutai/GitHub/harness-factories/kaya-ai/.claude/worktrees/kaya-ai/<id>/

**Every path in this brief is relative to a `<repo root>`, never to `workspace_root`.**
`worktree_owner()` computes legality as `commonpath` against `<owner root>/.claude/worktrees`, where
the owner comes from the worktree's own `.git` pointer file. Build it against `workspace_root`
instead and every served repository's worktrees share one directory — the per-repository isolation
is gone, and the guard would still report `legitimate`.

- REQ-01: The dispatch path creates a worktree per feature run at
  **`<repo root>/.claude/worktrees/<repo>/<id>/`**, and the orchestrator works inside it. For
  harness that is `<this checkout>/.claude/worktrees/harness/<id>/`. For a served repo it is that
  repo's own checkout under `workspace_root`, same shape. Two features for harness and two for
  another repo run at once: four worktrees, four branches.
- REQ-02: A worktree is cut from its own repository's default branch, never from another feature's
  branch. For harness that is `main`; for a served repo it is the `default_branch` its `fleet.yaml`
  entry declares, which is why that field exists — it is read before the checkout does.
- REQ-03: The worktree is removed when its feature reaches a terminal state, and its artifacts
  reach the default branch before removal.
- REQ-04: A governed agent that switches branch, or otherwise moves `HEAD`, during a live run is
  refused rather than trusted not to.
- REQ-05: The orchestrator's own instructions state where it works. It reaches an agent by
  preload, not by being told to go read a file.
- REQ-06: Two features closing out at the same time cannot silently lose Expertise entries.
  Whatever the merge policy is, a lost entry is DETECTED rather than trusted not to happen.
- REQ-07: A served repo's PRIMARY CLONE stays at `workspace_root/<repo>` and is not moved.
  `git worktree add` requires an existing clone, so worktrees are additional to a checkout and
  never a replacement. Nothing works in the clone directly.
- REQ-08: `WORKTREE_REL_RE` gains the repository segment. The pattern today strips
  `<segment>/<id>/`; with the repository named it must strip `<segment>/<repo>/<id>/`, or every
  write inside a worktree resolves against the wrong path and is refused.

## Success Criteria

- SC-01: With FOUR feature runs live — two on harness, two on a repo the factory serves — each
  orchestrator's commits land only on its own branch, and no working tree contains another's files.
  This is the operator's stated goal in full: two features at once for harness AND for other repos
  simultaneously. Proven by running them concurrently and inspecting every tree and branch history.
  verify: inspection
- SC-02: A worktree created for a feature run is cut from its own repository's default branch.
  Asserted against the merge-base, not against the branch name.
  verify: automated      evidence: integration
- SC-02b: A worktree at `.claude/worktrees/<repo>/<id>/` is accepted as legitimate, and one
  outside that layout is REFUSED with a message naming where worktrees belong. Both directions
  asserted, on a throwaway repository rather than this one.
  verify: automated      evidence: integration
- SC-02c: A domain-granted path written from INSIDE a worktree resolves to the same grant as from
  the checkout root. The prefix strip must remove `<segment>/<repo>/<id>/`, not
  `<segment>/<id>/` — measured 2026-08-20, today's pattern leaves the id in the path, so every
  in-worktree write would be refused. The test drives a real write for at least one agent and
  proves it FAILS before the strip is fixed.
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

- **DEC-193 does NOT need amending, and this brief said twice that it did.** The first draft
  claimed no enforcement change was needed; the second claimed legality itself had to be
  redefined. Both were answers to shapes the operator did not choose, and the settled one costs
  less than either.

  Measured 2026-08-20 on a throwaway repository with a worktree at
  `.claude/worktrees/harness/FEAT-30`: `worktree_owner()` returned `legitimate=True`. Legality is
  `commonpath` against `<owner root>/.claude/worktrees`, so a deeper path is still inside it and the
  rule holds unchanged. What DOES break is the prefix strip — `WORKTREE_REL_RE` on
  `.claude/worktrees/harness/FEAT-30/.harness/x.md` returns `FEAT-30/.harness/x.md` instead of
  `.harness/x.md`, so domain globs would miss and every in-worktree write would be refused. That is
  REQ-08 and SC-02c: one segment in one regex, in the enforcement layer, main-session-direct.
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
