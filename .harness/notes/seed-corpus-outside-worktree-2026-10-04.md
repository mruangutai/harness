# Seed: the feature corpus outside the worktree, re-planned from FEAT-58 (2026-10-04)

Source issue: #1559. Predecessor: `FEAT-58-corpus-outside-worktree`, abandoned 2026-10-04 (parent
#1641).

**Where FEAT-58's record lives.** Its BRIEF, signed plan, operator answers c1-c9 and receipts are
not on `main`; they are archived on branch `origin/feat/FEAT-58-corpus-outside-worktree` at
`f57e41dd`, under `.harness/harness/features/FEAT-58-corpus-outside-worktree/`. That branch is
never merged. Merging it would land 10 open high panel findings and an unbounded fix loop that
INV-32 and the cycle check refuse. Its DoD note is on `main` at
`.harness/notes/dod-worktree-corpus-2026-09-10.md`.

This note is the seed for the feature that replaces FEAT-58. It is research input for the BRIEF,
not a decision record.

## The binding rule (operator ruling, 2026-09-09, unchanged)

> The feature corpus is never materialised inside a worktree. It remains fully available to the
> active feature from outside the worktree.

Both halves bind. Making the copy cheaper (clone-on-write) does not satisfy "never materialised".

## Why FEAT-58 was abandoned rather than amended

Its plan was signed on 2026-09-10 and never built. By 2026-10-04 its branch was 534 commits behind
`main`:

- **File references.** `check-state.sh`, which the plan cites 86 times, is now the `check_state/`
  package. `check-domain`, `branch-create-gate`, `post-merge-sweep` and `run-unit-tests` are Python
  now.
- **Model of the system.** The plan has no fleet planning worktrees (#2058), no validator pin
  checkouts (#1994), and no hook-side path rooting (BUG-1016).
- **Budget.** It had 1 cycle left of 10.

`plan-merge.py check` reported 41 of 43 anchors resolved. That number is not evidence the plan is
current: `check` accepts any missing file whose directory exists as a file the plan creates.

## Decision audit against `main` at efc524f5

| | Decisions | Verdict |
|---|---|---|
| Carry over as written | D-04, D-05, D-06, D-11, D-13, D-14, D-15, D-16, D-17 | Premises re-checked and still true. D-06: FEAT-02 / FEAT-03-subissue-mirror is still the only branch collision. D-14: #1638 is still open. |
| Carry over; re-anchor files | D-01, D-02, D-03, D-07, D-10, D-12 | D-01: `merge-gate.py:197` still searches only `ROOT` for records. D-02: `linked_worktrees()` still lists only an owner root's `.git/worktrees`, and `check-domain.py:2693` and `validate-digest.py:752` call it with a root that can be a worktree. D-03: only `post-merge` exists, and the sweep is `post-merge-sweep.py`. D-12 targets `check_state/`. |
| Re-decide | D-08, D-09 | See below. |

### D-09: the read path

FEAT-58 chose a symlink `.harness/corpus` pointing at `<owner root>/.harness/harness/features`, on
the premise that "no anchor concept" existed. Two things have changed:

1. **Fleet records.** Fleet repositories keep their records under `.harness/<segment>/features`,
   for example `.harness/kaya/features`. The symlink reaches harness records only.
2. **An anchor now exists.** DEC-214 added `HARNESS_CONTROL_PLANE_ROOT`, which is injected into
   every agent and already used to read decisions, skills and expertise from the main checkout.

The candidates are therefore:

- the symlink;
- the existing control-plane anchor;
- reading through git (`git show <ref>:<path>`, the question 3 in #1559).

Both the symlink and the anchor read a **mutable working tree**. Only git reads a fixed commit.

### D-08: the sparse checkout list

FEAT-58's derivation drops `.harness/<repo>/features` for one segment and adds back the active
feature, whose id is the worktree's directory name.

Under ruling A (#2056), a fleet feature's planning worktree sits under the `harness` segment while
its active feature lives at `.harness/<fleet segment>/features/<id>`. The derivation has to:

- drop every `.harness/*/features`;
- re-add the active feature from whichever segment holds it.

The derived, directories-only approach still holds.

## Scope FEAT-58 never saw

1. **Validator pin checkouts** (`.claude/worktrees/.pins/`, #1994). Each QA or reviewer run checks
   out the full tree at the review commit. Decide whether a pin applies the sparse list or is
   excluded from it deliberately.
2. **Fleet planning worktrees** (#2058). `feature-worktree.py create --repo <owner>/<repo>` now cuts
   a harness planning worktree beside the code worktree.
3. **BUG-1016 path rooting.** The OMP hook rewrites relative tool paths into the feature worktree.
   Reads through the corpus path, and refusals of writes to it, must be proven on that path.
4. **`gh-sync` loader** (#2060). It drops non-`T-NN` task ids. FEAT-58's `N-NN` ids lost their
   issue map, so `abandon` could not close the sub-issues.

## Measured cost at seed time (2026-10-04)

These are logical sizes from `du`. Measure real savings with a `df` delta, as #1559 warns.

- 8 harness worktrees, 465 MB in total.
- Each worktree is 48–61 MB, of which `.harness/` is 41–51 MB.
