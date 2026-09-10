# REUSE angle — plan.yaml, FEAT-58-corpus-outside-worktree

## Conclusion

The plan reuses correctly at the module level (owner-root resolution, cone derivation, the
`.agents`/`.claude` precedent, the shim skeleton) — no task re-derives a mechanism that
`harness_boundary.py`, `feature-worktree.py`, `worktree_terminal.py` or `merge-gate.py` already
export. **One real finding**: T-02's `add_worktree()` re-derives, a fifth time, a `git worktree
add` fixture helper that four existing test files already carry near-identically. Everything
else below is a "no duplication found" with the check shown.

## Q1 — T-03 vs feature-worktree.py / worktree_terminal.py / harness_boundary.py

**No.** Verified by reading `harness_boundary.py:715-793` (`worktree_owner`, confirmed correct
FILE-`.git` parsing and `owner_root` return) and `feature-worktree.py:58-83` (`dest_for`,
`resolve_repo`, `_ID_RE`). T-03's five checks use `harness_boundary.worktree_owner()` for
owner-root — imported, not re-derived — and `os.path.basename(worktree)` for the
worktree-basename-to-feature-id mapping, which is one line, not a restatement of `dest_for`'s
forward path-builder (`owner_root/segment/id`); the two are inverse operations and `dest_for` is
not actually needed by any of the five checks as specified. T-03's own intent names
`worktree_terminal.py:38-45`'s import-by-path pattern and follows it rather than re-deriving a
loader. The cone-derivation logic itself (D-08: `git ls-tree -d --name-only HEAD` minus
`.harness` plus two explicit adds) has no precedent anywhere in `bin/` — grepped the whole
directory for `sparse-checkout`/`sparse_checkout`/`ls-tree -d` and found zero matches outside
this plan's own decisions. It is new work, not a re-implementation.

## Q2 — T-09's feature-index.py vs existing feature.json readers

**No exact duplicate, but several existing readers do the adjacent thing and are worth naming
so nobody re-proposes folding them together.** Every existing aggregate reader globs the
*working tree*, which is exactly the blindness D-01 exists to fix (inside a worktree the
working-tree glob sees one row):
- `merge-gate.py:134` (`feature_for`) — the very glob T-10 replaces.
- `check-state.sh:118-120` (`_feat_dirs`), `:608`, `:1151` — three separate
  `glob.glob(H, "*", "features", "*", "feature.json")` sites.
- `board_lifecycle.py:476` (`_all_feature_dirs`) — same glob shape, different consumer.
- `layout_migration.py:187-188` — a legacy/migrated glob pair for the same surface.
- `factory_claim.py:150-151` (`_BlockerCache.issue_number`) — reads one feature's
  `feature.json` at a time, cached by `(repo, feature)`, not an aggregate reader.

None of these reads via `git ls-files` (the index), and none persists a branch/issue-keyed
artifact — that combination is what T-09 actually builds and it does not exist anywhere today.
So `feature-index.py` fills a real gap rather than rebuilding one. Flagged as a finding anyway
(low severity) because check-state.sh, board_lifecycle.py and layout_migration.py keep their own
independent working-tree globs after this feature ships, unaffected by T-09/T-10 — a future
reader who assumes "the index is now the one true feature-listing mechanism" would be wrong
about three still-live call sites this plan deliberately does not touch (out of scope, correctly
not touched here — named only so it is not rediscovered as a surprise later).

## Q3 — T-16 Part 2 vs test-hooks-install.py's existing shim pattern

**Genuinely extends, not duplicates.** Read `test-hooks-install.py:397-447` (`_run_merge_and_check`,
the SC-14 missing-delegate case) and its invocation at `:450-504` (`case_sc14_end_to_end_and_red_proof`).
That existing case repoints **the post-merge shim's own delegate** (`bin/post-merge-sweep.sh`) at
a nonexistent path and asserts the merge succeeds, the diagnostic prints, and the worktree
*survives* the merge (i.e., the sweep never ran) — one shim, one delegate, one observable effect.
T-16 Part 2 needs three per-shim cases with three *different* observable effects (post-checkout:
unrepaired new tree; post-rewrite: unequal skip-bit set; post-merge: the T-14 dirty-tree/cleared-
skip-bits shape from the *inner* `worktree-state.py --repair` call now added to
`post-merge-sweep.sh`'s body — a different delegate than the one the existing case exercises).
T-16's own claim that `:286-310`'s exec-bit/`core.hooksPath` assertions are "necessary and not the
missing-delegate case" checks out — those lines assert presence and the bit, never a repointed,
missing delegate. The two new per-shim cases (post-checkout, post-rewrite) are net-new; the
post-merge case tests a delegate the existing SC-14 case does not touch (the inner repair call,
not the shim's own `_sweep` delegate). No lockstep-edit risk here — the two tests assert disjoint
failure shapes.

## Q4 — any `verify:` hand-rolling a check an existing script performs

**No script-level duplication found.** The closest candidates, checked and cleared:
- T-12's `verify` runs `test -x` and `grep -q 'worktree-state.py'` inline — this is a shallow
  sanity gate on T-12's own wiring, not a restatement of a script; T-16 (a later task in the
  same plan, not something "the tree already has") formalizes the deep version. Standard
  gate-then-deepen shape used throughout this plan (T-03 → T-04/T-05/T-06 is the same shape);
  not a reuse violation.
- T-09's `verify` and T-10 Part 3's `test-feature-index-regen.py` both invoke
  `feature-index.py --check` against real data — this is *correct* reuse of the one script in
  two legitimate contexts (post-generation sanity vs. later staleness regression), not two
  hand-rolled spellings of the same check.
- Tree-cleanliness (`git status --porcelain`) and skip-bit reads recur across T-03/T-04/T-07/
  T-13/T-14/T-19, but D-11 assigns exactly these ("cleanliness is `git status --porcelain | wc
  -l`") to the shared `f58_sparse_fixture.py` module as canonical measurement functions every
  task is required to import — this is the plan converging the duplication, not creating it.

## Q5 — does T-02's fixture duplicate an existing test helper

**Partially — one real finding.** `build_owner_root`/`hidden_paths`/`skip_bits`/`manifest` and
the sparse-checkout-cone machinery are genuinely new (no existing fixture builds a sparse
worktree, reads skip-bits, or hashes a manifest as a reusable API). But `add_worktree(root,
feature_id, sparse=True)`'s core mechanic — `git worktree add -q -b <branch> <dest> <ref>`
against `<root>/.claude/worktrees/<segment>/<id>` — is the exact shape already written,
independently, four times:
- `tests/integration/test-hooks-install.py:202-205` (`_add_wt`)
- `tests/integration/test-post-merge-sweep.py:188-191,263` (`_add_wt`, widened; `_bootstrap_repo`)
- `tests/integration/test-worktree-terminal.py:82-85` (`_add_wt`)
- `tests/integration/test-check-state-worktrees.py:54-56` (`_add_wt`, narrower)

T-02 does not import or lift any of these; its intent describes `add_worktree` as new work.

### Finding F-01
- **id / anchor**: T-02 (plan.yaml:353-354), vs. `tests/integration/test-hooks-install.py:202-205`,
  `tests/integration/test-post-merge-sweep.py:188-191`, `tests/integration/test-worktree-terminal.py:82-85`,
  `tests/integration/test-check-state-worktrees.py:54-56`
- **severity**: low
- **summary**: T-02's `add_worktree()` re-derives the `git worktree add` invocation and the
  `.claude/worktrees/<segment>/<id>` destination shape that four other integration test files
  already carry as their own `_add_wt` helper, instead of lifting the existing shape into the
  new shared fixture module.
- **cost**: five near-identical spellings of `git worktree add -q -b <branch> <dest> <ref>` now
  exist in the tree (four pre-existing plus T-02's). None import from another. If `git worktree
  add`'s flags or `dest_for`'s path shape ever changes, five call sites need the same edit; T-02's
  copy is the newest and least likely to be remembered by whoever fixes the other four first,
  since it lives in a helper module (not a `test-*.py` file) nobody browsing `tests/integration/`
  for "worktree fixture" callers would necessarily open.
- **alternative**: have `f58_sparse_fixture.py`'s `add_worktree` call (or be trivially adapted
  from) the existing `_add_wt` shape already proven in `test-post-merge-sweep.py` — that file's
  version is already the most general of the four (it accepts `ref`/`new_branch`). This is a
  same-task fix (T-02 is not yet built) and does not require touching the four existing test
  files, so it carries none of T-02's own scope risk.

## Findings summary

| id | severity | summary | lands_on |
|---|---|---|---|
| F-01 | low | T-02's `add_worktree` re-derives a `git worktree add` fixture helper already written four times in-tree | T-02 |
