# SIMPLIFICATION angle — FEAT-34 worktree act-3 enforced (flag-only)

## Q7 verdict: CONFIRMED

`test-post-merge-sweep.py:13-19`'s module docstring paragraph ("REWORK, T-03/T-04 combined
dispatch: ...") describes only the FIRST rework (the `_resolve_repo_root()` cwd-derivation
defect and its case `(h) case_cwd_outside_repo`, line 607). It says nothing about the SECOND
rework already in the file: `case_linked_worktree_main_checkout()` (line 664, its own inline
comment block at :656-661 labels it "T-03/T-04 SECOND REWORK") plus the `_resolve_main_checkout_root`
split in `post-merge-sweep.sh` (feat_dir must resolve against the main checkout, never the
BIN_DIR-derived root, which can be a linked worktree — the FEAT-35 `Review/pr:null` vs
`Done/pr:812` divergence). I enumerated all ten `case_*` functions (208, 319, 357, 407, 449, 486,
517, 552, 607, 664) against the docstring's claims: nine are accounted for (`case_dry_run_safety`
as "T-03's original", the seven case-list items, and case (h)); `case_linked_worktree_main_checkout`
is not mentioned anywhere in lines 13-60. This is a doc comment that omits a whole test and the
defect it exists to catch — the failure mode the dispatch calls out explicitly ("a doc comment
that lies about what a test covers").

Exact corrected wording — paste as a new paragraph immediately after the existing "REWORK,
T-03/T-04 combined dispatch: ..." paragraph (which ends "...cwd being OUTSIDE it.") and before
"That fix changes what EVERY case in this file must guard against:":

```
SECOND REWORK, T-03/T-04 combined dispatch: `feat_dir` used to be computed from the same
BIN_DIR-derived `root` that locates `gh-sync.py`/`feature-worktree.py` — correct for finding
those scripts, wrong for `feat_dir`, because that root can BE a linked worktree carrying its
own, possibly divergent, copy of `.harness/<repo>/features/<FEAT>/`. `os.path.isdir(feat_dir)`
then found that copy and proceeded with no SKIP at all, so `gh-sync.py ship` read and wrote the
WRONG feature (the FEAT-35 divergence already on record: worktree read `Review / pr:null` while
main read `Done / pr:812`). `post-merge-sweep.sh` now resolves `feat_dir` against a SEPARATE
main-checkout root, never the BIN_DIR-derived one. Case (i), `case_linked_worktree_main_checkout()`,
is the new case that would have caught this: invoked from inside a linked worktree carrying its
own divergent copy of a feature id, it proves the sweep ships and removes against the main
checkout's landed copy and never touches the linked worktree's.
```

- file: `.claude/skills/harness/bin/test-post-merge-sweep.py`
- line range: 13-19 (insertion point after 19, before 21)
- one-line summary: module docstring documents the first rework and case (h) only, omitting the
  second rework and case (i) `case_linked_worktree_main_checkout`, which guards the more serious
  wrong-feature-shipped defect.
- concrete cost: a reader who trusts the docstring to enumerate coverage believes the file's
  worst-case guard is "sweep ran from outside any repo" (case h); they will not know that
  wrong-copy shipping (case i, the FEAT-35 divergence) has a red proof here too, and could
  delete or weaken it as "belt-and-suspenders" without realizing it is the primary regression
  test for that defect class.
- concrete alternative: the paste-ready paragraph above.
- severity: med
- call: backlog row after ship (it is a comment-only correction; nothing here changes behavior
  or an assertion, and this pass is flag-only regardless — `review_sha` is pinned).

## Other SIMPLIFICATION findings on this surface

None that meet the bar.

Checked and explicitly NOT flagging (with reason):

- `check-state.sh:1582` (INV-30) — `str(_doc30.get("status", "")).split()[:1] != ["Done"]`
  looks like an over-elaborate pipeline for a status equality check, and the adjacent comment
  ("the exact string `Done` and nothing else") overclaims precision the `.split()[:1]` form does
  not literally enforce (a hypothetical "Done extra" would also match). But the identical idiom
  already exists, unchanged by this diff, at `check-state.sh:1073` inside the pre-existing INV-28
  block. INV-30 reused an established sibling pattern rather than inventing a new one — that is
  the REUSE angle's territory, and trimming it here would put INV-30 out of step with INV-28 for
  no semantic gain. Not flagged, per the hard constraint on preserving anchoring precedent.
- The INV-29 discriminator (`_repo_level29`, `check-state.sh` inside the new block) — the
  three-way `feature_id is None and (repo is not None or (fleet_path matches))` conjunct looks
  dense, but its own comment states the reason it must key on more than `feature_id`: a
  repository-level failure record and a genuine out-of-segment worktree record are otherwise
  identical on class and `feature_id`. I could not construct a simpler form that keeps that
  disambiguation; not flagged.
- `worktree_terminal.py` and `post-merge-sweep.sh` (the squad-built half) — read in full. Every
  branch and comment I could point at as "redundant" turned out to be explained inline as a fix
  for a measured defect (cwd-derivation, main-checkout-vs-BIN_DIR-root split, self-exclusion by
  realpath prefix). No conjunct or pipeline had a simpler form that preserved what the comment
  says it is pinning.
- `.claude/skills/harness/hooks/post-merge`, `harness-init/SKILL.md`'s `core.hooksPath` section,
  `harness/SKILL.md`'s act-3 text — mechanical/prose changes, no redundant logic or stale
  narration found.

## Settled, not re-litigated

Per dispatch: DEC-174's lane assignment, the plan's approved decisions, `review_sha`, and the two
cited mutation proofs (INV-29 `classify_all`→`classify`; INV-30 status-alone). Weighed both before
concluding the INV-29/INV-30 conjuncts above are load-bearing.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Q7 CONFIRMED — test-post-merge-sweep.py:13-19's docstring omits the second rework and case (i) (linked-worktree wrong-feature-shipped guard); one backlog-row finding, exact wording supplied. No other SIMPLIFICATION findings meet the bar on this surface."
  tests_added: 0
  suite: n/a
  task: none
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-34-worktree-act3-enforced/.harness/harness/features/FEAT-34-worktree-act3-enforced/notes/receipt-harness-backend-dev-simplify-simplification.md
```
