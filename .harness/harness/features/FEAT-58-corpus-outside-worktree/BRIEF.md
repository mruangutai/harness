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
| **D-2 (DoD)** | Every other feature readable on disk | REQ-02 | SC-01, SC-02 |
| **D-3 (DoD)** | Audit: active feature only, no corpus, refuses | REQ-03 | SC-04, SC-05, SC-06, SC-14, SC-16 |
| **D-4 (DoD)** | No two features claim one branch | REQ-04 | SC-07 |
| **D-5 (DoD)** | Fresh clone and CI unchanged | REQ-05 | SC-12 |
| **M-1 (DoD)** | One idempotent `--verify`/`--repair`, verify never repairs, and a named gate calls `--verify` | REQ-06 | SC-09, SC-10, SC-16 |
| **M-2 (DoD)** | It runs from `post-checkout`, `post-merge`, `post-rewrite` | REQ-07 | SC-11 |
| — | Corpus path gitignored; writes through it refused | REQ-08 | SC-02, SC-03 |
| — | The live FEAT-02 / FEAT-03 collision, on real data | REQ-09 | SC-08 |
| — | Nothing altered outside the active feature | REQ-10 | SC-13 |

**One id moved at the cycle-3 goal-check fix (GC-02), and nothing else did:** `SC-01` now also
grades **D-2 (DoD)** — it asserts `.harness/corpus` as `islink` plus `realpath` equality at the
CREATION surface, which is where a worktree that cannot read the corpus is produced. `SC-02`
continues to grade the READ surface. No REQ id, and no other SC id, changed row.

**One id LEFT at the cycle-5 review, and it is the only removal:** `SC-15`, the hardlink-alias
denial, is **struck** on the operator's ruling (`plan.yaml` decision D-14,
`notes/answers-operator-c5.md:6-27`), together with the task parts that built it. Three reasons,
and none of them is cost: a hardlink alias is not the mistake class the write guard exists to stop
— the realistic shape is the fumbled path (#1635), while writing through a deliberately created
hardlink is evasion by an agent that already holds Bash, which has its own guard; path-based
guards are defeated by hardlinks **universally**, so closing it here puts a general weakness at
the wrong altitude and implies the rest of the guard surface is hardlink-safe, which it is not;
and decisively, the remedy's own failure mode **was** the harm it was added to prevent — the
widened scan fail-opened on exactly the class SC-15 existed to close, and a control whose failure
mode is the harm is worse than no control because it also buys false confidence.

**The strike reaches both of the hardlink half's gates, ruled at cycle 5:** the
`check-domain.sh:1916` scan widening comes out with it, because that gate entered scope in the
scan-site design as the hardlink hole and nothing else, keeping it would leave a widened guard
with **no criterion and no test** whose only failure path is an uncaught `corpus_root()` raise —
exit 1, which `check-domain.sh:14` declares non-blocking, so the write proceeds — and the only fix
for that failure path is the error conversion the same ruling forbids. **REQ-08 is still
delivered** by the surviving two-**route** denial — the Write/Edit route through
`check-domain.sh` and the Bash route through `bash-write-guard.sh:855`, carried by `plan.yaml`
task `N-03` and graded by SC-02 and SC-03: a governed write to a path under the
corpus symlink is refused on both registered routes, and that is the requirement. The general
weakness is filed as **#1638** against the guard surface generally.

Fifteen criteria, not twenty-two. **A criterion states an observable outcome a consumer can
check; a line describing how a test is BUILT is not one** — positive controls, instrumentation,
manifest comparisons, perturbation preconditions and red proofs are all still mandatory, and
they live in the `verify:` and intent of the task that owns them (`plan.yaml`'s **twelve** tasks,
`N-01 … N-13` with `N-11` retired and its id deliberately left as a gap so recorded citations
still resolve). Nothing was dropped as coverage: the assertion ledger in
`runs/consolidate-eng/digest.md` maps every one of them to a landing place,
`notes/research-FEAT-58-apply-consolidation.md` records the map,
`notes/research-FEAT-58-apply-batch-c3.md` records the cycle-3 additions together with the three
rows whose evidence form changed, `notes/research-FEAT-58-apply-c5.md` records the cycle-5
pass — one ledger row removed, by name, and it is SC-15's —
`notes/research-FEAT-58-fold-n11.md` records the N-11 fold, which **moved** one row's owning task
and removed none, and `notes/research-FEAT-58-apply-c6.md` records this cycle-6 pass — **four
ledger rows added and none removed, 41 → 45**, each named there with its landing place.

**Thirteen rather than twelve**, and this is the one place the count moved before cycle 3: SC-12
and SC-13 were a single criterion carrying two failure modes that break alone — a new failure in
an existing suite, and an edit to a feature directory other than this one. A distinct failure
mode earns its own criterion, and consolidating there would have dropped an assertion rather
than removed padding.

**Fourteen rather than thirteen**, the one addition surviving from the operator's cycle-3 review:
SC-14, because the cross-feature scan fail-open turned out to have NINE choke points and not two
— "the audit is narrowed" and "no other site under `bin/` silently narrows" are two outcomes that
break independently, and a site left unwidened reports clean over one feature of eighty-nine the
day this ships.

**Fifteen rather than fourteen**, the one addition from the operator's cycle-6 review: SC-16,
because every assertion this plan made about the audit ran against a synthetic fixture whose
directories and records agree *by construction*, and such a fixture cannot catch a defect that
exists only because the real tree disagrees with itself — measured at the real owner root as 89
feature directories against 79 `feature.json` records. "The mechanism is correct" and "the
shipped code holds over the real tree" are two outcomes that break independently, and this is the
third control in this feature found blind to the thing it existed to catch (plan decision D-16).

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
  `.claude/worktrees` accounted for 239 s of a 240 s suite. **That rule is about COST, and about
  not mutating the real tree; it was never a rule against READING the real owner root** (operator,
  cycle 6). SC-16's real-repository assertions are read-only, they ADD to the fixture's assertions
  rather than replacing any of them, and the only tree they write is a disposable probe worktree
  the task itself creates and removes (plan decisions D-11 and D-16).
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
  NESTED `.harness/<repo>/docs/`**; **and the corpus read path `.harness/corpus` is present as a
  SYMLINK, `os.path.islink` true and `os.path.realpath` equal to the owner root's
  `.harness/harness/features`** — a `.harness/corpus` that exists as a materialised copy, or as
  a link pointing elsewhere, is the state this feature removes; a
  non-active feature's directory is absent. It holds by the harness creation path and by a bare
  `git worktree add` alike — on both arms, because `post-checkout` fires on `git worktree add`
  with cwd already inside the new tree and its delegate is the `--repair` that creates the link.
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
  clean. The refusal is asymmetric and both halves are graded: a **missing** name — expected but
  not reached — gates ALWAYS; an **unexpected** name — reached but not expected — gates only
  **inside a linked worktree**, where it is the one-feature violation itself, and anywhere else
  (owner root, fresh clone, CI runner) is REPORTED in the same message and is NON-GATING, since
  an uncommitted feature directory must not make the pre-commit gate refuse ahead of the commit
  that is its own remedy.
  verify: automated      evidence: integration
- SC-07: No two feature records claim one branch, and the merge gate acts on it: a duplicated head
  branch is DENIED with both feature ids named, the same merge is ALLOWED once one record is
  corrected, and both hold with the gate running from **inside** a sparse worktree. The literal
  `none`, an absent value and an empty value are not claims and produce no finding.
  verify: automated      evidence: integration
- SC-08: The shipped check reports zero branch-collision findings over the repository's own
  feature records, read at the reviewed commit — the live `FEAT-02` / `FEAT-03-subissue-mirror`
  pair having been ERA-EXEMPTED with the records themselves left uncorrected, under a non-empty
  reason whose emptying reddens the check — and a NEW duplicate claim still produces exactly one
  finding, so the exemption silences that one historical pair and nothing else.
  verify: automated      evidence: integration
- SC-09: One command establishes and repairs the state a worktree must hold. `--verify` fails per
  broken input with **six distinct non-zero exits, each naming its own reason and its own remedy** —
  wrong cone; skip-bits cleared; corpus path absent; corpus path pointing elsewhere; more than one
  feature directory materialised; dirty tree, whose remedy is by hand and never `--repair`.
  `--repair` is idempotent, announces each repair it actually made and is silent only on a true
  no-op. **And a named gate calls it:** `check-state.sh`'s preflight invokes `--verify`, and a
  failing `--verify` makes that gate REFUSE non-zero before a single invariant runs, leaving the
  tree unrepaired — **for the structural exits only (3 through 7). The dirty-tree exit (8) is
  REPORTED and NON-GATING**, because a dirty tree is the normal mid-task state of a feature
  worktree and `check-state.sh` is the canonical pre-commit gate for the whole repository (its own
  header, `:24`); gating on exit 8 would refuse ahead of the very commit that is exit 8's own
  stated remedy, deadlocking every worktree it runs in (D-12, amended by the operator at cycle 6
  on PL-02).
  verify: automated      evidence: integration
- SC-10: `--verify` never repairs: against a broken tree it exits non-zero and the tree is
  **byte-for-byte unchanged** afterwards, and its message claims no repair it did not make.
  verify: automated      evidence: integration
- SC-11: The state survives a merge, a rebase and a bare creation because the shims fire — after a
  merge touching a hidden feature's file the tree is clean and the skip-bits intact, after a rebase
  the skip-bit set equals the pre-rebase set — and a hook-fired failure is legibly attributed
  without failing the git operation it rides on: the git command still exits 0, the attributed line
  names the shim and its delegate, and the tree is visibly still broken rather than silently fixed.
  **The merge case must FAIL today.** Host baseline, measured 2026-09-10 on the real corpus and
  NOT a fixture expectation: **3337 paths reported deleted, 3807 skip-bits cleared, 0 remaining.**
  verify: automated      evidence: integration
- SC-12: Nothing outside the target moved. A checkout that is NOT a linked worktree behaves exactly
  as today — full corpus materialised, audit finding set and exit status equal to pre-change,
  `--verify` a no-op, the three shims inert; and the existing suites gain no failure, the
  failing-test SET equalling the baseline recorded at its own sha under the identical command
  lines. Graded at the reviewed commit, resolved from `HARNESS_REVIEW_SHA` defaulting to `HEAD`.
  verify: automated      evidence: integration
- SC-13: Over this feature's own pinned commit range, no feature directory other than its own is
  altered — the strong form of "nothing lost", byte-identity and not citation resolvability:
  `git diff --name-only <pre_change_sha>..<review_sha> -- .harness/harness/features` names no
  path outside `FEAT-58-corpus-outside-worktree/`. Both endpoints are
  the IMMUTABLE 40-hex literals this feature's own notes record — `pre_change_sha` in
  `notes/suite-baseline.md`, `review_sha` in `notes/nonregression.md` — never a merge-base and
  never `HEAD`. The check SKIPS, **printing its reason and NAMING the endpoint**, when either
  literal is absent OR is present but resolves to no object in the clone it is running in, so it
  never grades a later feature's commit range and never fails for the absence of history it was
  not given; the authoritative observation is made once, locally, in a full clone and recorded in
  `notes/nonregression.md`. **No pathspec exclusion is authorised:** D-06 is decided
  as Arm B, no record outside this feature's directory is corrected, and the criterion is whole.
  verify: automated      evidence: integration
- SC-14: No cross-feature scan site under `.claude/skills/harness/bin/` silently narrows when a
  worktree materialises one feature directory. Two observations, both required. From inside a
  sparse worktree each widened site reaches the SAME number of feature records as the owner root
  — not `1`. And a census
  over every `.py` and `.sh` file under that directory finds ZERO **corpus enumerations** carrying
  no `corpus-scope` marker from the closed vocabulary, while a new unmarked site written into a
  scratch directory produces exactly one finding. **The census's subject is an enumeration and
  nothing wider:** a call to `glob`/`iglob`/`os.listdir`/`os.scandir`/`Path.iterdir`, a shell `ls`
  or a shell glob expansion, whose pattern names a `features` path segment and whose feature-id
  position is a wildcard or absent — so the site enumerates FEATURE DIRECTORIES. **Out of subject,
  explicitly:** comments, docstrings, message strings, regex literals, code-shaped string
  literals, single-feature path joins that never enumerate, and any site pinned or filtered to one
  caller-named feature id, which cannot narrow a count it never reports. The subject is source
  text, so the census reddens on the branch of whoever edits a scanner; it is quantified over the
  whole `bin/` tree and never over a file allow-list, and it pins no count over the real tree.
  verify: automated      evidence: integration
- SC-16: The shipped audit and its preflight hold over the REAL repository and not only over the
  synthetic fixture. Two observations, both required, and both READ-ONLY with respect to the owner
  root and to every live worktree. **At the real owner root**, read AS IT STANDS ON DISK — never at
  a pinned ref, because `check-state.sh` has no such notion (`grep -c HARNESS_REVIEW_SHA` over it
  returns 0) and honouring one would mean checking the owner root out to that ref, which this
  criterion's own read-only rule forbids (operator amendment, cycle 8, on PP-05) — the
  shipped `check-state.sh` produces NO expected-versus-reached mismatch refusal and proceeds past
  the choke point — at least one invariant line printed, and the number of feature directories it
  reached greater than `70` so a read of nothing cannot pass. **No census figure is an
  expectation:** the criterion is the ABSENCE of a mismatch, never that a count equals `89` or
  `79`, because the real tree gains feature directories and a pinned literal reds on the next one
  created. **And inside a DISPOSABLE worktree of this repository** — created and removed by the
  task itself, never a live one — that is in good state and then made dirty, `check-state.sh`
  REPORTS `--verify`'s dirty-tree exit and still runs its invariants, while the SAME probe carrying
  a STRUCTURAL break instead refuses before any invariant runs. The pair is required: "does not
  refuse on a dirty tree" is otherwise satisfied by a preflight that never ran.
  verify: automated      evidence: integration

## Verification gaps

- `component`, `ui` and `typecheck` carry `cmd: null` (`unresolved`); `functional` and `eval` are
  `excluded` (DEC-187). No criterion above rests on any of them. `unit` and `integration` are the
  only live runners, and assertions must live under `tests/unit/**` or `tests/integration/**` —
  the directory selects the kind (DEC-213). Several criteria are proven by unit assertions as well
  as integration ones — SC-07's `none`/absent/empty cases, SC-09's message contract, SC-11's static
  shim checks, SC-14's source-text census — and each declares `integration` because its
  **decisive** clause needs a real worktree, a real merge or a real rebase.
- **No runner reproduces the host-scale merge defect.** SC-11's merge clause is proven at fixture
  scale; the 3337/3807 figures are a one-shot host measurement recorded in the DoD note, not a
  fixture assertion. What is therefore NOT proven automatically: that the real 3337-path corpus
  survives a merge. What carries it: the same command run once by hand on this host after the
  change, recorded under a `HOST-SCALE RESIDUAL` heading in N-04's receipt.
- **SC-13's nothing-altered clause has no fixture, and CI cannot run it.** It grades this
  feature's own commit range, which no synthetic repository can hold, so its assertion runs `git`
  against the real repository over a range pinned to two immutable literals its own notes record.
  Measured: `.github/workflows/tests.yml:50` is `actions/checkout@v4` with no `fetch-depth`, a
  depth-1 shallow clone, so in CI neither pinned object exists and the clause **announces a skip
  naming the endpoint** rather than reddening the sole required branch-protection context. What is
  therefore NOT proven in CI: nothing-altered. What carries it: one authoritative local run in a
  full clone, recorded verbatim under `## NOTHING ALTERED` in `notes/nonregression.md`, which the
  collected clause cross-checks wherever the objects resolve. Setting `fetch-depth: 0` was
  rejected — SC-12 asserts the CI runner is unchanged (plan decision D-13).
- **Two pre-change comparisons are no longer standing tests, and that is a real reduction.** A
  permanently collected test may not derive its pre-change side from a moving git ref (plan
  decision D-13), because after this feature merges the merge-base already holds the post-change
  file. Two assertions are therefore demoted to one-time proofs: N-09's audit-unchanged
  comparison, recorded under `AUDIT UNCHANGED` in `notes/nonregression.md`, and N-06's
  verify-gate pre-change reproduction, recorded under `PRE-CHANGE REPRODUCTION` in that task's
  receipt. What is therefore NOT re-proven on every suite run: that the pre-change
  `check-state.sh` behaves differently from the shipped one. What carries it: those two recorded
  verdicts, each naming the 40-hex sha it read and the command it ran, each a blocker on its own
  task. SC-12's other clauses and SC-13 stay standing assertions.

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
- **The hardlink-alias weakness in path-based guards, filed as #1638.** A worktree-local hardlink
  aliasing another feature's `plan.yaml` is invisible to `_hardlink_plan`'s root-scoped glob and
  to `worktree_owner()`, which is pure path arithmetic with no inode awareness. It is a general
  property of path-based guards rather than anything the corpus read path creates, and closing it
  inside this feature was struck by the operator at cycle 5 (plan decision D-14). REQ-08 is still
  delivered: a governed write to a path under the corpus symlink is refused on both routes.
- **The ten tracked feature directories carrying no `feature.json`, filed as #1640.** Measured at
  the real owner root at cycle 6: 89 feature directories against 79 records, the ten record-less
  ones holding tracked, non-ignored notes. It is a RECORD defect and not a replication one, ruled
  out of this feature by the operator at cycle 6. This feature's audit is expected to REPORT them
  accurately meanwhile — no suppression, no allow-list, and no restriction of either audit set to
  `feature.json`-carrying directories, which would report clean over a subset and is the exact
  defect this feature exists to remove.
- **Not this feature, by operator instruction:** the filed harness defects (#1595, #1596, #1597,
  #1598, #1630, #1631, #1635, #1636, #1637, #1638 and #1640); `FEAT-53`'s 138 MB of untracked run
  dirs (a retention defect, not replication); `597-omp-behavior-baseline`'s unlanded work.

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
  `bin/post-merge-sweep.sh` (FEAT-34 T-11, D-08) so a test can reach it. `bash-write-guard.sh:611-741`
  already refuses `git worktree add` outside the sanctioned location.
- **Shared file:** `.claude/skills/harness/bin/check-state.sh` is also touched by FEAT-57's T-19.
  Serialise the edits.
- **Naming:** `.agents` is a symlink to `.claude`; the repo-tracked surface is spelled
  `.claude/skills/...`, and `git show` of an `.agents/` path prints nothing.

## Approval

status: pending
