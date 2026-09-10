# Receipt — harness-dev-ops — FEAT-58 arch-eng (Q4 + Q5b)

## Q4 — RULING: derive the include-list at creation time; do not enumerate it in source

Enumeration is what the probe used and it is already measurably wrong. `git ls-tree --name-only
HEAD` at this worktree's HEAD returns 12 top-level entries: `.agents .claude .github .gitignore
.harness .omp AGENTS.md CLAUDE.md README.md council docs tests`. The design comment's ledger list
— `.claude tests docs council .harness/{expertise,notes,logs,factory} .harness/harness/docs` +
`features/<ID>` — omits `.agents`, `.github`, `.gitignore`, `.omp`, `AGENTS.md`, `CLAUDE.md`,
`README.md`, and (one level down, `git ls-tree --name-only HEAD -- .harness/`, 9 entries) omits
`.harness/README.md`, `.harness/glossary.md`, `.harness/harness.json`, `.harness/team-config.yaml`,
`.harness/harness/expertise`. `.agents` is not filler: `git ls-tree HEAD -- .agents/` shows it
holds exactly one entry, a symlink `.agents/skills -> ../.claude/skills` (mode 120000). Every
dispatch in this run — this one included, `.agents/skills/harness/bin/inflight_registry.py` — reads
through that symlink. A worktree built from the enumerated list is missing the very path this
skill's own commands use. That is not a hypothetical drift; it is drift measured on today's tree.

**Is a derived list expressible in cone mode?** Yes, without non-cone patterns, because the shape
needed is exactly cone mode's native case: "recurse fully into a listed leaf, list-only at its
ancestors, everything not listed is excluded." Derive it as: (1) `git ls-tree --name-only HEAD` for
the top level — include every entry whole *except* `.harness`; (2) `git ls-tree --name-only HEAD --
.harness/` — include every entry whole *except* the repo-segment(s) that hold `features/`
(today, only `.harness/harness`); (3) for each such segment, include its non-`features` children
whole (`docs`, `expertise`) and `features/<ACTIVE_ID>` alone. Step 3 is precisely "everything under
`features/` except one child, inverted" — cone mode's ordinary leaf-recursive-include-with-siblings-
excluded behaviour, no `!`-negation or non-cone pattern needed. **Rejected alternative:** a literal
path list in source (what the probe used). It requires a human edit on every new top-level
directory, and the `.agents` gap above shows that edit is already being missed today, before any
code exists.

**Failure mode of the rejected option (enumerated, unmaintained):** a new top-level path lands
and nobody adds it to the list. A worktree built from the stale list **silently excludes it** —
`git sparse-checkout set` does not know or care that the repository grew a directory it was never
told about, so nothing is red at creation time. Whether anything fails downstream depends entirely
on whether some later step happens to touch the missing path: a script that imports through it
(e.g. `.agents/skills/...`) fails loud but *late and mis-attributed* (`ImportError` / `No such file
or directory`, read as "the tool is broken," not "the worktree is incomplete"); a path nothing ever
touches (e.g. a doc file) is missing forever with no signal at all. This is strictly worse than the
derived list's failure mode, whose only way to go wrong is the deny-rule itself being wrong (e.g. a
second repo segment growing a non-`features` sibling it forgot to name) — a much smaller, reviewable
surface than "every top-level directory, forever."

**Degradation when derivation resolves an empty or wrong set — measured, not inferred.** In a
throwaway scratch repo (`mktemp -d`, `git init`, three files, one commit — not this repository, no
worktree touched, deleted immediately after):
- `git sparse-checkout set` with **no arguments** → **exit 0**, working tree reduced to only
  root-level loose files.
- `git sparse-checkout set does-not-exist` (a pattern matching **nothing**) → **exit 0**, same
  result, and `git sparse-checkout list` cheerfully echoes back `does-not-exist` as if it worked.
Git sparse-checkout has **no error path for "included nothing" or "included a name that doesn't
exist."** It is a silent success indistinguishable, from the tool's own output, from a correct
narrow checkout. This is the same shape as the fail-open already reproduced against
`check-state.sh` (1 of 88, exit 0) — the corpus sweep and the include-list share one property:
**git will not tell you when the set is wrong; only a positive-control check against `git ls-tree`
can.**

**What makes each of the two broken states loud:** neither a worktree that silently materialises
nothing needed, nor one that silently materialises everything, can be told apart by looking at
`git sparse-checkout list`'s own success/exit code — both look identical to a correct one from
git's point of view. The only thing that makes either loud is a check that does **not** trust the
list it just applied: after `git sparse-checkout set <derived-list>` inside `feature-worktree.py
create`, assert that a small, named set of required paths exists on disk (`.agents/skills`,
`.claude/skills`, `.harness/harness/features/<ID>`) and refuse (non-zero, deleting the half-built
worktree) if any is absent — mirroring the pattern this repository already uses for the identical
problem: `tests.yml`'s Repository-state gate (`:296-299`) derives its expected feature count from
`git ls-files`, never from the checker being gated, for exactly the reason that a checker cannot be
its own positive control. **Yes, this needs a gate of its own**, and it is a one-time,
creation-time assertion inside `create` (not a standing sweep) — the instrument is the required-path
existence check above; nothing in git itself can serve as that instrument, since both `set` calls
above returned 0.

## Q5b — worktree-creation half of the design comment

**Migration order (check dirty, then sparsify) is sound for the migration event itself, and it is
sound *because* of the order, not despite the SKIP_WORKTREE fact.** The measured fact — sparse
`git status --porcelain` reads clean — is a property of an *already-sparse* worktree: SKIP_WORKTREE
tells git to stop comparing those paths at all, so a genuine on-disk change to a since-excluded path
would never surface again. Checking dirty **before** `git sparse-checkout set` runs the check while
the worktree is still fully materialised and ordinary — every tracked path, including the ones about
to be excluded, is still compared normally, so the one-time migration's dirty check is not weakened
by the fact it is measured against. The residual is what happens **after**: `cmd_remove`'s dirty
gate (`feature-worktree.py:218-223`, unchanged by this ledger) calls the identical `git status
--porcelain` on every future `remove` of a now-permanently-sparse worktree, and from that point on it
is blind to any tracked path outside the cone by the same SKIP_WORKTREE mechanism the migration step
correctly avoided once. By construction (DEC-208/DEC-218) nothing legitimate ever writes outside a
worktree's own registered feature, so there should be nothing there to go undetected — but "should
never write there" is exactly the invariant a bug would violate, and this dirty check is no longer
capable of catching that violation once migration lands. Flag, not blocking: `remove`'s dirty check
needs a second opinion (e.g. `git clean -ndx` scoped to the cone, or a corpus-root check) if it is
meant to remain a real backstop post-migration.

**CI identity claim — verified by code, not by running CI.** `.github/workflows/tests.yml:50` uses
`actions/checkout@v4` with no sparse-checkout step and no linked worktrees anywhere in the job — a
plain, single checkout. `harness_boundary.worktree_owner()` (`:715-758`) finds a `.git`
**directory** (not a linked-worktree `.git` **file**) at that checkout's root and returns
`(cur, cur, True)` — checkout_dir and owner_root are the same path. A `corpus_root()` built on
`worktree_owner(cwd).owner_root or resolve_root(...)`, per the design comment's own formula,
therefore resolves to `cwd` in CI as a direct, already-shipped corollary of that existing branch —
true today by code reading, but **not covered by any existing automated test**, since `corpus_root()`
does not exist yet. Recommend the plan add one case asserting this composition against a plain
(non-worktree) checkout, rather than relying on the inference in this note.

**Nothing in the creation/migration half should be dropped**, but the ledger is incomplete as
written: it does not mention the creation-time positive-control check Q4 requires, and the migration
row does not mention `cmd_remove`'s post-migration dirty-check gap above. Both are additions to the
same two rows, not new rows.

## Measurement modes, stated per claim
- `git ls-tree --name-only HEAD [-- <path>]` — read surface / structural enumeration (used for
  every "N entries" count above).
- Scratch-repo `git sparse-checkout set` exit codes and `find … -type f` — behavioural probe, run
  in a throwaway `mktemp -d` repo, deleted immediately after; not run against this repository or any
  worktree.
- No `du`, no `df`, no worktree created or removed in this repository.
