# Receipt — harness-backend-dev — T-08

## Result: BLOCKED — T-08's own `verify:` block is self-contradictory; code and unit tests are correct and complete

## What was built (all three target files, done to spec)

1. **`harness_boundary.py`** (`+worktree_for_feature`/`+AmbiguousWorktree`, placed after
   `linked_worktrees`): enumerates `linked_worktrees(owner_root)`, keeps every checkout whose
   basename EQUALS `feature_id` or satisfies `feature_id.startswith(basename + "-")`; 0 → `None`,
   1 → the realpath, ≥2 → raises `AmbiguousWorktree` naming every candidate basename sorted.
   Docstring carries both required reasons verbatim-in-spirit (feature-worktree.py:236-248 citation
   and the 0.371ms/38ms cost citation).
2. **`inflight_registry.py`** — `feature_root`'s inline `os.path.basename(worktree) == feature`
   loop (was `:260-268`) replaced with a call through `harness_boundary.worktree_for_feature`;
   signature, return type, and total fallback (`Exception` or `None` → `owner_root`) unchanged;
   no other function touched.
3. **`test-harness-boundary.py`** — added a `make_worktree(mod, owner_root, name)` fixture (the
   two-sided gitdir pointer pair, following the shape used by `test-check-domain.py`'s `wt()` and
   `test-bash-write-guard.py`'s equivalent — this file itself had none to reuse, so this is the
   one gitdir-writer added here) and 6 new cases in `case_worktree_for_feature`: exact match,
   short-form prefix, unrelated id → `None`, hyphen-boundary non-match (`FEAT-XY` vs `FEAT-X`),
   no-`.git/worktrees` → `None`/no-raise, two-candidate → `AmbiguousWorktree` naming both.

## TDD evidence

- RED (pre-implementation, unmodified `harness_boundary.py`): `FAIL case_worktree_for_feature_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'worktree_for_feature'")` — the missing seam, not a fixture bug.
- GREEN: `python3 .claude/skills/harness/bin/test-harness-boundary.py` → `ALL PASS`, exit 0 (all 17 cases, the 5 pre-existing plus the new 6 counted individually — see full run below).
- Invariance: `test-inflight-registry.py` before the cutover: `111/111 checks passed`, exit 0. After the cutover: `111/111 checks passed`, exit 0. Identical, unmodified.

## The blocking defect: T-08's third `verify:` block cannot pass under its own stated algorithm

Ran the literal heredoc verbatim from the worktree root. It fails at:

```
assert ir.feature_root(d, 'FEAT-Y-other') == d, 'no worktree must fall back to owner_root'
AssertionError: no worktree must fall back to owner_root
```

This is not an implementation bug — it is a mathematical consequence of the verify script's own
fixture sequence combined with the algorithm the intent itself specifies (`feature_id.startswith(
basename + "-")`). Proof, run directly against my implementation:

```
FEAT-X-thing -> candidates: ['FEAT', 'FEAT-X']
FEAT-Y-other -> candidates: ['FEAT']
```

The script creates worktrees `FEAT-X` and (later) bare `FEAT`, then asserts `'FEAT-X-thing'`
is ambiguous (matches both `FEAT-X` and `FEAT` — correct, and it does) **and**, in the very next
line, asserts `'FEAT-Y-other'` has no worktree at all and must fall back to `owner_root`. But
`'FEAT-Y-other'` also starts with `"FEAT-"`, so it uniquely matches the same bare `FEAT` worktree
the previous assertion relies on for ambiguity — it is never candidate-less once `FEAT` exists.
Any implementation of the stated rule that makes the first assertion true (ambiguity via a bare
`FEAT` worktree) necessarily makes the second assertion false, and vice versa: no rule satisfying
"equal, or prefix + hyphen" can distinguish `FEAT-Y-other` from `FEAT-X-thing` once a bare `FEAT`
worktree exists in the same set, because both ids share the `"FEAT-"` prefix. The explicit
"never guess, never prefer the longest match" instruction rules out breaking the tie by any other
heuristic (e.g. discarding single-token basenames or preferring the more specific candidate),
which would also have been undocumented, invented behavior — a spec violation on its own.

`plan.yaml` T-08's `verify:` block (`:1174-1207`) is what I was dispatched to satisfy exactly and
told not to modify (`plan.yaml` is out of scope for me). The literal string I ran matches the
dispatch's quoted block and `plan.yaml`'s block scalar byte-for-byte — this is not a
transcription mismatch, it is a defect intrinsic to the acceptance script's own fixture choice
(reusing a bare `FEAT` worktree for the ambiguity case collides with the unrelated-id case that
runs after it). A minimal fix at the plan level would rename the ambiguity worktree to something
that does not share a prefix with `FEAT-Y-other` (e.g. `FEAT-Z` instead of bare `FEAT`), or change
the unrelated id to one that does not start with `FEAT-` at all (e.g. `OTHER-thing`) — either
change is a `plan.yaml` edit, outside my write domain.

## Full first two verify components — both green, quoted

```
$ python3 .claude/skills/harness/bin/test-harness-boundary.py
... (11 pre-existing PASS lines) ...
PASS worktree_for_feature_exact_basename_match
PASS worktree_for_feature_short_form_prefix_match
PASS worktree_for_feature_unrelated_id_returns_none
PASS worktree_for_feature_hyphen_boundary_not_crossed
PASS worktree_for_feature_two_candidates_raises_ambiguous
PASS worktree_for_feature_no_worktrees_dir_returns_none

ALL PASS
$ echo $? -> 0

$ python3 .claude/skills/harness/bin/test-inflight-registry.py   # BEFORE the cutover
... PASS - 111/111 checks passed
$ echo $? -> 0

$ python3 .claude/skills/harness/bin/test-inflight-registry.py   # AFTER the cutover
... PASS - 111/111 checks passed
$ echo $? -> 0
```

## `git status --porcelain` (worktree)

```
 M .claude/skills/harness/bin/harness_boundary.py
 M .claude/skills/harness/bin/inflight_registry.py
 M .claude/skills/harness/bin/test-harness-boundary.py
 M .claude/skills/harness/bin/test-validate-digest.py
 M .claude/skills/harness/bin/validate-digest.py
```

Exactly my three target files plus the two files already dirty and owned by the main session.
Nothing committed.

## Recommendation to the lead/PM (corrected in cycle 2 — the FEAT-Z suggestion below was wrong)

Amend T-08's third `verify:` block in `plan.yaml` (this is a `plan.yaml` edit, not mine to make):
the ambiguity setup (`wt('FEAT')` alongside `wt('FEAT-X')`) is fine as-is — the defect is the
FINAL assertion's id. Renaming the ambiguity worktree to `FEAT-Z` would not fix anything: `FEAT-Z`
is not a prefix of `FEAT-X-thing`, so it would silently drop out of the ambiguity candidate set and
break the very assertion it exists to support. The only minimal fix is changing the id used in the
final "no worktree, falls back to owner_root" assertion away from `FEAT-Y-other` — any id sharing
the `FEAT` bare-worktree's prefix family will always resolve to that worktree once it exists — to
one outside every worktree basename's prefix family, e.g. `'OTHER-thing'`:
`ir.feature_root(d, 'OTHER-thing') == d`. Once that one id is changed the block should pass
unmodified against the implementation delivered here; no further source change is anticipated.

## Cycle 2 — `worktree_for_feature_hyphen_boundary_not_crossed` made discriminating

**Finding accepted as stated:** the cycle-1 case created `FEAT-XY` alongside `FEAT-X` and asserted
`worktree_for_feature(tmp, "FEAT-X") == short`. Under the exact boundary-less bug the case is named
for (`feature_id.startswith(basename)`, no `"-"`), `"FEAT-X".startswith("FEAT-XY")` is False, so
`FEAT-XY` was never even a candidate — the assertion was green under the bug it claims to catch.

**Fix applied** (`test-harness-boundary.py`, inside `case_worktree_for_feature`, same case name,
no new helper, `make_worktree` reused): the case now looks the LONGER id up against the SHORTER
basename — `mod.worktree_for_feature(tmp, "FEAT-XY") is None` — with `FEAT-X` as the only worktree.
Correct rule: `"FEAT-XY" == "FEAT-X"` is False and `"FEAT-XY".startswith("FEAT-X-")` is False, so
`None`. Boundary-less bug: `"FEAT-XY".startswith("FEAT-X")` is True, so it would wrongly return
`FEAT-X`'s checkout. The two rules now diverge on this input.

**Mutation proof, quoted verbatim.** `harness_boundary.py:219` mutated from
`feature_id.startswith(os.path.basename(checkout) + "-")` to
`feature_id.startswith(os.path.basename(checkout))` (the `"-"` dropped):

```
$ python3 .claude/skills/harness/bin/test-harness-boundary.py
... (14 other PASS lines, unchanged) ...
FAIL worktree_for_feature_hyphen_boundary_not_crossed a FEAT-X worktree must not match a FEAT-XY lookup
PASS worktree_for_feature_two_candidates_raises_ambiguous
PASS worktree_for_feature_no_worktrees_dir_returns_none

1 FAILURE(S): ['worktree_for_feature_hyphen_boundary_not_crossed']
$ echo $? -> 1
```

Exactly and only the target case reddened, naming the wrong-value symptom. Reverted
`harness_boundary.py:219` to `feature_id.startswith(os.path.basename(checkout) + "-")` verbatim.
Hash before mutation: `e6bce1aabe41fb7c08d31dd9b1d1b560345690c7913dd9862d5d37515cd7b817`. Hash
after revert: identical (`e6bce1aabe41fb7c08d31dd9b1d1b560345690c7913dd9862d5d37515cd7b817`) —
byte-identical to the end of cycle 1. `git diff --stat -- .claude/skills/harness/bin/harness_boundary.py`
still reports `1 file changed, 47 insertions(+)`, matching cycle 1's line count (no net change from
the scratch mutation).

```
$ python3 .claude/skills/harness/bin/test-harness-boundary.py   # after revert
... (all 17 case names) ...
ALL PASS
$ echo $? -> 0

$ python3 .claude/skills/harness/bin/test-inflight-registry.py   # after revert, unmodified
... PASS - 111/111 checks passed
$ echo $? -> 0
```

`git status --porcelain` (worktree): same five `M` entries as cycle 1
(`harness_boundary.py`, `inflight_registry.py`, `test-harness-boundary.py`,
`test-validate-digest.py`, `validate-digest.py`), plus this receipt itself as `??` (an untracked
notes artifact, not part of the reviewed diff). Nothing committed, nothing else touched.

The plan-level `verify:` third-component defect from cycle 1 stands unchanged and is not addressed
here per instruction — reported again below as an open question, not a BLOCKED verdict.
