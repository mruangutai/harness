# Grilling — the feature corpus must not be replicated into a worktree — 2026-09-09

Source ticket: issue #1559. Two measurement/design comments on that ticket are part of this
artifact by reference and pm should read both:
- measurements: https://github.com/mruangutai/harness/issues/1559#issuecomment-5612266665
- design: https://github.com/mruangutai/harness/issues/1559#issuecomment-5612425746

## Destination

A feature worktree materialises exactly one feature directory — its own — and the active feature
can still read every other feature's record from outside the worktree, with no gate able to
report clean on a partial view.

## Settled

- Is a cheap copy acceptable (APFS clonefile making 42 MB cost 0.3 MB of real blocks)? →
  **No.** The rule is that the corpus is not replicated, not that replication is cheap. Reflink
  is orthogonal and optional, considered only after the rule holds.
- Must the corpus still be reachable from the active feature? → **Yes, this is the other half of
  the bedrock rule.** "Not materialised" and "fully available" both bind; availability is not
  tradeable for bytes.
- Where does the corpus live? → **Outside the worktree, materialised once.** Two providers:
  the shared object database (authoritative, version-addressable, already outside every
  worktree) and the owner-root checkout (path convenience, already on disk, not a second copy).
- What happens when a reader sees fewer features than the record holds? → **It refuses,
  non-zero, naming `N of M`.** Never reports clean. This is measured live behaviour today, not a
  hypothetical: see Facts.
- Is the state-store-in-the-working-tree question (ticket question 3) in scope? → **Only as far
  as the read path.** No write path moves, nothing is pruned, no record is rewritten, and the
  record stays git-tracked at its existing paths.
- Are standing worktrees removed to achieve this? → **No.** 29 exist and stay; migration is an
  in-place `git sparse-checkout set`.

## Not yet specified

- Which of the eleven `features/*` readers are genuinely single-feature and need no change. The
  design's ledger proposes a split (four corpus sweeps, four own-feature, two fixture-only, one
  path-logic) but calls confirming it the plan's first task rather than an assumption.
- Whether the corpus root belongs in `harness_boundary.py` beside `worktree_owner()` or in a new
  module. Either satisfies the rule; it is an architecture call for eng-lead.
- How a task that legitimately needs the whole corpus declares which provider and which ref it
  read. The design requires it be stated; the mechanism is unspecified.
- Whether the sparse include-list is enumerated in source or derived. Enumeration was what the
  probe used; a derived list is not yet designed.

## Out of scope

- APFS clonefile / reflink worktree creation. Measured and real (42,248 KB → 340 KB of real
  blocks) but it makes a copy cheap rather than removing it, so it does not meet the rule.
- Moving the state store out of git, archiving, pruning, or lossily rewriting any feature's
  record. Ticket question 3 in its full form.
- Reducing the number of standing worktrees.

## Facts I verified (so pm does not re-derive them)

All at `abff2a84`, on this host, with two throwaway probe worktrees since removed.

- A worktree materialises the whole landed corpus — `ls .harness/harness/features | wc -l` inside
  `.claude/worktrees/harness/FEAT-57-review-latency` returns **87**.
- The corpus is 3306 tracked files / 36 MB, of which `notes/` alone is 2724 files / 27.9 MB;
  `.harness/` is 3434 of the repository's 3724 tracked files (92%).
- Current cost: **30 worktrees, 1217 MB**. `.git` is shared (74 MB, paid once) — nothing is cloned;
  the working tree is materialised 30 times.
- Growth: corpus bytes in `main`'s tree went 0.2 MB (2026-08-01) → 8.5 → 19.3 → **29.8 MB**
  (2026-09-09), ≈ +1.1 MB/day, which at 30 worktrees is ≈ +33 MB/day of disk.
- Cone-mode sparse checkout carrying one feature: **44 MB → 8.9 MB**, 463 files instead of ~3900,
  and `git status --porcelain` is **empty** — SKIP_WORKTREE means the dirty-tree halt does not fire.
- The corpus is fully readable from inside a worktree with nothing materialised:
  `git ls-tree -d --name-only main:.harness/harness/features | wc -l` → 87, and
  `git grep -l review_sha main -- .harness/harness/features` → 932 files in **0.06s**, against
  **0.30s / 928 files** for the materialised copy. The git-served view is both faster and less
  stale than the copy.
- The fail-open is live, not hypothetical: `check-state.sh` run in the sparse probe swept **1 of
  88** features and **exited 0**.
- Nothing needs a second feature's directory: every `team-config.yaml` domain glob is
  `features/*/…` (a wildcard over one feature) and DEC-208/DEC-218 already bind feature writes to
  the registered worktree, so the corpus is read-only in a worktree by construction.
- A worktree never carried live siblings' in-flight state anyway: `FEAT-57-review-latency` has no
  directory at `main`'s HEAD.
- `harness_boundary.worktree_owner(path)` already returns `(checkout_dir, owner_root, legitimate)`,
  so deriving a corpus root is a small function at an existing seam.
- Sweep latency is not an argument either way: `check-state.sh` 3.78s full vs 3.10s sparse.

## Constraints pm must carry into the plan

- `check-state.sh` is shared with FEAT-57's T-19 — serialise the edits.
- Execution waits on FEAT-57's replay manifest and dataset being frozen and spot-checked; planning
  has no precondition.
- DEC-174, CORRECTED 2026-09-10 (the original wording here had it backwards, and the design comment
  on issue #1559 repeats the error): a change to hooks, validators and gate scripts is made
  **directly by the main session**, never dispatched through a team run whose gates are the artifact
  being changed. `feature-worktree.py`, `check-state.sh`, `harness_boundary.py`, `check-domain.py`,
  `merge-gate.py`, `dispatch-guard.sh` and the validators are exactly that surface, so those tasks
  belong in the `main-session-direct` lane and `check-plan-routes.py` printing DEVIATION on them
  while exiting 0 is the carve-out working.
- The verification trap: `du` reports logical size. A criterion phrased as "`du` of
  `.claude/worktrees` falls below N" passes a wrong reflink implementation and fails a correct one.
  State the measurement mode next to every claim — `df` delta for real blocks, `find -type f | wc -l`
  for the read surface, `ls features | wc -l` for materialisation.
