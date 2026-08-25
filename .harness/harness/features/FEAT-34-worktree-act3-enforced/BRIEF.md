<!-- invariants: [29, 30] -->
<!-- The EXPLICIT claim, read by check-plan-routes.py. Declared rather than left to a
     prose scan because this brief also CITES INV-28 while recording why the number
     moved, and a scanner cannot tell a claim from a citation. FEAT-26's T-05 holds
     INV-28 and builds first, measured 2026-08-23.
     AMENDED 2026-08-24 (issue #806, RE-SIGNED same day): the list gains 30, the milestone
     invariant. Derived at 9165162, not inferred from the gate script's highest: INV-28 has
     since BUILT into check-state.sh (:1044, :1068, :1080) so the brief's original premise
     that the script holds neither 28 nor 29 is stale; INV-29 is claimed by this brief; and
     `grep -rn 'INV-30' .harness/ .claude/` returns zero occurrences, so 30 is free on both
     halves of the rule check-plan-routes.py enforces. -->

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
- SC-06 (AMENDED, Amendment 4): In a throwaway repository, the hook removes the merged feature's
  worktree on the **fast-forward** shape (`$1 = 0`), asserted on that shape alone. **The squash
  clause is struck as unsatisfiable by any implementation, not as unmet.** Measured: `git merge
  --squash` fires `post-merge` with `$1 = 1` while the default branch ref still points at its
  PRE-squash commit — `git cat-file -e HEAD:<feature.json>` exits non-zero at hook-fire time — and
  the separate `git commit` that completes the squash **does not re-fire the hook**. So a feature
  landed BY the squash is invisible when the hook runs and visible only when nothing will run again.
  That is git's behaviour, not the sweep's, and no code change closes it. What replaces the struck
  clause: the hook on the squash path must record nothing and remove nothing, asserted as silence
  rather than as a removal.
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

## Amendment 1 (2026-08-24) — two additions: the terminal `Done` write, and the per-clone `core.hooksPath` prerequisite

**NOT YET RE-SIGNED. The `## Approval` block below records what was signed on 2026-08-23 and is
unchanged; this amendment is presented for re-signature at the plan signature.**

**One amendment, both additions, one re-signature.** Issue #806's terminal `Done` write (part A) and
the `core.hooksPath` prerequisite (part B) are each scope beyond the 2026-08-23 signature. They are
not separated into two amendments because they are re-signed together, in one act, and a second
amendment would invite half a signature.

**Why it belongs here and not in its own feature.** A hook that fires when a feature reaches `Done`
cannot fire if nothing reliably writes `Done`. #806 is this feature's missing prerequisite, not its
neighbour, and it rides the SAME trigger this feature already uses — the merge landing locally on the
default branch.

**Measured at `9165162` on 2026-08-24, and the premise holds.** 24 features read `status: Done` with a
milestone recorded. Ten of those milestones — 4, 5, 6, 7, 8, 10, 16, 17, 20, 21 — carry
`closed_at` timestamps inside a four-second window, `2026-08-24T14:07:46Z` through
`2026-08-24T14:07:50Z`, while their pull requests merged between `2026-08-06T00:41:45Z` (#136) and
`2026-08-23T01:20:31Z` (#721). `cmd_ship` closes the milestone unconditionally once entered, so a
milestone that stayed open for one to eighteen days after its merge and then closed in a batch is
proof that `ship` never ran on the merge. **Skipping `ship` is the normal case, not an accident.**
The batch close is a hand repair performed after the measurement; the harm it repaired is the record.

**The ruling — the same two-mechanism architecture this brief already argues.** One post-merge hook
does both jobs in the order the state requires: **record the terminal status, then remove the checkout
that status makes obsolete.** And `check-state.sh` gains an invariant refusing a `Done` feature whose
milestone is open. The brief's own words for the worktree half carry over unchanged: *the hook closes
the window, the invariant proves it closed.*

**The invariant keys on the milestone, never on the status agreeing with itself.** `status: Done` has
more than one path that can write it — #806's own repair wrote it by hand. The milestone has exactly
one, `cmd_ship`.

### Part B — the tracked hook cannot run in any clone, this one included

**Measured at `9165162`, in this checkout:**

```
$ git config --get core.hooksPath
/Users/molchairuangutai/GitHub/harness/.git/hooks
```

An absolute path carrying a username. It is not merely unset — it is set to a value no other clone
can have, and `harness-init` installs no step that sets it. So REQ-09's outcome ("a fresh clone
acquires the automation by running a named setup step") has, today, no step to run: the tracked hook
directory does not exist and nothing points git at one.

REQ-09 and SC-08 already state the outcome and grade both of its halves, and neither is restated
here. What the signature of 2026-08-23 does not cover is the behaviour the operator added when
answering Q1: the setup step must be **idempotent**, and when `core.hooksPath` is already set to
something the harness did not write, it must **say what it found** rather than silently displace an
operator's own hooks directory. `core.hooksPath` takes over hook resolution for the entire clone —
that is the mechanism's cost, and stating what was displaced is the whole of the mitigation.

The second uncovered thing is the wiring itself. SC-08 grades that the path resolves and the hook
file is executable; SC-06 and SC-07 grade the sweep body, installed by hand into a fixture's
`.git/hooks/`. **Nothing today grades that the tracked hook actually reaches the sweep body**, so a
shim pointing at a path that does not exist satisfies every criterion in the signed brief.

This also closes `## Open Questions` Q1. Where the tracked directory lives is a design choice with no
existing answer to look up, and it is recorded as a `D-NN` in `plan.yaml`, not as a requirement.

### Added requirements

- REQ-11: When a merge lands the default branch locally and a feature it carries has reached its
  terminal state, that feature's terminal status and its milestone closure are recorded without
  anyone running a command.
- REQ-12: A feature whose recorded status is `Done` while its recorded milestone is still open is
  reported by `check-state.sh`. The **milestone** is the fact keyed on, because it has exactly one
  writer; the status does not corroborate itself.
- REQ-13: The setup step that points a clone at the tracked hooks directory can be run repeatedly
  with the same result, and when it finds `core.hooksPath` already set to a value it did not write,
  it reports what it found. An operator's own hooks directory is never displaced silently.

### Added success criteria

- SC-11: In a fixture carrying two terminal features and a stubbed `gh`, the sweep records each
  feature's terminal status and closes each feature's milestone, **asserted per feature** rather than
  by a total call count. Red proof: an implementation that records the triggering feature only passes
  a count-based assertion and fails the per-feature one.
  verify: automated        evidence: integration
- SC-12: Three clauses, each asserted separately. A fixture whose `Done` feature has an open recorded
  milestone produces an `INV-30` finding; the same fixture with that milestone closed produces none;
  and with GitHub unreachable the run produces neither an `INV-30` finding nor an error, matching
  INV-26's established offline posture at `check-state.sh:1205`. An implementation that keys on
  `status` alone fails clause two, since the status is `Done` in both.
  verify: automated        evidence: integration
- SC-13: Three clauses, each asserted separately. In a fresh clone fixture the setup step run twice
  leaves `core.hooksPath` at the same value and exits 0 both times; run against a clone whose
  `core.hooksPath` is already set to an unrelated directory, it reports the value it found on stdout
  and names it; and no run leaves the clone pointing at a directory the harness did not write without
  having said so. Red proof: an implementation that unconditionally writes the config passes clause
  one and fails clause two, and that failing state is demonstrated before the step is written.
  verify: automated        evidence: integration
- SC-14: In a fresh clone fixture, after the setup step and with no hook hand-installed into
  `.git/hooks/`, a real merge that lands a terminal feature removes that feature's worktree. This
  grades the tracked hook's wiring end to end. Red proof: a shim whose target path does not exist
  satisfies SC-08 in full and fails this.
  verify: automated        evidence: integration

### Added verification gaps

- **This operator's own clone is graded by nobody.** SC-13 and SC-14 grade a fresh clone FIXTURE.
  Whether the working clone at `/Users/molchairuangutai/GitHub/harness` — measured at `9165162`
  pointing `core.hooksPath` at `/Users/molchairuangutai/GitHub/harness/.git/hooks` — is ever
  repointed is an act the operator performs, carried by INV-29's refusal and by one UAT observation
  at ship. It is deliberately not an SC, because a fixture can fake it and this one cannot be faked.
- **INV-30 is silent offline by construction.** Its fact lives on GitHub, and `check-state.sh` runs
  before every commit, so it follows INV-26 and records nothing when the network or `gh` is
  unavailable. A clone that never reaches GitHub is outside its reach — the same shape, and the same
  accepted cost, as the local-default-branch reading in `## Goal`.

## Amendment 2 (2026-08-24) — the cross-repository failure posture is graded

**PURELY ADDITIVE. NOT YET RE-SIGNED.** This amendment adds one success criterion, `SC-15`. It
changes no existing requirement, no existing success criterion and no existing verification gap; every
word of `REQ-01`..`REQ-13` and `SC-01`..`SC-14` above stands exactly as signed. The `## Approval`
block below records the signature of Amendment 1 and is therefore **stale from the moment this
amendment lands** — it needs one re-signature covering `SC-15`, and nothing else.

**The gap, verified at source.** `SC-04` grades only the positive second-repository case: a `Done`
feature in a second repository under `WORKTREES_SEGMENT` producing an `INV-29` finding. `REQ-04`
requires that the refusal cover **every** repository "with no per-repository exception to remember or
later remove". What satisfies that clause is not the positive case alone but the posture the
enumeration takes when a declared repository cannot be read — and no criterion above grades any branch
of it. A repository silently skipped because its checkout could not be enumerated passes every
criterion in the signed brief. This is not hypothetical: `.harness/factory/fleet.yaml` declares
`mruangutai/harness-factory-smoke` and no checkout for it exists on this machine, so the
absent-checkout branch is live today.

**No new requirement.** `REQ-04`'s no-exception clause already commits the outcome; what was missing
was the criterion that can falsify it. Adding a requirement here would restate `REQ-04` in narrower
words and give the goal-check two homes for one commitment.

**It costs no new work.** The behaviour graded is the failure posture the approved plan already
specifies, and the fixture it is graded on — a `fleet.yaml`, a workspace root, and a real second git
repository with a landed `Done` feature and a real `git worktree add` — already exists in
`test-worktree-terminal.py` (`case_second_repo`). This makes evidence that will exist anyway into
graded evidence.

### Added success criterion

- SC-15: **The cross-repository failure posture, three branches, each asserted separately and never by
  a total record count.** Over the second-repository fixture in `test-worktree-terminal.py`, with the
  fleet declaring a readable repository alongside the two failure shapes, a single cross-repository
  enumeration call produces: **(a)** for a declared repository whose checkout directory does not
  exist, no record for it and no error — asserted on the absence of a record for that repository, not
  on how many records came back; **(b)** for a declared repository whose checkout directory exists but
  cannot be enumerated, exactly one repository-level `unresolved` record, its class and its path
  asserted as separate claims and its path being that checkout directory; **(c)** when `fleet.yaml`
  itself cannot be loaded, one `unresolved` record naming the fleet path **and** the harness
  checkout's own records still returned — two assertions, because a failure that is swallowed
  collapses the enumeration to the harness alone, which is the harness-only implementation `SC-04`
  says must fail. Each of the three is blocking where the posture says blocking: (b) and (c) are
  reportable records, (a) is silence. **Red proofs, each demonstrated failing before the
  implementation is wired in:** an implementation that emits nothing for both (a) and (b) passes (a)
  and fails (b); one that emits a record for both passes (b) and fails (a); one that catches the fleet
  load error and returns only the harness's records passes (a) and (b) and fails (c). A total-count
  assertion is satisfied by the wrong distribution of records and grades none of the three.
  verify: automated        evidence: integration


## Amendment 3 (2026-08-24) — the sweep's own location must never decide which copy it acts on

**Measured, not feared.** `post-merge-sweep.sh` used to build `feat_dir` from the same root it
locates its sibling scripts under. That root can BE a linked worktree carrying its own divergent,
never-landed copy of the same feature id — and `os.path.isdir(feat_dir)` then finds that copy and
proceeds. **No SKIP branch is ever reached**, so `gh-sync.py ship` reads and writes the wrong
`feature.json`. This is the FEAT-35 divergence already on record: the worktree read
`Review / pr: null` while `main` read `Done / pr: 812`.

It is reachable because `harness-init` writes a **relative** `core.hooksPath` (T-12), so every
worktree resolves to its own hooks directory and its own sweep.

**The fix is built and the test is written.** This amendment adds only the criterion that names
what that test proves. It commissions no engineering — `test-post-merge-sweep.py:665-687` already
carries the fixture and the red proof.

### Added success criterion

- SC-16: **The sweep's own on-disk location never decides which copy of a feature it acts on.** In a
  fixture where the sweep script runs from inside a **linked worktree** that carries its own
  divergent, never-landed copy of the same feature id as the main checkout, six clauses, each
  asserted separately and never by one substring match: **(a)** the sweep exits 0; **(b)** the root
  derived from the script's own location resolves to that linked worktree, which is what proves the
  fixture is the per-worktree-hooks scenario and not an accidental main-checkout run; **(c)** the
  root the feature directory is resolved under is the **main checkout**, asserted as an exact path
  both equal to the main checkout and unequal to the linked worktree, read from a resolved-path line
  the sweep prints unconditionally — **never from a skip**, because the wrong copy exists on disk
  and no skip branch is ever reached; **(d)** the landed copy's milestone is closed; **(e)** the
  divergent copy's own milestone is never touched, asserted on the absence of any call naming it;
  **(f)** the terminal worktree under the main checkout is removed, proving the correct copy was
  found rather than merely not written to. **Red proof:** an implementation that resolves the
  feature directory from the same root it locates its sibling scripts under passes (a), (b) and (f),
  closes the divergent milestone, and fails (c), (d) and (e) — and that failing state must be
  demonstrated, not asserted.
  verify: automated        evidence: integration


## Amendment 4 (2026-08-25) — the printed command must RUN, the squash clause was impossible, and SC-08 was never a UAT

**Three corrections the review panel forced, none of them optional.**

**One.** `REQ-02` had no criterion that could falsify it. Sixteen criteria graded `INV-29` and every
one was blind to a command that prints correctly and cannot be executed: `SC-01` asserts the command
against an exact-named fixture where both id derivations produce the same string, and `SC-05`'s
short-named case asserts the refusal FIRES without ever reading the command text. **Counting a line
is not reading it.** The defect shipped through all sixteen and was found by a human reading the
message. `SC-17` below is that gap closed, and its clause (c) runs the printed command.

**Two.** `SC-06`'s squash clause is amended above. It is struck as **unsatisfiable by any
implementation**, on a measurement, not marked unmet — `git merge --squash` fires the hook before
the ref moves and the completing commit never re-fires it. Recording it as a failure would blame the
sweep for git's behaviour.

**Three.** `SC-08` was mistakenly instructed to the validate phase as an operator-run UAT that must
stay `not_met`. **That instruction was wrong and the artifact says so:** `BRIEF.md:202-205` declares
it `verify: automated`, T-13 grades it through `test-hooks-install.py`, and `grep -i uat` over
`BRIEF.md` and `plan.yaml` returns two hits, both Verification-gaps entries, neither a criterion.
`pm` graded it MET on its own reading rather than obeying the instruction, and checked rather than
deferring. **SC-08 stands as automated and met.** The genuinely outstanding item is the
operator's-own-clone gap already recorded at `:217-221` and `:346-352`, which this brief
deliberately refuses to make a criterion because a fixture can fake it and that cannot.

### Added success criterion

- SC-17: **The printed removal command must actually run.** Over the same one fixture `SC-05`
  grades — four standing worktrees, including the **short-named** worktree whose landed directory on
  the default branch is full-named and `Done` — the `INV-29` line for THAT worktree is graded on its
  command text, three clauses each asserted separately and never by one substring match: **(a)** the
  line carries a `feature-worktree.py remove` command; **(b)** the command's `--id` value is composed
  from the found worktree's OWN directory basename, asserted as an exact string built from the
  fixture's worktree path and NOT from the landed directory name — the two differ in this fixture and
  are identical in every exact-named one, which is why this criterion names the short-named worktree
  specifically; **(c)** running the printed command verbatim exits 0 and that worktree is gone
  afterwards. **Red proof, demonstrated failing before the fix:** an implementation composing `--id`
  from the resolved landed feature id passes (a), passes every clause of `SC-01` and every clause of
  `SC-05`, and fails (b) and (c) — `feature-worktree.py remove`'s GATE 1 exits 3, "not a linked
  worktree". This is also `D-02`'s guarantee stated as a criterion: `post-merge-sweep.sh:150` already
  derives the id from the record's own path, and the gate must not disagree with the hook.
  verify: automated        evidence: integration

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-25
amendments-signed: Amendment 1, Amendment 2, Amendment 3, Amendment 4
note: RE-SIGNED TWICE on 2026-08-24. The original signature of 2026-08-23 covered the
  brief without either amendment. The second signature covers Amendment 1 in full —
  REQ-11/12/13 and SC-11/12/13/14. The third covers Amendment 2 — SC-15, the
  cross-repository failure posture, added because SC-04 graded only the positive
  second-repository case while REQ-04 requires no per-repository exception, so a
  repository silently skipped passed every criterion in the brief. The date moves rather
  than being kept alongside the old ones, so a reader never has to work out which date
  governs which paragraph. The fourth signature covers Amendment 3 - SC-16, the criterion
  naming what the already-built linked-worktree test proves. It commissions no work.
  The fifth signature covers Amendment 4 - SC-17, SC-06's struck squash clause, and the
  correction that SC-08 was never a UAT. SC-17 DOES commission work: its clause (c) runs
  the printed command, which no existing test did.
