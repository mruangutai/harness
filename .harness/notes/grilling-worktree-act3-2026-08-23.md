# Grilling — enforce act 3 of the worktree lifecycle (#728) — 2026-08-23

## Destination

**A worktree cannot outlive its feature.** When a FEAT-NN flow reaches `Done` on the default branch,
a post-merge hook removes its checkout automatically, and `check-state.sh` REFUSES if anything is
still standing. Two mechanisms: one closes the window, one proves it closed.

## Settled

- **How loud?** → **BLOCKING, exit 2.** Not a violation-and-continue, not a note. The operator
  confirmed the term first: "feature" means a FEAT-NN flow, the thing with a directory under
  `.harness/<repo>/features/` and a `feature.json` whose `status` reads `Done`.
- **The cost was named and accepted:** `check-state.sh` runs before every commit, so an orphaned
  FEAT-31 worktree stops a commit on FEAT-33. The pain lands on whoever is working, not on whoever
  left the checkout. The operator chose blocking with that stated.
- **A worktree whose feature directory is absent from the default branch** — an abandoned or
  never-landed flow → **OUT OF SCOPE.** Not a second finding class, not a note. Unreported, as today.
- **A feature at `Building` with NO worktree** (the inverse) → **OUT OF SCOPE.** This effort closes
  act 3 only.
- **Which worktrees?** → **every repo under `.claude/worktrees/`**, not harness alone. One sentence,
  no exception to remember or later remove.
- **A DIRTY worktree for a `Done` feature** → **still blocks, and the message must SAY it is dirty**
  and that `remove` will refuse until the changes are dealt with. Not the plain command alone.
- **The post-merge window is CLOSED AUTOMATICALLY, and a git `post-merge` hook is IN SCOPE.** The
  operator asked for automation rather than pasting a command. The hook is the only route that does
  not contradict a recorded mechanical constraint — see the orchestrator fact below. Three things it
  must carry, all named to the operator before the ruling: a TRACKED hooks directory, because
  `.git/hooks/` is not version controlled; an explicit GUARD so it never removes the tree it is
  running inside, since linked worktrees share the main repository's hooks directory; and an install
  step, because a hook nobody installs is prose again.
- **The gate is not replaced by the hook.** The hook fires on the local `pull`, never on the GitHub
  merge, so a checkout that is never pulled stays orphaned. The invariant is what catches that, and
  it stays BLOCKING.
- **Which agent removes the worktree?** → **none of the sixteen.** The main session or the hook. See
  the mechanical fact below; the operator's original ask was "orchestrator or one of the agents" and
  was withdrawn once the constraint was measured.
- **The invariant's message names the directory it actually FOUND**, whether short-named or at the
  flow id. This was fog and dissolved on a fact, not a decision: `commands/harness.md:21` already
  instructs `create --id <flow-id>`, so the four short-named worktrees on disk are operator error
  against a correct instruction, not a tool defect.

## Not yet specified

- Where the tracked hooks directory lives and how `core.hooksPath` is set per clone. Both the harness
  and a fleet repository need it, and it is not yet clear whether that is one mechanism or two.
- Whether the hook should remove EVERY eligible worktree it finds on one firing, or only the feature
  whose merge triggered it. The first is simpler and self-healing; the second is narrower. Not sharp
  enough to state as a requirement yet.

## Out of scope

- The abandoned-flow worktree, and the missing-worktree inverse. Both ruled above.
- Any ship-flow step that runs `remove` automatically. `SKILL.md:312-322` already carries that
  instruction and it is exactly the habit that failed; the gate is the answer, not another line of
  prose. Recorded in #728.

## Facts I verified (so pm does not re-derive them)

- **INV-25 already enumerates worktrees.** `check-state.sh:1076` runs
  `git worktree list --porcelain` and walks the records at `:1083-1090`. A sibling invariant reuses
  that loop; this is not new plumbing. Measured at `3ed95a4`.
- **INV-25 already prints removal guidance** (`:1148`), and `:1132` carries a deliberate comment
  refusing to print it in one case, because `git worktree remove` exits 0 from INSIDE the tree it
  deletes and would delete the caller's own working directory. Read that comment before writing a
  message.
- **The next free number is INV-28.** INV-1..INV-27 are in use; INV-20 is taken and INV-10 is retired
  and unreusable. Do NOT assume the count from the highest number — that false premise reached
  FEAT-26's dispatch and is recorded as its Q5.
- **`remove` WORKS now, as of `3ed95a4` (PR #729).** #726 and #727 are fixed, so the command the gate
  names will succeed. Before today it could not run for any feature, ever.
- **`remove`'s refusal codes, from `feature-worktree.py`:** dirty tree → exit 4 with `WOULD DISCARD`
  lines; unlanded tracked artifact → exit 5 with `MISSING`/`DIFFERS` lines; ambiguous short id →
  exit 5 naming every candidate. There is no force flag and there must not be one.
- **HAZARD — `check-state.sh:22` sets `root="${CLAUDE_PROJECT_DIR:-$(pwd)}"` and reads `feature.json`
  from the WORKING TREE, not from the default branch.** The main checkout is frequently on a `chore/`
  branch — it was for most of 2026-08-23 — so "status on the default branch" is NOT what a plain file
  read returns. The invariant must resolve the default branch's copy explicitly, and a test must
  cover the case where the working tree disagrees with it. This is the same class of defect as the
  stale worktree the invariant exists to catch.
- **THE MECHANICAL CONSTRAINT THAT RULES OUT EVERY AGENT.** `SKILL.md:323-325`: act 3 is never the
  orchestrator's, because `git worktree remove` exits 0 when run from INSIDE the tree it deletes, so
  an agent following that instruction deletes its own working directory mid-run. This binds every
  agent dispatched into the worktree, leads and members alike. The main session is the only tier
  structurally outside it. `check-state.sh:1132` carries the same warning for the same reason.
- **`post-merge` FIRES ON BOTH MERGE SHAPES.** Measured 2026-08-23 in a throwaway repository, not
  recalled: a fast-forward merge fired it with `$1 = 0` and `git merge --squash` plus commit fired it
  with `$1 = 1`. It does NOT fire on commit, checkout or fetch. In practice it fires on the `git pull`
  after a PR merges — six times on 2026-08-23, once per PR.
- **`.git/hooks/` is NOT version controlled**, and linked worktrees SHARE the main repository's hooks
  directory. Those two facts are what make the hook a feature rather than a line of config.
- **Measured 2026-08-23:** four worktrees were open, two for `Done` features. One was read during a
  status question and answered `Review` for a feature that is `Done`. That is the concrete harm.

## Ruling, added 2026-08-23 after the validator panel's B-1

**REQ-05 keeps reading the LOCAL default branch. The Goal's claim is WITHDRAWN, not the mechanism.**

**What was wrong.** The Goal justified two mechanisms by saying the hook fires on the local `pull`
and never on the GitHub merge, so a clone that is never pulled stays orphaned and only the gate
catches it. **That is false.** `feature-worktree.py:287` resolves the landed blob against the LOCAL
ref, and `:373` prints "Compared against LOCAL" in its own output. In a never-pulled clone, local
`main` does not read `Done` either, so NEITHER mechanism fires. The main session wrote that
justification and the panel found it.

**What is true, and what the Goal must say instead:** the gate catches a clone where the hook is
missing, not installed, or failed. That is a real and different case, and it is why two mechanisms
still each earn their place.

**Rejected, with the cost that rejected them.** Reading `origin/<default_branch>` reproduces the
same hole one level out — that ref is only as fresh as the last fetch — and it gives a pre-commit
gate network-adjacent semantics it does not have today. Fetching before reading closes the hole for
real and turns a correctness check into an availability dependency: slow, and broken offline.

## Facts the validator panel corrected — the main session had these WRONG

- **The registration trap is NOT silent for `bin/`.** `run-unit-tests.sh:48-61` prints
  `MISCONFIGURED` and exits 2 before running anything, and integration's `cmd` is that script. The
  trap is open ONLY for a test file placed outside `BIN_DIR` — which is the live risk for SC-06,
  SC-07 and SC-08, because they grade a hook and an install step rather than a bin script.
- **`integration.detect` holds 22 explicit filenames, not 23.** Twenty-three pipe-separated entries,
  one of which is the `tests/integration/**` glob. Both sides of the mirror agree; no drift.
- **SC-09 is confirmed RED today** by three independent counts: 16 agents, only
  `harness-orchestrator.md:9` preloads `harness`, and zero occurrences of "worktree" across the three
  universal skills.
- **SC-01's `exits 2` half does not discriminate.** `test-check-state.py:1214-1218` already records
  as a measurement that exit code is non-discriminating in this fixture family — the fixture is red
  for other reasons, so `code != 0` passes whether or not INV-28 fires. Grade on the line prefix, not
  the exit status.
