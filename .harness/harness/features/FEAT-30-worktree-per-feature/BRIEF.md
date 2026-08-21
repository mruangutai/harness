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

### Terms

Five names carry every path in this brief. Each one already exists in the code, so this table says
where it is defined and what it holds. Values measured 2026-08-20.

| Term | What it is | Defined at | Value here |
|---|---|---|---|
| `workspace_root` | The CONTAINER directory holding every served repository's checkout. One directory, many repositories. | `.harness/factory/fleet.yaml:25`, read by `factory_config.py:197` | `/Users/molchairuangutai/GitHub/harness-factories` |
| `owner_root` | ONE repository's checkout. `worktree_owner()` returns it, read from the worktree's own `.git` pointer file. | `harness_boundary.py` — `worktree_owner()` returns `(checkout_dir, owner_root, legitimate)` | `…/harness-factories/kaya-ai` for kaya-ai |
| `harness_root` | The harness checkout's own root. It IS the `owner_root` when the repository is harness — one directory, two names, because two modules reach it two ways. | `factory_config.py:44` — `harness_root()` | `/Users/molchairuangutai/GitHub/harness` |
| `WORKTREES_SEGMENT` | The path segment under an `owner_root` where linked worktrees are legal. A constant, cited by name so the value is never spelled twice. | `harness_boundary.py:33` — `WORKTREES_SEGMENT = ".claude/worktrees"` | `.claude/worktrees` |
| `<repo>` | The repository name AFTER the owner. `mruangutai/kaya-ai` gives `kaya-ai`. | `factory_config.py:334` — `workspace_path()` | `harness`, `kaya-ai` |

`<id>` is the feature id — `FEAT-30`.

**`harness_root` is NOT under `workspace_root`, and that is deliberate.** `fleet.yaml:10` records
`mruangutai/harness` as absent on purpose (DEC-174 am.1). Harness develops itself in its own
checkout, so it has an `owner_root` and no `workspace_root` entry.

So a worktree path is `owner_root`/`WORKTREES_SEGMENT`/`<repo>`/`<id>`/, which expands to:

    harness         /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-30/
    kaya-ai         /Users/molchairuangutai/GitHub/harness-factories/kaya-ai/.claude/worktrees/kaya-ai/FEAT-30/

**`workspace_root` and `owner_root` are NOT the same thing, and conflating them loses the
isolation this feature exists to build.** Every path in this brief is relative to an `owner_root`,
never to `workspace_root`. `worktree_owner()` computes legality as `commonpath` against
`owner_root`/`WORKTREES_SEGMENT`, where the owner comes from the worktree's own `.git` pointer
file. Build it against `workspace_root` instead and every served repository's worktrees share one
directory — the per-repository isolation is gone, and the guard would still report `legitimate`.

### The location rule

Settled by the operator 2026-08-20 and stated as three facts so nobody re-derives it:

1. **`workspace_root` is for every repository EXCEPT harness.** `fleet.yaml` declares them and
   `workspace_root`/`<repo>` holds each one's checkout, outside this repository.
2. **Harness's worktrees hang off `harness_root`, never off `workspace_root`.** `fleet.yaml`
   excludes `mruangutai/harness` on purpose (DEC-174 am.1) so that this stays true, and the absence
   is what enforces it. Every repository uses `WORKTREES_SEGMENT`; what differs is the `owner_root`
   it hangs from.
3. **The repository is NAMED in the path** — `WORKTREES_SEGMENT`/`<repo>`/`<id>`/ — so a reader can
   see which repository a working tree belongs to without inferring it.

### The requirements

- REQ-01: The dispatch path creates a worktree per feature run at
  **`owner_root`/`WORKTREES_SEGMENT`/`<repo>`/`<id>`/**, and the orchestrator works inside it. The
  shape is one shape, applied per repository — see *Terms* above for the two expansions. Two
  features for harness and two for a served repository run at once: four worktrees, four
  branches.
- REQ-02: A worktree is cut from its own repository's default branch, never from another feature's
  branch. For harness that is `main`; for a served repo it is the `default_branch` its `fleet.yaml`
  entry declares, which is why that field exists — it is read before the checkout does.
- REQ-03: The worktree is removed when its feature reaches a terminal state, and its artifacts
  reach the default branch before removal.
- REQ-04: **SCOPED 2026-08-20, operator ruling — the refusal binds ALL SIXTEEN governed agents,
  `harness-dev-ops` included.** A governed agent that switches branch, or otherwise moves `HEAD`,
  during a live run is refused rather than trusted not to.

  The original text was silent on `harness-dev-ops`, and silence resolved to *exempt*:
  `bash-write-guard.sh:56-57` returns exit 0 for that persona before line 58's `harness-` prefix
  test, so a rule keyed off that prefix provably never reaches it — and T-01, T-02 and T-08 are
  laned to exactly that persona. The scoping is therefore what makes the requirement true of the
  agents most likely to move `HEAD`.

  **Why this does not contradict DEC-151.** That entry scopes the exemption to **target paths** —
  the authority at `DECISIONS.md:3650` reads *"Every other harness agent except dev-ops (exempt per
  DEC-85 — owns builds) gets extractable target paths checked against its team-config domain"* — and
  moving `HEAD` is not a target path. The exemption exists to preserve one recovery path: when the
  guard itself is broken, `harness-dev-ops` can still write. Placing the `HEAD` matcher ahead of the
  exemption removes nothing from that path — dev-ops keeps its exemption for every WRITE, including
  writes to the guard's own source.

  **And DEC-151 grounds the exemption in DEC-85, which cuts the same way.** DEC-85 is cited for
  "owns builds", and at `:1092` it explicitly corrects the premise that dev-ops is special on this
  route: *"All 9 doers hold `Bash` (not just `dev-ops`, as §4.2 claimed)."* So exempting dev-ops
  from a Bash-route `HEAD` refusal has less grounding than the exemption's own basis supplies, not
  more.

  **Citation corrected 2026-08-20.** The three preceding drafts of this paragraph quoted
  `DECISIONS-INDEX.md:170` — a generated summary row — as though it were the ruling. Three tiers
  argued REQ-04 from that row before anyone opened the entry. Substance is unchanged; the authority
  is stronger than the summary was.

  **The accepted cost, recorded rather than buried.** When `HEAD` is wrong and the guard is
  working, `harness-dev-ops` cannot fix it either. The repair is the operator's, from the main
  session, which carries no `agent_type` and which this guard does not bind.
- REQ-05: The orchestrator's own instructions state where it works. It reaches an agent by
  preload, not by being told to go read a file.
- REQ-06: Two features closing out at the same time cannot silently lose Expertise entries.
  Whatever the merge policy is, a lost entry is DETECTED rather than trusted not to happen.
- REQ-07: A served repo's PRIMARY CLONE stays at `workspace_root/<repo>` and is not moved.
  `git worktree add` requires an existing clone, so worktrees are additional to a checkout and
  never a replacement. Nothing works in the clone directly.
- REQ-08: The guard resolves an in-worktree path by asking WHICH CHECKOUT it is standing in and
  relativizing against that, replacing the fixed-segment `WORKTREE_REL_RE` strip. Operator ruling,
  2026-08-20, after asking why segment-counting code was needed at all.

  The regex is why naming the repository in the path breaks permissions: it removes a fixed number
  of segments, so a longer path leaves the wrong remainder and matches no grant. `worktree_owner()`
  already returns the containing checkout and is already called in this module, so the information
  needed is present — it was just being reconstructed by pattern instead of used.

  **Measured 2026-08-20, both options, 2000 iterations:** regex 0.3 ms total, walk-and-relativize
  46.8 ms total. 150x slower and still **0.023 ms per write**, against a guard that already reads
  files. The regex buys speed nobody needs at the price of coupling the guard to one path shape,
  and that coupling bills again on every future layout change. This is a SIMPLIFICATION, not an
  addition: one mechanism replaces one mechanism, and the segment count stops being load-bearing.

## Success Criteria

- SC-01: FOUR worktrees exist at once — two for harness, two for a repo declared in `fleet.yaml` —
  and none can see another's files or branch. Asserted mechanically: create all four, write a
  distinct file from each, and prove every tree contains its own file and NOT the other three, and
  that each `HEAD` names only its own branch. This is the operator's stated goal in full — two
  features at once for harness AND for other repos simultaneously — so it is the criterion that runs
  every time, not one graded once by eye.
  verify: automated      evidence: integration
- SC-01b: **AMENDED 2026-08-20, operator instruction — automated, not `uat`.** FOUR CONCURRENT
  writers, two per repository, each committing into its own worktree, with every commit landing
  only on its own branch and NO other branch advancing. Concurrent, not serial: the four writers
  synchronise on a barrier and the test asserts their write windows actually overlapped, because a
  serialised fixture asserts nothing about contention.
  **The discriminating negative is part of the criterion, not an extra:** the SAME four-writer
  scenario, driven against ONE shared checkout instead of four worktrees, must be DETECTED by the
  same isolation predicate. A four-worktree concurrency test that also passes when isolation is
  broken is worse than the `uat` it replaces.
  The original text's other clauses are dropped rather than automated, and each for a stated
  reason: the shared account budget and the shared board are **out of scope by operator ruling**
  (see *Out of scope, deliberately* below), so a criterion asserting them asserted something this
  brief excludes; and Expertise-file contention is REQ-06's and SC-08's job, already `automated`.
  What remains is what SC-01's static four-tree check cannot reach — commits, under contention.
  verify: automated      evidence: integration
- SC-02: A worktree created for a feature run is cut from its own repository's default branch.
  Asserted against the merge-base, not against the branch name.
  verify: automated      evidence: integration
- SC-02b: A worktree at `owner_root`/`WORKTREES_SEGMENT`/`<repo>`/`<id>`/ is accepted as
  legitimate, and one outside that layout is REFUSED with a message naming where worktrees belong. Both directions
  asserted, on a throwaway repository rather than this one.
  verify: automated      evidence: integration
- SC-02c: A domain-granted path written from INSIDE a worktree resolves to the same grant as from
  the checkout root, **for every one of the 16 agents**, and the resolution does not depend on how
  many segments the worktree path has. Proven by resolving each agent's grants at a worktree depth
  the old regex could not handle. Today's pattern leaves the id in the path and matches nothing, so
  the test must be shown to FAIL before the change — a test written after it would pass and prove
  nothing.
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

**There are none, and this section says so rather than being omitted** (DEC-163). It exists because a
kind with `cmd: null` in `harness.json` has NO RUNNER: qa resolves it to a soft skip, so a criterion
resting on it can never be met and never fails loudly — a gate that looks real and does nothing.

- `functional`, `component`, `ui`, `eval` and `typecheck` all have `cmd: null`. **No criterion above
  rests on any of them.** Every `automated` criterion is pinned to `integration`, which runs via
  `run-unit-tests.sh --kind integration`.
- **11 of 12 criteria are `automated`, and NONE is `uat`.** SC-01b was the single `uat` criterion
  until the operator's 2026-08-20 instruction; it is now `automated / integration` and owned by
  T-10. Its former reason — four live orchestrators contending for one account budget — named
  clauses this brief puts out of scope, so what was left was automatable and is now automated.
  SC-06 remains `inspection` because it is a `grep` over two instruction files. Nothing is left to
  a human.

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
  `commonpath` against `owner_root`/`WORKTREES_SEGMENT`, so a deeper path is still inside it and the
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

status: approved
approved_by: operator (Mike Ruangutai), via main session
date: 2026-08-20
