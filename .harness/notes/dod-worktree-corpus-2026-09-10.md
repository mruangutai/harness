# Definition of done — the feature corpus must not be replicated into a worktree — 2026-09-10

Operator-authored, iterated in dialog. Supersedes the 15 success criteria in
`FEAT-58-corpus-outside-worktree/BRIEF.md`, which was halted mid-plan at 8 of 10 cycles because it
was shaped around a problem statement this note replaces. Source ticket: issue #1559.

This is the operator's definition of done at a limited level — the floor, not an exhaustive list.
pm still owns REQ-NN and SC-NN and their `verify:` methods.

## The five things done means

1. **Prior worktrees are not cloned into the active planning or building worktree.** A worktree
   materialises exactly one feature directory — its own.
2. **Prior features remain available to the active worktree on disk**, for any agent on the team
   that needs to look back at a prior `FEAT-NN` or `BUG-NN`. Available means present at a path an
   agent can read with ordinary tools — NOT "recoverable from git history".
3. **Only the active feature is audited.** No sweep over the corpus.
4. **Two features cannot claim the same branch.**
5. **A fresh clone and CI behave exactly as today**, and in particular do not replicate prior
   worktrees either.

## Rulings taken in dialog, with the evidence behind them

### On (2) — the corpus does NOT move, the copies stop

The operator's ruling, explicitly: the corpus is not deleted from disk and git is not to become
its only record. Artifacts from prior features MUST be available on disk to any agent on the team.

The mechanism that satisfies this without moving the directory: **one real directory at the owner
root, reached from each worktree through a symlink at a stable path.**

    ln -s <owner-root>/.harness/harness/features  .harness/corpus
    → 89 features readable from inside the worktree, 0 bytes added

Measured. Agents read `.harness/corpus/FEAT-10-software-factory/…` with ordinary tools; the path is
identical in every worktree, so there is no new anchor concept and no prose for an agent to
remember. The active feature's own directory stays a real, tracked, writable directory in its
worktree.

Two conditions: the symlink must be gitignored (git reports `?? .harness/corpus` without it), and
the write guard must refuse writes *through* it — a symlink is read-only by convention, not by
enforcement.

### On (3) — the audit never needed the corpus

Every per-feature invariant reaches its verdict from one feature's own record: INV-17's handoff
notes, INV-23's budget-versus-`STATE.md`, `check-plan-routes` over `plan.yaml`,
`validate-feature-json`'s schema pass, board station versus `feature.json`. None consults a second
feature. The 88-wide sweep was a convenient glob, never a requirement. The corpus's value is at
**planning** time — precedent and prior decisions — which is a read, not an audit.

Measured cost of the sweep that was never earning anything: 89 feature directories, 60 with no
commit in over 7 days, 454 of `check-state.py`'s 1181 finding lines naming one of those 60 — all
re-derived every run about records nothing writes.

An earlier idea of mine — an incremental sweep with a content+checker-version cache key — is
**dropped**. It optimised work that should not happen at all.

### On (4) — git already enforces half of it

    $ git worktree add /tmp/dup-probe feat/FEAT-57-review-latency
    fatal: 'feat/FEAT-57-review-latency' is already used by worktree at
           .claude/worktrees/harness/FEAT-57-review-latency

One branch, one worktree is free. The half that needs building is at the **record** level: two
`feature.json` files can name the same branch and git cannot see it. That case is live —
`feat/harness-native-foundation` is claimed by both `FEAT-02` and `FEAT-03-subissue-mirror`.

The structure needed is a **uniqueness index**, not a corpus walk: one row per feature carrying
id, branch and issue numbers. Measured at **79 rows, 5848 bytes**. `merge-gate.py`'s
`feature_for(branch)` is its consumer.

Two conditions, both from present data:
- The check goes red on day one against `FEAT-02` / `FEAT-03`. Either correct those two records or
  era-exempt the pair explicitly, with the reason recorded. A new gate whose first run reports a
  violation is a gate the team learns to step over.
- The literal string `none` is not a branch claim. Four records carry it (`FEAT-01`,
  `FEAT-15-domain-product-base`, `FEAT-19-central-product-config`, `FEAT-28-ci-wiring-asserted`).
  Treat it as a claim and the check reports four collisions that do not exist. A test must pin
  that those four produce no finding while `FEAT-02`/`FEAT-03` produce exactly one.

## The mechanism requirement — deterministic command, never prose

Operator ruling: the state a worktree must hold is established and repaired by a **standard
deterministic command**, not by instructions an agent is expected to follow.

**Why this is not optional — measured.** Merging a change to a hidden feature's note into a sparse
worktree succeeded and left the content correct, but:

    git status --porcelain  →  3337 lines, all " D"      every hidden file reported DELETED
    git ls-files -t         →  3807 H, 0 S               every skip-bit cleared

The merge wiped the skip-worktree marks, so git believed the whole corpus had been deleted. The
harness halts on a dirty tree, and `git commit -a` in that state would land the corpus deletion on
the default branch. The repair is one command:

    git sparse-checkout reapply  →  dirty 0, 3337 skip-bits restored

**The host already exists and is tested.** `core.hooksPath` is `.claude/skills/harness/hooks`,
and the hook SCRIPTS are tracked in the repository.

**CORRECTED 2026-09-10, operator error.** This sentence originally read "tracked in the repository
so it travels with a clone". That conflated the tracked hook scripts with the `core.hooksPath`
config pointing at them, which is LOCAL git config and is NOT cloned — measured:
`git ls-files | grep -c gitconfig` returns 0. The mechanism does travel, but by two other means, and
they should be cited rather than assumed: `harness-init/SKILL.md:81` sets `core.hooksPath` as an
onboarding step, and `check-state.py:2607` is INV-31, which REFUSES a clone whose `core.hooksPath`
is wrong ("no harness hook runs on this clone"). A fresh clone missing the config is therefore a
named and gated state, not a silent hole. `post-merge` there is a deliberate shim whose
body lives in `bin/post-merge-sweep.py` so a test can reach it (FEAT-34 T-11, D-08), and that sweep
already walks every linked worktree — its `SKIP … not under WORKTREES_SEGMENT` lines appeared in
the probe above.

So one idempotent command covers both the symlink and the skip-bits:

    worktree-state.py --verify | --repair      exit non-zero with a named reason
      1. cone matches the derived include list plus exactly this worktree's feature
      2. git sparse-checkout reapply
      3. .harness/corpus resolves to <owner-root>/.harness/harness/features
      4. exactly one feature directory materialised
      5. working tree clean

Invoked at worktree creation and from hook shims beside the existing one: `post-merge`,
`post-checkout`, and `post-rewrite` for rebase.

**`--verify` is what gates call, and it FAILS rather than repairing.** Repair is an explicit act. A
gate that quietly fixes state hides the fact that something broke it.

## Settled since the first draft — nothing is open

### The rule holds regardless of who creates the worktree

Ruled: it holds always. Not by trusting agents — measured, `post-checkout` fires on worktree
creation with cwd already inside the new tree:

    $ git worktree add --detach /tmp/hookwt main
    POST-CHECKOUT FIRED: cwd=/private/tmp/hookwt args=000000… 805e772f… 1

So the same idempotent command runs however a worktree is made, and there is no harness-route
versus manual-route distinction to design around. This matters because agents legitimately DO run
bare `git worktree add` — `harness-verification-rules` instructs QA to run perturbation proofs in a
disposable worktree by exactly that route — so a rule depending on agent compliance would be
violated by design.

**CORRECTED 2026-09-10, operator error.** This paragraph originally ended "A QA probe worktree now
gets stripped automatically without QA knowing." That was wrong, and wrong in the direction that
matters: it claimed coverage the design does not deliver. The scope guard keys on the feature-id
form, so a `qa-*` probe tree is left alone — and that is CORRECT, not a gap. A perturbation proof
runs against the tree as it really is; stripping a probe would make it measure something other than
the thing being probed. A disposable probe carries a faithful full checkout. What survives from the
claim is the part that was never about QA: the hook fires whoever creates the worktree, so the
mechanism does not depend on anyone remembering a rule.

A creation door already exists and stays: `bash-write-guard.py:512` refuses `git worktree add`
outside the sanctioned location, and refuses a destination it cannot parse rather than permitting
it. That guard was added because both hooks were measured exiting 0 on
`git worktree add --detach ~/GitHub/harness-SIBLING HEAD` at a29ad06. Trust is not the mechanism;
the hook and the door are.

### "Nothing lost" takes the STRONG form

Ruled: byte-identity, not citation resolvability. Sparse checkout never modifies content — it only
stops writing files to disk — so proving nothing was altered costs one `git diff` over the
feature's own commit range, asserting no edit to any feature directory other than its own. The
weak form only proves things can be found, not that they are unaltered, and it is not cheaper.

### The dead checkouts — DONE, and out of scope

Executed by the operator's main session on 2026-09-10, before any plan: **23 of 30 worktrees
removed, 62 of 100 local branches pruned, `.claude/worktrees` 1192 MB → 362 MB.** Every removal
retained its branch, so each is one `feature-worktree.py create` away from returning.

Composition: 13 with a merged PR and the branch in `main`; 6 merged with no PR (five `qa-*` probes
plus `BUG-1154`); 4 dead but clean, having never written a line of code (`FEAT-04`, `FEAT-05`,
`FEAT-32`, `gh-sync-abandoned-tasks`). Nothing was deleted on the strength of `git branch --merged`
alone — the 7 branches `-d` refused were each verified with
`git merge-base --is-ancestor <branch> main` before forcing.

Two traps found and avoided, worth keeping because they will recur: **a merged PR does not mean
landed work** — squash-merge leaves the branch tip a non-ancestor of `main`, and `597-omp-behavior-
baseline` (PR #809 MERGED) still holds 178 files / +3195 insertions unlanded, `gh-sync-abandoned-
tasks` (PR #1190 MERGED) 2 files / +46. And **`FEAT-53` is not dead** despite 7 days idle and zero
code delta: it holds 27 uncommitted files of live prototype work.

This is housekeeping and stays out of the feature. It does touch issue #1559's constraint that no
standing worktree is removed to achieve the DoD — that guard exists to stop the effort faking its
own measurement, which is a different act from cleaning up landed checkouts, and the operator
loosened it deliberately.

### Converging existing worktrees — no longer a task

Six worktrees remain and only three are genuinely live (`FEAT-57`, `FEAT-58`, `BUG-285`). The
halted plan's SC-06 — converge ~30 checkouts in place, graded by inspecting a note the team wrote
about its own work — has no subject left. Either the remaining few are converted by the same
idempotent command on their next checkout or merge, or they age out. **The one irreversible task in
the feature is gone**, and with it the high panel finding PF-5945852660e0bd21e2b5aabb8cd48383 that
withheld the plan.

### Where the footprint stands after cleanup

    362 MB across 6 worktrees
    168 MB replicated corpus (46%)      <- this feature's target
    138 MB FEAT-53's untracked run dirs <- a RETENTION defect, not replication; not this feature
     56 MB code, docs, tests

The corpus share is the largest remaining component and, unlike the other two, it GROWS: corpus
bytes in `main` went 0.2 MB (2026-08-01) → 8.5 → 19.3 → 29.8 MB (2026-09-09), about +1.1 MB/day,
multiplied by every standing worktree. Cleanup wins once; this feature stops the compounding. An
earlier claim of mine that the corpus was "no longer the biggest thing on the disk" was a
pre-cleanup number carried into a post-cleanup total, and is withdrawn.

## BINDING ON PLANNING — the seven that must each carry a REQ and an SC

Operator ruling: the plan MUST cover all seven, each traced to its own REQ and at least one SC.
None may be folded into another, deferred to a follow-up, or graded by inspection where a runner
can grade it. A plan returning with fewer than seven covered is incomplete on its face.

| | What | Kind |
|---|---|---|
| **D-1** | A worktree materialises exactly one feature directory — its own | behaviour |
| **D-2** | Every other feature is readable on disk from inside that worktree | behaviour |
| **D-3** | The audit covers the active feature only, reads no corpus, and REFUSES rather than reporting clean when it cannot reach what it expects | behaviour + failure mode |
| **D-4** | No two features claim the same branch | invariant |
| **D-5** | A fresh clone and CI behave exactly as today | non-regression |
| **M-1** | One idempotent `--verify` / `--repair` command, `--verify` never repairing | mechanism |
| **M-2** | That command runs from `post-checkout`, `post-merge` and `post-rewrite`, so it fires whoever creates or merges the worktree | mechanism |

M-1 and M-2 are not implementation detail behind D-1..D-3. They are the reason D-1..D-3 survive
contact with a merge, a rebase, and an agent running bare `git worktree add`. They get their own
REQs.

## How each is PROVEN — the test matrix

### The fixture, first, because it decides whether this suite is usable

A **synthetic repository** — a real `git init`, five fake feature directories, a handful of tracked
files — never a copy of this repository. Issue #1526 is the precedent: a fixture that copied
`.claude/worktrees` accounted for 239 s of a 240 s suite. Every test below runs against the
synthetic fixture; the real host is measured once, by hand, and recorded.

### D-1 — one feature per worktree

- **Integration, positive:** create a worktree through the creation path for feature `X`; assert
  `ls .harness/*/features` is exactly `[X]`.
- **Positive control, and this one is mandatory:** `git sparse-checkout set` **exits 0 both with no
  arguments and with patterns matching nothing**, so a success exit proves nothing. The test must
  assert that named required paths EXIST on disk afterwards — including `.agents/skills`, which the
  original probe's hand-written include list omitted and every dispatch resolves through.
- **Derivation, not a literal list:** add a new top-level directory to the fixture, create a new
  worktree, assert it appears without any source edit. A literal include list fails this.

### D-2 — the corpus is readable on disk

- **Integration:** from inside the worktree, read another feature's `BRIEF.md` through
  `.harness/corpus/<other>/BRIEF.md`; assert the bytes equal the root's copy.
- **Cost:** assert the read costs no materialised bytes, and that `git status --porcelain` is empty
  — which fails if the symlink is not gitignored.
- **Negative, the one that matters:** a governed write THROUGH the symlink is REFUSED. Invoke the
  guard the way the hook does, not by calling a helper. A symlink is read-only by convention until
  a test proves the guard says otherwise.

### D-3 — audit scope and its failure mode

- **Equivalence, not "exit 0":** the finding set the audit produces for feature `X` in a sparse
  worktree is IDENTICAL to the set it produces for `X` in a full checkout. Exit 0 is what the
  present fail-open already returns; equality of findings is the real claim.
- **No corpus reach:** assert the audit opens no path under another feature's directory. Instrument
  it — a call-count or an opened-path assertion — rather than inferring it from output.
- **Mutation, fail-closed:** break what the audit expects to reach and assert a **non-zero exit
  whose message carries the counts**. The measured pre-change behaviour is the baseline this must
  contradict: `check-state.py` in a sparse worktree swept **1 of 88** and **exited 0**. A test that
  cannot distinguish those two states is not testing anything.

### D-4 — branch uniqueness

- **Unit, three cases:** two records naming one branch → exactly one finding, naming both features;
  four records carrying the literal `none` → zero findings; absent or empty branch → zero findings.
  The `none` case is not padding — treating it as a claim yields four false collisions, and a gate
  that cries wolf gets muted along with its one true finding.
- **Integration:** `merge-gate.py` DENIES a merge whose head branch is claimed by two features, and
  ALLOWS the same merge once the duplicate is corrected.
- **Real-data act, separate from the suite:** `FEAT-02` / `FEAT-03-subissue-mirror` are corrected or
  explicitly era-exempted BEFORE the check ships, with the reason recorded. Both are terminal, so
  no branch value may be invented.

### D-5 — fresh clone and CI unchanged

- **Integration:** in a fixture checkout that is not a linked worktree, assert the corpus is fully
  materialised, the audit behaves as pre-change, and `--verify` succeeds as a no-op.
- **The strongest evidence is negative:** the existing suite, run in a plain clone, must be
  untouched by this change. A single new failure there is a D-5 violation.

### M-1 — the command

- **Six broken inputs, six distinct non-zero exits, each naming its own reason:** wrong cone;
  skip-bits cleared; symlink absent; symlink pointing elsewhere; more than one feature directory
  materialised; dirty tree.
- **`--verify` MUST NOT repair.** Run `--verify` against a broken tree, assert it fails AND that the
  tree is byte-for-byte unchanged afterwards. This is the test that stops a gate from quietly
  fixing what it is supposed to report.
- **Idempotence:** `--repair` twice; the second run changes nothing and still exits 0.

### M-2 — the hooks

- **The reproduction, as a regression test — this one fails today and is the centrepiece:** create a
  sparse worktree, merge a commit touching a hidden feature's file, assert `git status --porcelain`
  is EMPTY and the skip-bits are intact. Pre-change measurement: **3337 paths reported deleted,
  3807 skip-bits cleared, 0 remaining.**
- **Bare creation:** `git worktree add` directly, no harness path; assert the result is sparse
  because `post-checkout` fired. Measured: it fires with cwd already inside the new tree.
- **Rebase:** `post-rewrite` restores state after a rebase in a sparse worktree.
- **Shim integrity:** each hook shim's delegated path resolves and is executable — the existing
  FEAT-34 D-08 / SC-14 pattern, extended, so a shim pointing at a missing file cannot pass.

### What must NOT be written

No test asserting a byte figure, a `du` value, or a worktree size. `du` reports logical size and
would pass a wrong implementation while failing a correct one, and any real-block bound is
satisfiable by APFS clonefile — the mechanism this rule excludes. Materialisation is graded by
`ls .harness/*/features | wc -l`, the read surface by `find -type f | wc -l`, cleanliness by
`git status --porcelain | wc -l`.

### Nothing lost — the whole-feature check, run once at the end

One `git diff` over this feature's own commit range asserting no edit to any feature directory other
than its own. Strong form: not "the citations resolve", but "nothing was altered".

## Carried forward from the halted plan — evidence, not decisions

- Three live defects it surfaced, all independent of this DoD: `merge-gate.py:169`
  (`if not owners: return`) silently ALLOWS a merge it cannot resolve; `branch-create-gate.py`
  would deny branch creation for every non-materialised flow post-convergence, with a false
  message; `check-domain.py:2150`'s worktree tier has been reaching nothing whenever the hook fires
  from inside a worktree, because `.git` is a file there and the `OSError` is swallowed. The third
  matters most: the claim that the corpus is read-only inside a worktree rests on that tier.
- `settings.json` registers nine hook commands, all through `${CLAUDE_PROJECT_DIR}`, and the five
  scripts the halted plan wanted to relocate appear in none of them — so the audit class and the
  not-hook-bound class are the same set. Under this DoD they stop needing corpus reach at all,
  which is cheaper than relocating anything.
- Member receipts from the halted altitude run assert conclusions with no lead verdict behind them.
  Evidence only; nothing in them is settled.
- Six harness defects filed out of the run, none to be folded into this feature: #1595, #1596,
  #1597, #1598, #1630, #1631.

## Verification discipline

`du` reports logical size and will pass a wrong implementation while failing a correct one. State
the measurement mode beside every claim: `ls .harness/*/features | wc -l` for materialisation,
`find -type f | wc -l` for the read surface, `df -k` delta for real blocks, `git status --porcelain
| wc -l` for cleanliness. No criterion is gated on a byte figure, because a byte bound is
satisfiable by APFS clonefile — the mechanism the operator's rule excludes.

## RECONCILIATION with the signed plan — 2026-09-11

FEAT-58's BRIEF and plan were signed at cycle 9 (`fd900d0b`). Every item of this note's BINDING ON
PLANNING table traces to its own REQ and at least one SC, verified in the artifacts rather than from
the plan's claim about itself:

| Item | REQ | SC | Tasks |
|---|---|---|---|
| D-1 | REQ-01 | SC-01 | N-02, N-05 |
| D-2 | REQ-02 (+REQ-08) | SC-02 (+SC-03) | N-03 |
| D-3 | REQ-03 | SC-04, SC-05, SC-06 (+SC-14, SC-16) | N-06, N-10, N-13, N-14 |
| D-4 | REQ-04 (+REQ-09) | SC-07 (+SC-08) | N-07, N-08 |
| D-5 | REQ-05 | SC-12 | N-09 |
| M-1 | REQ-06 | SC-09, SC-10 | N-02 |
| M-2 | REQ-07 | SC-11 | N-04 |
| nothing lost (strong form) | REQ-10 | SC-13 | N-09 |

**Three amendments to THIS NOTE, so the floor matches what was signed.** In each case the plan is
right and this note was stale — all three are operator rulings taken after the note was written and
never folded back.

1. **D-3 is narrowed by SUBJECT, not by LOCATION.** The rule stated above reads "only audit the
   active worktree". What was signed is narrower in what an audit examines and explicit about where
   it runs: a feature worktree's audit covers its own feature, and the four repo-level record audits
   — `board_lifecycle.py`, `check-plan-routes.py`, `validate-feature-json.py`, `check-domain.py`'s
   peer sweep — read **the owner root** (N-10, behind one `feature_corpus` seam). That follows this
   note's own altitude reasoning, that a repo-wide record audit belongs where the record is
   complete; the original sentence just did not say it. Read D-3 as: no audit sweeps the corpus
   *from inside a worktree*, and no audit reports clean over a subset.

2. **M-1's gate behaviour: exits 3-7 gate, exit 8 reports.** The mechanism section above says
   `--verify` "fails loudly" when a gate calls it. Amended at cycle 6 on finding PL-02: gating on
   the dirty-tree exit would make `check-state.py` — the canonical pre-commit gate for the whole
   repository — refuse in every dirty feature worktree, which is the normal mid-task state, and
   refuse ahead of the very commit that is exit 8's own stated remedy. The structural exits (3-7)
   gate; the dirty tree is reported and non-gating. SC-09 carries the reason inline.

3. **The fixture rule forbids COST and MUTATION, never READING the real tree.** "A synthetic
   repository … never a copy of this repository" was written against the #1526 precedent (a fixture
   copying `.claude/worktrees`, 239 s of a 240 s suite) and against mutating live state. It was read
   as forbidding any real-repository assertion. Clarified at cycle 6 on finding PL-04 and now
   binding here: read-only assertions against the real owner root are REQUIRED, because a fixture
   whose directories and records agree by construction cannot catch a defect that exists only
   because the real tree disagrees with itself — which is exactly the 89-versus-79 case. They are
   read-only, they never touch a live worktree, the dirty case uses a disposable tree, and the
   synthetic fixture keeps every assertion it already had. SC-16, N-13 and N-14 carry this.

**One item struck and not replaced.** SC-15 and the hardlink scan are gone (cycle 5), because a
control whose own failure mode is the harm it was added to prevent is worse than no control. The
general weakness is #1638. This note never required it.

**Signed with seven findings dispositioned**, in `plan.yaml`'s `approval.rulings`: H-01 converted to
build-phase work as N-14 with M-01 folded in; L-02 fixed by the operator at signature; M-02, L-01,
L-03 and NF-01 accepted as known residue. Reasoning:
`features/FEAT-58-corpus-outside-worktree/notes/answers-operator-c9.md`.
