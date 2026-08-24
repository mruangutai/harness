<!-- invariants: 29 -->
<!-- The EXPLICIT claim, read by check-plan-routes.py. Declared rather than left to a
     prose scan because this brief also CITES INV-28 while recording why the number
     moved, and a scanner cannot tell a claim from a citation. FEAT-26's T-05 holds
     INV-28 and builds first, measured 2026-08-23. -->

# BRIEF — FEAT-34 Worktree act 3, enforced

## Problem

**A worktree outlives its feature, and nothing notices.** Act 3 of the worktree lifecycle —
removal at a terminal state — is prose in `.claude/skills/harness/SKILL.md:321` and nothing else.
Measured 2026-08-23 during the grilling (`.harness/notes/grilling-worktree-act3-2026-08-23.md`):
four worktrees stood open, two of them for features already at `Done`, and one of those stale
checkouts was read during a status question and answered `Review` for a feature that was `Done`.
A wrong answer from a directory that should not have existed. Re-measured at `3ed95a4`, two
worktrees remain — `FEAT-26` (`Ready`) and `FEAT-33`, whose feature directory is absent from
`main` altogether — so the specific stale pair has since been cleaned by hand, which is the
point: the only mechanism today is somebody remembering.

Two aggravating facts, both measured rather than recalled. First, the habit the prose asks for is
the one that failed, and it cannot be fixed by more prose: `SKILL.md:325` records that
`git worktree remove` exits 0 from **inside** the tree it deletes, so an agent obeying the
instruction deletes its own working directory mid-run. Second, the prohibition that follows from
that fact reaches exactly **one** of the sixteen agents: the act-3 statement lives only in
`.claude/skills/harness/SKILL.md`, preloaded by `harness-orchestrator` alone. `harness-team`
mentions worktrees (`:90`) but never removal; `harness-handoff`, `harness-expertise` and
`harness-principles` — the three universal skills — do not mention it at all. Fifteen agents
carry no statement of the rule they are bound by.

## Goal

A worktree cannot outlive its feature. When a FEAT-NN flow reaches `Done` on the default branch,
its checkout is removed automatically as the merge lands locally, and `check-state.sh` refuses
outright if one is still standing. Two mechanisms, kept distinct on purpose: the hook closes the
window, the invariant proves it closed. **The hook does not replace the invariant** — the hook
lives in a clone's own hooks path, so in any clone where it is missing, was never installed by the
setup step, or failed on the merge, the checkout stays standing and only the invariant catches it.
Both mechanisms read the **local** default branch (`feature-worktree.py:287` resolves
`git rev-parse <default_branch>:<rel>`, and `:373` prints "Compared against LOCAL
<default_branch>" in its own output), so a clone that never pulls is outside the reach of both —
by decision, not by oversight: reading `origin/<default_branch>` reproduces the same hole one level
out, since that ref is only as fresh as the last fetch, and fetching before reading turns a
pre-commit gate into an availability dependency. Neither is reintroduced.

## Requirements

- REQ-01: A worktree whose feature reads `status: Done` on the **default branch** makes
  `check-state.sh` REFUSE — a blocking finding at exit 2, not a note and not a
  violation-and-continue.
- REQ-02: The refusal names the worktree directory it actually found, and the exact command that
  removes it.
- REQ-03: When that worktree has uncommitted changes, it still refuses, and the message says the
  tree is dirty and that `remove` will decline until the changes are dealt with — not the bare
  command alone.
- REQ-04: The refusal covers **every** repository's worktrees under `WORKTREES_SEGMENT`, with no
  per-repository exception to remember or later remove.
- REQ-05: The status the refusal reads is the **default branch's** copy of `feature.json`. A
  working tree sitting on a `chore/` branch can neither make the finding fire early nor keep it
  silent late.
- REQ-06: A worktree is exempt **only** when the default branch genuinely carries no feature
  directory for it — the abandoned-flow class stays unreported, as today. A lookup that returns
  nothing for any **other** reason is not an exemption and must still refuse: a short-named
  worktree whose id does not resolve to the directory that exists on the default branch, a
  `feature.json` present but unparseable, or an enumeration or git command that errors. Absence
  of the directory is the exempting fact; failure of the lookup is not.
- REQ-07: When a merge lands the default branch locally and a feature it carries reads `Done`,
  that feature's worktree is removed without anyone running a command.
- REQ-08: The automatic removal never removes the worktree the removing process is running
  inside, and says why it declined.
- REQ-09: A fresh clone acquires the automation by running a named setup step — nobody hand-authors
  or hand-copies a file into an untracked directory to get it.
- REQ-10: The statement that removing a worktree is not an agent's act is reachable by **every**
  agent that can be dispatched into a worktree, not by the orchestrator alone.

## Constraints

**What SUPPLIES this feature (already built — do not strike, do not rebuild):**

- **INV-25's worktree enumeration.** `check-state.sh:1076` runs
  `["git", "worktree", "list", "--porcelain"]` and walks the records at `:1086-1094`. A sibling
  invariant reuses that loop; this is not new plumbing. *(Re-verified at `3ed95a4`.)*
- **INV-25's removal-guidance precedent.** `:1148` prints `git worktree remove <path>`, and
  `:1132` carries a deliberate comment refusing to print it when the session is rooted in the
  tree, for the same mechanical reason as `SKILL.md:325`. Read that comment before writing any
  message. *(Re-verified at `3ed95a4`.)*
- **`feature-worktree.py remove` works**, as of `3ed95a4` (PR #729, closing #726 and #727), so the
  command a message names will actually succeed. Its refusals: dirty tree → exit 4 with
  `WOULD DISCARD` lines; unlanded artifact → exit 5 with `MISSING`/`DIFFERS` lines; ambiguous
  short id → exit 5 naming every candidate. **There is no force flag and there must not be one.**
- **Default-branch resolution already exists.** `feature-worktree.py` `resolve_repo` returns a
  `default_branch` per repository (`harness` → `main`; a fleet repo → its `default_branch` field)
  and `:287` already reads a landed blob with `git rev-parse <default_branch>:<rel>`. REQ-05 has a
  mechanism to reuse rather than invent.
- **`post-merge` fires on both merge shapes.** Measured 2026-08-23 in a throwaway repository: a
  fast-forward merge fired it with `$1 = 0`, and `git merge --squash` plus commit fired it with
  `$1 = 1`. It does **not** fire on commit, checkout or fetch. In practice it fires on the
  `git pull` after a PR merges.
- **DEC-95, DEC-193** define the worktree as the unit of concurrency and fix the two legal code
  locations. **DEC-143** fixes how the guard resolves a path inside a worktree.

**What BLOCKS or bounds:**

- **DEC-174 amendment 4 — the enforcement-layer carve-out, and it bites hard here.** The
  enumeration is `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`,
  **`check-state.sh`**, `check-plan-routes.py`, `dispatch-guard.sh`, **and the test file of each**.
  This feature changes `check-state.sh` and `test-check-state.py`, so **the plan round must lane
  those tasks `execution_mode: main-session-direct`** (with DEC-179's resolution) rather than
  discovering it mid-run. The amendment's own working rule applies to any helper: a module a gate
  imports is not itself a gate — a squad may write the library, but **the cutover that makes the
  gate use it is main-session-direct**, proven by showing the violation set is identical before
  and after.
- **The new invariant is INV-29, not INV-28.** The number is not inferred from the highest in the
  gate script — INV-20 is taken and INV-10 is retired and unreusable, and that exact false premise
  reached FEAT-26's dispatch and is recorded as its Q5. Measured 2026-08-23 at `3ed95a4`: the
  free-number check has two halves, and the second one moved this feature. `check-state.sh`
  contains zero occurrences of either `INV-28` or `INV-29`, but
  `.harness/harness/features/FEAT-26-pr-linkage-recorded/plan.yaml` uses `INV-28` sixteen times
  (its T-05 adds it), FEAT-26 is signed and already in ship, and the operator ruled 2026-08-23 that
  it builds first. `INV-29` occurs nowhere under `.harness/` or `.claude/` at that sha. A
  signed-but-unbuilt plan claims a number just as firmly as the gate script does.
- **`.git/hooks/` is not version controlled**, and linked worktrees **share the main repository's
  hooks directory**. Those two facts are what make REQ-07 through REQ-09 a feature rather than a
  line of config.
- **The blocking cost is accepted, not open.** `check-state.sh` runs before every commit, so an
  orphaned FEAT-31 worktree stops a commit on FEAT-33. The pain lands on whoever is working, not
  on whoever left the checkout. The operator chose blocking with that stated.
- **`integration`'s `detect` is almost entirely an explicit file enumeration.** Measured at
  `3ed95a4`: 23 pipe-separated entries, of which 22 are literal filenames under
  `.claude/skills/harness/bin/` and one is the `tests/integration/**` glob;
  `run-unit-tests.sh:18`'s `INTEGRATION_SCRIPTS` holds the same 22, so the two sides agree today.
  Any new test file this feature adds must be registered in both. **The trap is loud, not silent,
  for anything under `BIN_DIR`** (`run-unit-tests.sh:5`): `:48-61` prints `MISCONFIGURED` and exits
  2 before running a thing, and `integration`'s `cmd` is that script. The trap is open **only for a
  test file placed outside `BIN_DIR`** — the live risk here, because SC-06, SC-07 and SC-08 grade a
  git hook and an install step that may not live in `bin/`. `run-unit-tests.sh:110-115` reports
  `KIND-DRIFT` when the two lists disagree.

**Out of scope, ruled by the operator:**

- A worktree whose feature directory is absent from the default branch (REQ-06 makes this
  explicit). Not a second finding class, not a note.
- The inverse case: a feature at `Building` with **no** worktree. This effort closes act 3 only.
- Any ship-flow prose step that runs `remove`. `SKILL.md:321` already carries that instruction and
  it is exactly the habit that failed; the gate is the answer, not another line of prose.
  Recorded in #728.
- A dedicated agent spawned to run `remove`. **None of the sixteen removes a worktree** — the main
  session or the hook, and REQ-10 makes the rule reachable.

## Success Criteria

- SC-01: With a fixture whose default-branch `feature.json` reads `Done` and whose worktree is
  present, `check-state.sh` emits an `INV-29` finding at blocking severity; with the same fixture
  at `Review`, no `INV-29` finding appears. **Severity is asserted on the finding line's own
  prefix, never on the run's exit code** — `test-check-state.py:1214-1218` records as a
  measurement that these fixtures are red for other reasons, so `code != 0` passes whether or not
  the invariant fires. That firing line also carries **the removal command with the found
  worktree's own path substituted into it**, asserted as one exact string composed from the
  fixture's path — this is what grades REQ-02's second clause on the plain (non-dirty) refusal.
  Red proof, three inputs that must make it fail: a message naming the directory but carrying no
  command; a bare removal command with no path; a command carrying a different worktree's path.
  Every assertion must be demonstrated failing before the invariant exists.
  verify: automated        evidence: integration
- SC-02: **The deadlock case.** A fixture where the *working tree* says `Done` while the *default
  branch* says `Review` produces **no** `INV-29` finding; the inverse — default branch `Done`,
  working tree `Review` — produces one. An implementation that reads the working tree fails both
  halves, and that failing state must be demonstrated.
  verify: automated        evidence: integration
- SC-03: For a `Done` feature whose worktree has an uncommitted change, `INV-29` still fires and
  its message asserts both that the tree is dirty and that `remove` will decline until the changes
  are dealt with. Graded per clause, not by one substring match.
  verify: automated        evidence: integration
- SC-04: A fixture containing a `Done` feature in a **second** repository under
  `WORKTREES_SEGMENT` produces an `INV-29` finding for it. A harness-only implementation fails
  this case.
  verify: automated        evidence: integration
- SC-05: One fixture, four standing worktrees, each graded by its own assertion: (a) a worktree
  whose feature directory is genuinely absent from the default branch produces **no** `INV-29`
  finding; (b) a full-named `Done` sibling in the same fixture produces one; (c) a **short-named**
  worktree whose full-named directory on the default branch reads `Done` produces one — the lookup
  by that id fails, the exemption must not; (d) a worktree whose default-branch `feature.json` is
  present but unparseable produces one. An implementation that keys the exemption on "the lookup
  returned nothing" passes (a) and (b) and **fails (c) and (d)** — that is the red proof, and it is
  the over-suppression that would make every refusal in REQ-01..REQ-05 silently stop firing. The
  live tree is NOT this fixture: at `3ed95a4` the standing `FEAT-33` worktree is short-named **and**
  genuinely absent from `main`, so it cannot discriminate (c) from (a).
  verify: automated        evidence: integration
- SC-06: In a throwaway repository, the hook removes the merged feature's worktree on **both**
  measured shapes — fast-forward (`$1 = 0`) and `merge --squash` plus commit (`$1 = 1`) — and each
  shape is asserted separately.
  verify: automated        evidence: integration
- SC-07: Invoked with its cwd inside a linked worktree that is itself eligible, the hook leaves
  that worktree standing and reports why it declined. Red proof: an unguarded hook deletes it and
  the assertion fails.
  verify: automated        evidence: integration
- SC-08: In a fresh clone fixture, the automation is absent and reported as not installed before
  the named setup step runs, and after it runs `core.hooksPath` resolves to the tracked directory
  and the hook is executable. Both halves asserted.
  verify: automated        evidence: integration
- SC-09: For **each of the sixteen agents** in `.claude/agents/`, at least one preloaded skill
  states that removing a worktree is not that agent's act — asserted per agent, never by a
  file-global count. Fifteen of sixteen fail this today at `3ed95a4`, which is its red proof.
  verify: inspection
- SC-10: `bash .claude/skills/harness/bin/check-state.sh` reports no violation attributable to
  this feature's own artifacts, and the full `integration` kind passes, at the pinned `review_sha`
  read with `git show <review_sha>:<path>` rather than from the working tree.
  verify: automated        evidence: integration

## Verification gaps

- **No runner covers "the hook fires on this operator's machine."** Every SC above grades the hook
  *script* and the *install step* in fixtures. Whether `core.hooksPath` is actually set in the
  operator's own clone, and whether a real PR merge therefore removes a real worktree, is carried
  by INV-29 — which is precisely why the invariant is not replaced by the hook. Worth one UAT
  observation at ship, not an SC that a fixture can fake.
- `component`, `ui`, `eval` and `typecheck` all have `cmd: null` in `.harness/harness.json`. None
  of them detects any file this feature touches, so no SC rests on a null kind.
- **`integration` is active, but a test file placed OUTSIDE `.claude/skills/harness/bin/` and not
  registered in `detect` is a runner matching zero files** — a gate that looks real and does
  nothing, and the one registration failure that is silent (see Constraints; inside `BIN_DIR` the
  runner exits 2 loudly instead). SC-06, SC-07 and SC-08 grade a git hook and an install step, so
  they are exactly where this can happen. Registration is part of the work, not an afterthought.

## Open Questions

Two fog patches carried forward from the grilling artifact's `## Not yet specified`, deliberately
**not** sharpened into requirements — neither can be stated precisely without inventing structure,
and pre-slicing them would decide at brief time what belongs in the plan or to the operator.

- **Q1 (operator's, non-blocking on signature):** where the tracked hooks directory lives and how
  `core.hooksPath` is set per clone. REQ-09 states the *outcome* — a fresh clone acquires it by a
  named step — and stops there. Whether the harness and a fleet repository share one mechanism or
  need two is undecided, and REQ-07 through REQ-09 are written to be satisfied by either.
- **Q2 (plan round's, resolvable as a D-NN):** whether one `post-merge` firing removes **every**
  eligible worktree it finds or only the feature whose merge triggered it. REQ-07 and SC-06 are
  written to be neutral — both readings satisfy them — so this does not block the signature.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-23
