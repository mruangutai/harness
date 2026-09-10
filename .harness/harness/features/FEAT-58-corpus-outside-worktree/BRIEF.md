# BRIEF — FEAT-58-corpus-outside-worktree

Feature id **ratified**, not coined (DEC-133: it is already the worktree and branch name). Source
ticket: issue #1559.

**Goal of record for this run:** `.harness/notes/dod-worktree-corpus-2026-09-10.md` — the operator's
definition of done, iterated in dialog. It supersedes the 11 REQ / 15 SC this file previously
carried and the grilling artifact of 2026-09-09 except for that artifact's Facts section. Every REQ
and SC below traces to a line of that note; nothing was carried forward for reading reasonably.

**Superseded and deliberately gone** (restored only if re-derivation forces it, on stated evidence):
the in-place migration/convergence of standing worktrees — the note records only three live
worktrees remain and the irreversible task has no subject left (note:172-179); the corpus-root
anchor concept and provider/ref frame declarations — the audit never needed the corpus (note:44-57),
so there is nothing to anchor; the fifteen-reader ledger — the reader set collapses to one active
feature; the incremental sweep cache — explicitly dropped by the operator (note:56-57); APFS
clonefile/reflink as the mechanism — see Non-goals; every byte-count criterion — a byte bound is
satisfiable by clonefile, the mechanism the rule excludes (note:299-303).

## Problem

A git worktree checks out the whole tree, so isolating one feature's code replicates the entire
state store with it. Measured on this host: 362 MB across 6 worktrees after the operator's
2026-09-10 cleanup, of which **168 MB (46%) is replicated corpus** — the largest remaining
component and the only one that grows: corpus bytes in `main` went 0.2 MB (2026-08-01) → 29.8 MB
(2026-09-09), ≈ +1.1 MB/day, multiplied by every standing worktree (note:181-192). Cleanup wins
once; the replication compounds.

The second half of the problem is what happens when the copy is removed carelessly. Two measured
failures, and they are why the mechanism requirements exist:

- In a cone-mode sparse probe at `abff2a84`, `check-state.sh` swept **1 of 88** features and
  **exited 0**. A partial view reports clean.
- Merging a change into a sparse worktree wiped the skip-worktree marks: `git status --porcelain`
  returned **3337 lines, all `" D"`**, and `git ls-files -t` returned **3807 H, 0 S** — git believed
  the whole corpus was deleted, and `git commit -a` in that state would land that deletion on the
  default branch (note:87-98, measured 2026-09-10 on this host's real corpus).

## Goal

A worktree materialises exactly one feature directory — its own — while every other feature stays
readable on disk with ordinary tools from inside that worktree; the audit stops sweeping the corpus
and refuses rather than reporting clean when it cannot reach what it expects; no two features claim
the same branch; a fresh clone and CI behave exactly as today. That state is established and
repaired by one deterministic command, not by prose an agent is expected to follow, and that command
fires however a worktree is created, merged or rebased.

## Requirements

- REQ-01 (D-1 DoD): Creating a feature worktree materialises exactly one feature directory — its
  own — and every path the worktree needs to function still exists on disk.
- REQ-02 (D-2 DoD): From inside such a worktree, every other feature's record is readable on disk
  with ordinary tools, at a path identical in every worktree, with byte-identical content and no
  materialised copy. "Available" never means "recoverable from git history".
- REQ-03 (D-3 DoD): The audit covers the active feature only, reads no other feature's directory,
  and REFUSES non-zero — naming its counts — rather than reporting clean when it cannot reach what
  it expects.
- REQ-04 (D-4 DoD): No two feature records claim the same branch. The literal string `none` is not
  a branch claim, and neither is an absent or empty value.
- REQ-05 (D-5 DoD): A checkout that is not a linked worktree — a fresh clone, a CI runner —
  behaves exactly as it does today: full corpus materialised, audit unchanged, no refusals, no new
  failure in the existing suite.
- REQ-06 (M-1 DoD): One idempotent command establishes and repairs the state a worktree must hold,
  and fails with a named reason per broken input. `--verify` reports and never repairs.
- REQ-07 (M-2 DoD): That command runs automatically from `post-checkout`, `post-merge` and
  `post-rewrite`, so the state holds whoever creates, merges or rebases the worktree — including an
  agent running bare `git worktree add` — and a hook-fired failure never breaks the git operation
  it rides on.
- REQ-08 (forced by the D-2 (DoD) rulings, note:40-42): The corpus read path never appears as a
  change in `git status`, and a governed write *through* it is refused by the guard rather than
  being read-only by convention.
- REQ-09 (forced by the D-4 (DoD) ruling, note:73-80): Before the uniqueness check ships, the live
  collision — `feat/harness-native-foundation`, claimed by both `FEAT-02` and
  `FEAT-03-subissue-mirror` — is corrected or explicitly era-exempted with the reason recorded, so
  the check's first run over real records reports no violation. Both features are terminal, so no
  branch value may be invented.
- REQ-10 (forced by the strong form of "nothing lost", note:143-147, 305-308): Over this feature's
  own commit range, no feature directory other than its own is altered. Not "citations resolve" —
  nothing was changed.

**Namespace note, and it is load-bearing for every reference below:** the DoD note's seven binding
items are spelled `D-1 … D-5`, `M-1`, `M-2` and are always qualified `(DoD)` here. `plan.yaml`'s
architectural decisions are spelled `D-01 … D-11`. They are two namespaces and a bare `D-3` would
read as either.

## Coverage — every binding item to its own REQ and SC

| Item | What | REQ | SC |
|---|---|---|---|
| **D-1 (DoD)** | Exactly one feature directory materialised | REQ-01 | SC-01 |
| **D-2 (DoD)** | Every other feature readable on disk | REQ-02 | SC-02 |
| **D-3 (DoD)** | Audit: active feature only, no corpus, refuses | REQ-03 | SC-04, SC-05, SC-06 |
| **D-4 (DoD)** | No two features claim one branch | REQ-04 | SC-07 |
| **D-5 (DoD)** | Fresh clone and CI unchanged | REQ-05 | SC-12 |
| **M-1 (DoD)** | One idempotent `--verify`/`--repair`, verify never repairs, and a named gate calls `--verify` | REQ-06 | SC-09, SC-10 |
| **M-2 (DoD)** | It runs from `post-checkout`, `post-merge`, `post-rewrite` | REQ-07 | SC-11 |
| — | Corpus path gitignored; writes through it refused | REQ-08 | SC-02, SC-03 |
| — | The live FEAT-02 / FEAT-03 collision, on real data | REQ-09 | SC-08 |
| — | Nothing altered outside the active feature | REQ-10 | SC-13 |

Thirteen criteria, not twenty-two. **A criterion states an observable outcome a consumer can check;
a line describing how a test is BUILT is not one** — positive controls, instrumentation, manifest
comparisons, perturbation preconditions and red proofs are all still mandatory, and they live in
the `verify:` and intent of the task that owns them (`plan.yaml` tasks N-01 … N-09). Nothing was
dropped as coverage: the assertion ledger in `runs/consolidate-eng/digest.md` maps every one of
them to a landing place, and `notes/research-FEAT-58-apply-consolidation.md` records the map.

**Thirteen rather than twelve**, and this is the one place the count moved: SC-12 and SC-13 were a
single criterion carrying two failure modes that break alone — a new failure in an existing suite,
and an edit to a feature directory other than this one. A distinct failure mode earns its own
criterion, and consolidating there would have dropped an assertion rather than removed padding.

**On `traces:`** — this plan's tasks carry SC ids alongside REQ ids in `traces:`, deliberately: the
goal-check reads it to find which task grades which criterion, and no other field carries that
edge. Read a `traces:` list as REQ ids plus the criteria the task grades.

## Verification discipline — binding on every criterion below

- **Measurement modes, and no others** (note:327-333): materialisation `ls .harness/*/features |
  wc -l`; read surface `find <dir> -type f | wc -l`; cleanliness `git status --porcelain | wc -l`.
  **No criterion is gated on a byte figure, a `du` value or a worktree size** — `du` reports logical
  size and a real-block bound is satisfiable by APFS clonefile.
- **The fixture is a synthetic repository** — a real `git init`, a handful of fake feature
  directories — **never a copy of this repository.** Precedent #1526: a fixture that copied
  `.claude/worktrees` accounted for 239 s of a 240 s suite.
- **Exit 0 is never evidence.** `git sparse-checkout set` exits 0 both with no arguments and with
  patterns matching nothing, and the present audit fail-open exits 0 having swept 1 of 88. Every
  criterion asserts a named observable — a path that exists, a finding set, a count — not a status.

## Success Criteria

- SC-01: A worktree materialises exactly one feature directory — its own — and every path it needs
  to function still exists inside it. `ls <worktree>/.harness/*/features | wc -l` returns `1` and
  the single entry is the active feature id; the required paths are present on disk, per path,
  including the dispatch-critical skills path under **both** the tracked `.claude/skills` spelling
  and the `.agents/skills` symlink every dispatch resolves through, **and each non-features
  `.harness` subtree the worktree needs — `.harness/factory/`, `.harness/expertise/` and the
  NESTED `.harness/<repo>/docs/` — asserted individually, never as one aggregate clause**; a
  non-active feature's directory is absent. It holds by the harness creation path and by a bare
  `git worktree add` alike, and the failing state — the full feature count materialised — is
  demonstrated first.
  verify: automated      evidence: integration
- SC-02: From inside the worktree, every other feature's record is readable on disk with ordinary
  file tools at the same path in every worktree, byte-identical to the owner root's copy, and the
  read costs no materialised feature file and no `git status` dirt:
  `find <worktree>/.harness/*/features -type f` returns only paths under the active id, and
  `git status --porcelain | wc -l` returns `0`.
  verify: automated      evidence: integration
- SC-03: A governed write **through** the corpus path is REFUSED, non-zero, on both registered
  guard entrypoints — the Write/Edit route and the Bash route — while a write to the active
  feature's own directory through those same entrypoints still SUCCEEDS.
  verify: automated      evidence: integration
- SC-04: The audit's finding set for feature `X` in a sparse worktree is IDENTICAL, as a set, to
  the set it produces for `X` in a full checkout. **Exit status is excluded from the comparison** —
  the present fail-open already exits 0, measured sweeping **1 of 88** in a cone-mode sparse probe
  at `abff2a84`.
  verify: automated      evidence: integration
- SC-05: The audit opens no path under another feature's directory.
  verify: automated      evidence: integration
- SC-06: When the audit cannot reach what it expects, it REFUSES — a non-zero exit whose message
  carries the counts in the form `N of M` and this repository's remedy tail — rather than reporting
  clean.
  verify: automated      evidence: integration
- SC-07: No two feature records claim one branch, and the merge gate acts on it: a duplicated head
  branch is DENIED with both feature ids named, the same merge is ALLOWED once one record is
  corrected, and both hold with the gate running from **inside** a sparse worktree. The literal
  `none`, an absent value and an empty value are not claims and produce no finding.
  verify: automated      evidence: integration
- SC-08: The shipped check reports zero branch-collision findings over the repository's own feature
  records, read at the reviewed commit — the live `FEAT-02` / `FEAT-03-subissue-mirror` pair having
  been corrected or era-exempted with a non-empty reason whose emptying reddens the check.
  verify: automated      evidence: integration
- SC-09: One command establishes and repairs the state a worktree must hold. `--verify` fails per
  broken input with **six distinct non-zero exits, each naming its own reason and its own remedy** —
  wrong cone; skip-bits cleared; corpus path absent; corpus path pointing elsewhere; more than one
  feature directory materialised; dirty tree, whose remedy is by hand and never `--repair`.
  `--repair` is idempotent, announces each repair it actually made and is silent only on a true
  no-op. **And a named gate calls it:** `check-state.sh`'s preflight invokes `--verify` — asserted
  by the invocation it records, never by exit 0 — and a failing `--verify` makes that gate REFUSE
  non-zero before a single invariant runs, leaving the tree unrepaired (D-12).
  verify: automated      evidence: integration
- SC-10: `--verify` never repairs: against a broken tree it exits non-zero and the tree is
  **byte-for-byte unchanged** afterwards, and its message claims no repair it did not make.
  verify: automated      evidence: integration
- SC-11: The state survives a merge, a rebase and a bare creation because the shims fire — after a
  merge touching a hidden feature's file the tree is clean and the skip-bits intact, after a rebase
  the skip-bit set equals the pre-rebase set — and a hook-fired failure is legibly attributed
  without failing the git operation it rides on: the git command still exits 0, the attributed line
  names the shim and its delegate, and the tree is visibly still broken rather than silently fixed.
  **The merge case must FAIL today**; the pre-change shape is reproduced in the same file. Host
  baseline, measured 2026-09-10 on the real corpus and NOT a fixture expectation: **3337 paths
  reported deleted, 3807 skip-bits cleared, 0 remaining.**
  verify: automated      evidence: integration
- SC-12: Nothing outside the target moved. A checkout that is NOT a linked worktree behaves exactly
  as today — full corpus materialised, audit finding set and exit status equal to pre-change,
  `--verify` a no-op, the three shims inert; and the existing suites gain no failure, the
  failing-test SET equalling the baseline recorded at its own sha under the identical command
  lines. Graded at the reviewed commit, resolved from `HARNESS_REVIEW_SHA` defaulting to `HEAD`.
  verify: automated      evidence: integration
- SC-13: Over this feature's own pinned commit range, no feature directory other than its own is
  altered — the strong form of "nothing lost", byte-identity and not citation resolvability:
  `git diff --name-only "$(git merge-base origin/main HEAD)..HEAD" -- .harness/harness/features`
  names no path outside `FEAT-58-corpus-outside-worktree/`, with BOTH the stdout and the exit
  status asserted — `git diff` exits 0 whatever it prints, so a status check alone asserts nothing
  and an output check alone cannot tell an empty result from a failed invocation. Graded at the
  reviewed commit, resolved from `HARNESS_REVIEW_SHA` defaulting to `HEAD`. If the operator picks
  D-06 Arm A, that signature also signs one named pathspec exclusion, for
  `.harness/harness/features/FEAT-03-subissue-mirror/feature.json` and nothing else.
  verify: automated      evidence: integration

## Verification gaps

- `component`, `ui` and `typecheck` carry `cmd: null` (`unresolved`); `functional` and `eval` are
  `excluded` (DEC-187). No criterion above rests on any of them. `unit` and `integration` are the
  only live runners, and assertions must live under `tests/unit/**` or `tests/integration/**` —
  the directory selects the kind (DEC-213). Several criteria are proven by unit assertions as well
  as integration ones — SC-07's `none`/absent/empty cases, SC-09's message contract, SC-11's static
  shim checks — and each declares `integration` because its **decisive** clause needs a real
  worktree, a real merge or a real rebase.
- **No runner reproduces the host-scale merge defect.** SC-11's merge clause is proven at fixture
  scale; the 3337/3807 figures are a one-shot host measurement recorded in the DoD note, not a
  fixture assertion. What is therefore NOT proven automatically: that the real 3337-path corpus
  survives a merge. What carries it: the same command run once by hand on this host after the
  change, recorded under a `HOST-SCALE RESIDUAL` heading in N-04's receipt.
- **SC-13's nothing-altered clause has no fixture.** It grades this feature's own commit range,
  which no synthetic repository can hold, so its assertion runs `git` against the real repository
  at the reviewed commit rather than against a fixture. That is a scope limit on the fixture, not
  a downgrade of the method: the clause is still an integration assertion and still fails loudly.

## Non-goals

- **APFS clonefile / reflink worktree creation as the mechanism.** Measured and real (124× fewer
  real blocks), and excluded: it makes the copy cheap instead of removing it. File count, audit
  sweep surface, agent read surface and the O(features × worktrees) growth term are all untouched.
  Reopening it as the mechanism requires the operator to revise the rule.
- **Moving the state store out of git, archiving, pruning or lossily rewriting any record.** Only
  the READ path is in scope; the record stays git-tracked at its existing paths (issue #1559 q3).
- **Converging the standing worktrees as a task.** Three of six remaining are live; they either
  convert on their next checkout, merge or rebase by REQ-07's own mechanism, or they age out. The
  one irreversible task in the halted plan has no subject left (note:172-179).
- **Worktree and branch housekeeping.** Already executed by the operator on 2026-09-10 (23 of 30
  worktrees removed, 62 of 100 branches pruned, 1192 MB → 362 MB) and out of the feature.
- **Reducing the number of standing worktrees.** The DoD is about what a worktree costs, not how
  many exist. Removing a worktree is additionally not an agent's act.
- **Not this feature, by operator instruction:** the six filed harness defects (#1595, #1596, #1597,
  #1598, #1630, #1631); `FEAT-53`'s 138 MB of untracked run dirs (a retention defect, not
  replication); `597-omp-behavior-baseline`'s unlanded work.

## Constraints

- **The DoD note BLOCKS:** `.harness/notes/dod-worktree-corpus-2026-09-10.md` is the floor. All
  seven binding items must be covered; none may be folded into another or deferred.
- **DEC-174 BLOCKS DISPATCH:** the hooks, gate scripts and validators being changed ARE the
  enforcement path, so each such change is made **directly by the main session**, never through a
  team run whose gates are the artifact being changed. `.claude/commands/**` is `main-session-direct`.
  `check-plan-routes.py` exiting 0 with informational DEVIATION lines is the carve-out working.
- **DEC-133 BLOCKS** renaming: the feature id is immutable.
- **DEC-95 SUPPLIES:** `.harness/` is per-worktree state — which justifies the live feature's
  directory and says nothing about the others.
- **DEC-193 SUPPLIES the bound:** exactly two locations hold code under harness authority —
  `WORKTREES_SEGMENT`-rooted checkouts and `workspace_root/<repo>`.
- **DEC-208 / DEC-218 SUPPLY:** feature writes already bind to the registered worktree; REQ-08 makes
  that binding reach a write attempted through the corpus path rather than trusting convention.
- **DEC-163 BLOCKS** resting an `automated` criterion on a null runner; see Verification gaps.
- **DEC-213 BLOCKS** test placement: `tests/unit/**` and `tests/integration/**`.
- **The host already supplies the mechanism:** `core.hooksPath` is `.claude/skills/harness/hooks`,
  tracked so it travels with a clone; `post-merge` is already a shim delegating to
  `bin/post-merge-sweep.sh` (FEAT-34 T-11, D-08) so a test can reach it. `bash-write-guard.sh:512`
  already refuses `git worktree add` outside the sanctioned location.
- **Shared file:** `.claude/skills/harness/bin/check-state.sh` is also touched by FEAT-57's T-19.
  Serialise the edits.
- **Naming:** `.agents` is a symlink to `.claude`; the repo-tracked surface is spelled
  `.claude/skills/...`, and `git show` of an `.agents/` path prints nothing.

## Approval

status: pending
