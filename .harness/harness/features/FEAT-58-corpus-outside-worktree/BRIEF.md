# BRIEF — FEAT-58-corpus-outside-worktree

Feature id **ratified**, not coined: `FEAT-58-corpus-outside-worktree` is already the worktree
directory name and the branch name (`feat/FEAT-58-corpus-outside-worktree`), so DEC-133's
immutability rule forecloses renaming it. Source ticket: issue #1559. Grilling artifact (step zero,
already run): `.harness/notes/grilling-worktree-corpus-2026-09-09.md`.

## Problem

A git worktree checks out the whole tree, so isolating one feature's *code* replicates the entire
*state store* with it. Observed at `abff2a84` on this host: a worktree materialises the whole landed
corpus — `ls .harness/harness/features | wc -l` inside a feature worktree returned **87**
(88 at the current tip). The corpus is 3306 tracked files / 36 MB, of which `notes/` alone is 2724
files / 27.9 MB; `.harness/` is 3434 of the repository's 3724 tracked files. **Standing cost — the
one measurement this document uses, stated once here: 30 worktrees, 1217 MB.** Measured on this
host at `abff2a84` (`.harness/notes/grilling-worktree-corpus-2026-09-09.md:62`); the same artifact
at `:56` records that two throwaway probe worktrees were removed after that measurement, so a live
enumeration today may return one or two fewer. That is the measurement's mode, not a competing
figure. Every later mention of the standing-worktree count below refers back to this paragraph
rather than restating a number, and no criterion is gated on the value: SC-06 and the migration
enumerate the live set and compare it against itself. (`.git` is shared and paid once — nothing is
cloned; the working tree is materialised once per worktree.) The corpus in `main`'s tree grew
0.2 MB (2026-08-01) → 29.8 MB (2026-09-09), ≈ +1.1 MB/day tracked, ≈ +33 MB/day of disk at the
measured count. The cost is O(features × worktrees) and both terms only grow.

None of it is needed there. Every `team-config.yaml` domain glob is `features/*/…` — a wildcard over
one feature — and DEC-208/DEC-218 bind feature writes to the registered worktree, so the corpus is
read-only in a worktree by construction — except that the guard tiers enforcing that binding reach
nothing when the hook fires from inside a worktree (`harness_boundary.py:171-175` returns `[]` on
`OSError` because `.git` is a file there), at all three of the call sites that pass the wrong root:
the two that DENY a write (`check-domain.sh:752`, `:780`) and the one that REPORTS (`:2150`). So the
guarantee is asserted and not enforced until REQ-12 closes it. A worktree cut from `main` never
carried a live sibling's
in-flight state (`FEAT-57-review-latency`, live in a sibling worktree, has no directory at `main`'s
HEAD). It is a read-only reference copy of history, replicated N times.

The second half of the problem is what happens when you remove it carelessly. Measured in a
throwaway cone-mode sparse probe at `abff2a84`: `check-state.sh` swept **1 of 88** features and
**exited 0**. Every record-sweep invariant is scoped to whatever happens to be on disk, so a partial
view reports clean. `git status --porcelain` was also empty in that probe — SKIP_WORKTREE means the
dirty-tree halt does not fire on the unmaterialised paths.

## Goal

The operator's bedrock ruling, both halves binding: **the feature corpus is never materialised
inside a worktree, and it remains fully available to the active feature from outside the worktree.**
"Not materialised" is not satisfied by making the copy cheap; "available" is not tradeable for
bytes. A feature worktree materialises exactly one feature directory — its own — while every other
feature's record stays readable, complete and version-addressable from inside that worktree, and no
gate can report clean on a partial view.

## Requirements

- REQ-01: Creating a feature worktree materialises exactly one feature directory, its own, and no
  other feature's record exists as a file inside it.
- REQ-02: From inside such a worktree, the whole corpus — every feature's record, at a stated
  version — is enumerable, readable and searchable, at zero additional materialised bytes.
- REQ-03: A reader that walks the feature tree resolves the corpus set from a source independent of
  what is materialised in the working tree, never from what is underfoot.
- REQ-04: A reader refuses, non-zero, when the CORPUS ROOT it resolved holds fewer feature
  directories than the corpus set resolved from that same root. The count is taken at the corpus
  root, never at the reader's own checkout — a sparse checkout is the designed end state of REQ-01,
  so a predicate reading it would refuse on this feature's own success path. That refusal names
  `N of M` and the corpus root it used. Refusal is the default path, not an error branch: a reader
  that cannot resolve a corpus root, or cannot resolve the ref it was given, refuses rather than
  sweeping — with a message naming what could not be resolved and carrying NO `N of M` count.
  Every refusal message states what to do next, not only what is wrong.
- REQ-05: A recorded corpus sweep states the frame it read — which provider, and for the
  history-backed provider which ref — so a sweep's scope is auditable after the fact. A sweep that
  uses more than one provider in the same run (for example a history-backed completeness gate
  alongside a path-backed content read) states each frame on its own, naming the base each provider
  actually used; one merged line covering two different reads is auditable as neither.
- REQ-06: The standing worktrees converge on the same behaviour in place. None is removed, none is
  re-cloned, and one carrying uncommitted work is refused rather than converted.
- REQ-07: No feature's recorded history is deleted, pruned or lossily rewritten; the record stays
  git-tracked at its existing paths, and no write path moves.
- REQ-08: Every existing citation into the record stays resolvable, including the note paths cited
  by FEAT-57's frozen replay dataset.
- REQ-09: The single-feature readers keep behaving exactly as they do today, and the corpus readers
  are accounted for by working instrument rather than by a remembered count. Every reader named in
  the reader ledger (`notes/receipt-harness-backend-dev-arch-eng.md`) is individually accounted for,
  by parity or by refusal, and so is every script `.claude/settings.json` registers as a hook —
  including the six the ledger never reached: `bash-write-guard.sh`, `validate-digest.py` and
  `dispatch-guard.sh`, each of which resolves at most one feature from a path or a text field and
  enumerates nothing, and `gh-close-gate.sh`, `plan-sign-gate.sh` and `inject-expertise.sh`, which
  carry no feature-record path at all and are therefore outside the reader set, with that reason
  stated in the record itself rather than left silent. The ledger is carried as named evidence and
  stays OPEN as an artifact, because no instrument proves completeness over readers cleared by
  inspection. No count is asserted: a count is satisfied by N-1 conforming readers and is blind to
  the Nth, and this effort has already moved eleven → twelve → fourteen → OPEN. What is owed
  instead is two instruments that fire — a discovery scan asserting every file calling the corpus
  API is a named, accounted-for reader, and a lint asserting no file outside the API enumerates the
  corpus at all.
- REQ-10: A checkout that is not a linked worktree — a fresh clone, a CI runner — behaves exactly as
  before this feature: identity behaviour, full tree, no refusals.
- REQ-11: An agent reading the agent-facing prose can tell where the corpus lives and how to read
  it, and is never instructed to enumerate the record relative to its own checkout.
- REQ-12: The corpus root is read-only from inside a feature worktree, and that read-only property
  is ENFORCED rather than asserted by construction: every guard tier that binds writes to the
  registered worktree reaches the checkouts it claims to cover, and refuses a write whose owning
  checkout it cannot resolve rather than allowing it.

## Success Criteria

Measurement discipline, binding on every criterion below: **`du` is forbidden as evidence for any
block-level or footprint claim** — it reports logical size, so it passes a wrong implementation and
fails a correct one. Materialisation is counted with `ls <dir> | wc -l`, read surface with
`find <dir> -type f | wc -l`, real blocks (nowhere load-bearing here) with a `df -k` delta. A
bytes-only criterion is deliberately absent: a clone-on-write implementation would satisfy one while
violating the rule, so every footprint criterion below counts entries or files, which such an
implementation cannot pass.

- SC-01: In a worktree created by the standard creation path for feature `<ID>`,
  `ls <worktree>/.harness/harness/features | wc -l` returns `1` and the single entry is `<ID>`. The
  test demonstrates the failing state first: the same command against a worktree created by the
  pre-change path returns the full corpus count (87 at `abff2a84`).
  verify: automated      evidence: integration
- SC-02: The read surface of that worktree, counted as `find <worktree> -type f | wc -l`, is at
  least an order of magnitude below the pre-change count, and zero of those files lie under
  `.harness/harness/features/` outside `<ID>`. The second clause is the discriminating one: an
  implementation that only makes the copy cheap leaves the file count unchanged and fails here.
  verify: automated      evidence: integration
- SC-03: From inside that worktree, the corpus is complete: the feature-directory count resolved
  through the corpus path equals the count at the owner root's default branch, and a content search
  over the corpus returns a path set equal to the one the owner root returns for the same query. The
  search is NAMED, not implied — it is
  `git -C <corpus_root> grep -l <needle> <ref> -- .harness/harness/features/`, with the leading
  `<ref>:` stripped from each returned path, where `<ref>` is the owner root's default branch
  resolved once as `git -C <owner_root> rev-parse <default-branch>` and `<needle>` is a fixed
  literal string committed into more than one feature directory, so a single hit cannot pass by
  accident. The same command run at the owner root supplies the comparison set. Equality of sets
  and counts, not of bytes, and never a substring check over concatenated output.
  verify: automated      evidence: integration
- SC-04: Every corpus-sweeping reader the reader ledger classifies as a sweep — each named
  individually — refuses when the CORPUS ROOT it resolved is short of the set resolved from that
  root. Run against a fixture whose corpus root holds M feature directories with fewer than M
  materialised, each reader exits non-zero, prints `N of M`, names the corpus root it used, and
  prints a next step the operator can act on — what to run or check — not merely the fact. Each
  reader is asserted individually; a suite-wide green does not discharge this, and neither does a
  substring-presence assertion on three tokens: the actionability clause is asserted as its own
  check. The fixture shape is retained — a repository standing as its own corpus root, partially
  materialised — because it tests the corrected predicate directly rather than synthesising an
  unreachable state. In production this refusal fires only when the owner root's never-sparse
  invariant is itself violated (a migration mistargeting the owner root, a manual
  `git sparse-checkout` run there, corruption); it is that invariant's last-line defence, and a
  blobless clone does NOT trigger it. Two failing states are demonstrated first: the same fixture
  against the pre-change `check-state.sh` exits 0 having swept a subset, reproducing the measured
  `1 of 88 / EXIT=0`; and the pre-change `merge-gate.py`, whose `feature_for` finds no owning
  `feature.json` under a partial view, ALLOWS the merge at `merge-gate.py:169`
  (`if not owners: return`) — a confirmed fail-open that this change arms and must therefore close.
  For `merge-gate.py` the required behaviour is a denied merge, not a swept count.
  verify: automated      evidence: integration
- SC-05: When the corpus cannot be resolved — no corpus root derivable, or a named ref missing — the
  reader refuses non-zero, names what it could not resolve, states what to do next, prints NO
  `N of M` count (that count belongs to the short-root case alone, and its absence here is what
  distinguishes the two refusal states), and sweeps nothing. Proven by a fixture that removes the
  resolution input while leaving a partial view on disk; a reader that falls back to the on-disk
  view fails the criterion, and so does one whose message names the fault without a next step.
  verify: automated      evidence: integration
- SC-06: Every linked worktree of the owner root is converged in place and individually accounted
  for. The migration writes a per-worktree record under this feature's `notes/` naming, for each
  linked worktree: its id, `ls .harness/harness/features | wc -l` before and after, and its dirty
  status; every entry reads post-count `1`, or carries an explicit refusal reason. The set of linked
  worktree basenames enumerated before and after migration is identical — none removed, none added.
  A criterion covering only newly created worktrees would leave the standing ones wrong, which is
  why the per-worktree enumeration, not an aggregate, is what is graded, read at `review_sha` with
  `git show <review_sha>:<path>`.
  verify: inspection
- SC-07: No recorded history is lost. Over this feature's own commit range, pinned as
  `git merge-base <default-branch> HEAD`..HEAD and never left unbounded,
  `git log --diff-filter=D --name-only -- .harness/harness/features` names no file, and no path
  under the record is moved or rewritten. Graded at `review_sha`, and the check asserts BOTH the
  command's exit status AND that its stdout is empty: `git log` exits 0 whatever it prints, so a
  status-only assertion can never go red.
  verify: inspection
- SC-08: Every note path cited by FEAT-57's frozen replay manifest resolves, from inside a converged
  worktree, to non-empty content at the ref the manifest records. Each cited path is asserted
  individually; an aggregate resolvable-count is satisfied by the conformers alone and does not
  discharge this.
  verify: automated      evidence: integration
- SC-09: The reader inventory is graded by instrument, not by a count. Both instruments exist and
  both are shown to fire: (a) a discovery scan asserts that every tracked file calling
  `corpus_root` / `corpus_features` / `corpus_read` outside `harness_boundary.py` is a MEMBER of the
  named-reader list (⊆ — soundness, not completeness) and reddens when a real API caller is dropped
  from that list; (b) the lint asserts that no tracked file outside `harness_boundary.py` enumerates
  the corpus directly, and reddens against a known-violating fixture line for each enumeration
  shape. Every reader named in the list is individually either proven unchanged in behaviour — same
  exit status and same output for the same input in a converged worktree and in a full checkout — or
  covered by SC-04's per-reader refusal assertion; a named reader in neither list fails this
  criterion. The ledger is cited as the evidence of what has been classified so far and is recorded
  OPEN. No number of readers is asserted: completeness over inspection-cleared readers is not
  mechanisable, and this criterion does not fake it.
  verify: automated      evidence: integration
- SC-10: Cleanliness is evaluated before the cone changes, and a worktree carrying uncommitted work
  is refused non-zero and left untouched. The test's modification lies in a path the new cone would
  exclude, so an implementation that inspects the tree only after sparsification sees an empty
  `git status --porcelain` (measured behaviour of SKIP_WORKTREE at `abff2a84`) and fails the
  criterion. The refusal is demonstrated red first against an implementation that checks after.
  verify: automated      evidence: integration
- SC-11: The agent-facing prose surface carries the corpus anchor, graded over an OPEN set rather
  than a named three. Read at a pinned ref — `review_sha` when it is pinned, else `HEAD`, with the
  sweep printing which it used — the sweep globs every `.claude/skills/**/SKILL.md`, every
  `.claude/agents/*.md` and every `.claude/commands/*.md` and asserts that no live agent-facing
  instruction directs a reader to enumerate the record relative to its own checkout, and that each
  surface designated as an anchor surface states where the corpus lives and how to read it. A
  closed enumeration of the files the change itself edited does not discharge this: a 27th skill
  file must be able to redden it. The sweep pairs its absence search with a positive control that
  must match, and asserts the search's exit status — an absence count alone passes when the search
  errors. Prose has no gate, so the reader is named rather than left as "the reviewer":
  `harness-ui-reviewer` reads the sweep's output and the anchor paragraphs and judges whether an
  agent could act on them. The sweep is this criterion's evidence, not a competing automated gate.
  verify: inspection
- SC-12: In a checkout that is not a linked worktree, behaviour is identical to the pre-change code:
  corpus resolution returns that checkout, and each reader's exit status and swept feature count
  match the pre-change values for the same input. CI is unaffected.
  verify: automated      evidence: unit
- SC-13: The growth term is broken: landing a new feature directory on the default branch does not
  change `find <worktree> -type f | wc -l` for an existing converged worktree. Counted as files, not
  bytes.
  verify: automated      evidence: integration
- SC-14: A recorded corpus sweep states the frame it read. For `check-state.sh` and for each of the
  four validator sweeps, the run's output carries TWO distinct frame lines — the ENUMERATION frame
  naming `provider=history` and the resolved ref, and the CONTENT frame naming `provider=path` and
  the base — and where the in-flight feature entered the scope through the caller-side union, the
  content frame names that feature and its own base. Each line is asserted individually, per reader;
  one aggregate substring search over a run's output is satisfied by either line alone. The failing
  state is demonstrated first: the pre-change readers print no frame line at all. Presence and
  content of the recorded frames is what is graded; there is no dispatch-time declaration to grade,
  and no byte-for-byte parity with pre-change output is claimed — added output cannot be
  byte-identical to output without it.
  verify: automated      evidence: integration
- SC-15: Fired from inside a linked worktree, `check-domain.sh`'s two DENIAL tiers REFUSE a write they
  must refuse. Graded by OUTCOME, each clause individually, never by a reached-path set — a tier can
  enumerate correctly and still not deny:
  (a) `feature_checkout_guard`: a write to a feature artifact belonging to a SIBLING linked worktree,
  attempted from inside a different linked worktree, exits 2 and the message names the expected worktree.
  (b) `claim_checkout_guard`: a governed `harness-` agent whose live claim is registered in a SIBLING
  worktree's registry, writing to a harness-base path outside that claimed worktree, exits 2 and the
  message names the held claim set. The claim must live in a sibling registry, so a tier enumerating
  only its own checkout cannot see it.
  (c) the owner root unresolvable (`corpus_root` returns None): BOTH tiers exit 2. An enumeration that
  cannot be resolved is a refusal, never a pass-through.
  (d) the REPORT tier at the sweep reaches a matching file in a SIBLING linked worktree, asserted as a
  path SET by name and never as a count — a count is satisfied by the root tier alone and is blind to an
  empty worktree tier. This clause alone does not satisfy the criterion; it is the third call site of the
  same defect, not the denial behaviour.
  The failing state is demonstrated first and separately for (a), (b) and (c): against the pre-change
  spelling — `linked_worktrees(root)` where `.git` is a file — each of those three writes is ALLOWED,
  exit 0. That allow is the defect.
  verify: automated      evidence: integration

## Verification gaps

- `component`, `ui` and `typecheck` carry `cmd: null` (status `unresolved`); `functional` and `eval`
  are `excluded` (DEC-187). No SC above rests on any of them. `unit` and `integration` are the only
  live runners and every `automated` SC names one of them. Assertions must live under
  `tests/unit/**` or `tests/integration/**` — the directory selects the kind (DEC-213).
- **No runner exercises real host state.** SC-06 (the standing worktrees, at the count Problem
  measures) and SC-07 (nothing deleted) are graded by inspection of a recorded,
  `review_sha`-pinned transcript, because the outcome is a one-shot change to this host's disk, not
  a property a test fixture can hold. What is therefore NOT proven automatically: that the
  migration ran over every standing worktree on this machine. What carries it: the per-worktree
  record required by SC-06 and the reviewer reading it. A host-state audit script would close this;
  it is a dev-ops backlog item, not this feature's.
- **Prose has no gate at all.** SC-11 is inspection by construction. An agent that runs
  `ls .harness/*/features` inside its worktree and concludes the record is gone is the same
  fail-open in prose, and only the reviewer catches it.

## Non-goals

Each of these is closed, with the reason attached so a later reader cannot re-open it casually.

- **APFS clonefile / reflink worktree creation as the mechanism.** Measured and real — 42,248 KB of
  real blocks for `git worktree add` versus 340 KB for `cp -Rc`, a 124× reduction, `df -k` delta at
  `abff2a84`. It is excluded because it makes the copy cheap instead of removing it: file count,
  gate-sweep surface, agent read surface and the O(features × worktrees) growth term are all
  untouched, and the operator's rule is that the corpus is not replicated, not that replication is
  cheap. Orthogonal and optional, worth taking on the residual **only after the rule holds**.
  Reopening it as the mechanism requires the operator to revise the bedrock rule.
- **Moving the state store out of git, archiving, pruning, or lossily rewriting any feature's
  record** — issue #1559's question 3 in its full form. Only the READ path is in scope. No write
  path moves, nothing is pruned, no record is rewritten, and the record stays git-tracked at its
  existing paths. Settled at grilling on 2026-09-09; it is a separate architectural decision about
  what this repository is.
- **Reducing the number of standing worktrees.** Every standing worktree — at the count Problem
  measures — stays. The DoD is about what a worktree costs, not how many exist; migration is in
  place and removes nothing. Removing a worktree is additionally not an agent's act at all.
- **Changing the write path.** Feature writes bind to the registered worktree (DEC-208/DEC-218), and
  no write path, write rule or claim-set moves here. What is NOT excluded, and is REQ-12, is the
  correction that makes that binding actually reach sibling checkouts — one wrong owner root passed at
  three call sites (`check-domain.sh:752` and `:780`, which deny a write, and `:2150`, which reports),
  plus a refusal when that root cannot be resolved at all. Measured, the domain guard's worktree tiers
  reach nothing when the hook fires from inside a worktree, so the read-only guarantee this feature
  leans on is asserted rather than enforced today. Correcting the tiers and testing them is in scope;
  changing what the write rule says is not.

## Constraints

- **The bedrock rule** (operator ruling 2026-09-09, issue #1559 comment 5612425746) BLOCKS: both
  halves bind, and a solution satisfying only one is not a solution.
- **DEC-174** BLOCKS DISPATCH — not planning, and not execution: `feature-worktree.py`,
  `check-state.sh`, `harness_boundary.py`, `check-domain.sh`, `merge-gate.py`,
  `branch-create-gate.sh` and the validators ARE the enforcement path being changed, so every change
  to them is made **directly by the main session** and is never dispatched through a team run whose
  gates are the artifact being changed. Corrected at source on 2026-09-10
  (`.harness/notes/grilling-worktree-corpus-2026-09-09.md:89-92`): the earlier gloss "may plan but
  must not execute" had it backwards. A majority of this plan's tasks sitting in the
  `main-session-direct` lane is intended, and `check-plan-routes.py` exiting 0 with informational
  DEVIATION lines is the carve-out working as designed.
- **DEC-133** BLOCKS renaming: the feature id is immutable once created.
- **DEC-95** SUPPLIES: `.harness/` is per-worktree state, which justifies **the live feature's**
  directory in the worktree and says nothing about the other 87. It is not an obstacle to removing
  the rest.
- **DEC-214** SUPPLIES: two anchors already exist — an injected control-plane root for reads and a
  dispatch-resolved feature-tree root for writes. A read-only cross-feature corpus anchor extends
  that ruling rather than competing with it, and
  `harness_boundary.worktree_owner()` already returns `(checkout_dir, owner_root, legitimate)`, so
  the derivation sits at an existing seam.
- **DEC-208 / DEC-218** SUPPLY: claim-set binding already refuses feature writes outside the
  registered worktree, so no new write guard is needed for a corpus root that lives outside it.
- **DEC-193** SUPPLIES the bound: exactly two locations hold code under harness authority —
  `WORKTREES_SEGMENT`-rooted checkouts and `workspace_root/<repo>` — so corpus-root derivation has a
  closed set of legitimate answers.
- **DEC-163** BLOCKS resting any `verify: automated` SC on a kind whose runner is null; see
  `## Verification gaps`.
- **DEC-213** BLOCKS test placement: `tests/unit/**` and `tests/integration/**`, directory selects
  kind.
- **Shared file:** `.claude/skills/harness/bin/check-state.sh` is also touched by FEAT-57's T-19.
  Serialise the edits.
- **Sequencing:** planning has no precondition. EXECUTION waits on FEAT-57's replay manifest and
  dataset being frozen and spot-checked — inside FEAT-57's build, not at its terminal state.
- **Measurement:** `du` reports logical size and is forbidden as evidence for footprint claims.
  Every measured claim states its mode inline.
- **The four open architecture questions are now answered by measurement**, in the arch-eng run of
  2026-09-09 (`runs/arch-eng/digest.md` and the two receipts under `notes/`): which readers are
  genuinely single-feature, where the corpus-root derivation lives, how a task declares its
  provider and ref, and whether the sparse include-list is enumerated or derived. Each is recorded
  as a `D-NN` in `plan.yaml`. This document states the outcome they must satisfy, never the
  mechanism.

## Approval

status: pending
