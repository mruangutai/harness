# SIMPLIFICATION angle — BUG-1286-test-tree-enforcement (build, cycle 1)

## BLUF

Three findings. Two are verified-dead logic inside the case-11 hygiene certifier
(`tests/unit/test-suite-layout.py`) — a tautological conjunct and an unreachable
disjunct, both confirmed by exhaustive small-alphabet enumeration, not by
inspection alone. Given settled item 5 protects case 11 outright and this pass has
a one-fix ceiling, I label both `backlog` rather than spend the pass's one apply
slot on zero-behavior-change cleanup inside the single most heavily-reviewed
function in the feature (10 panel cycles per plan.yaml `panel.last_run.cycle`).
The third finding — a narrative comment in the same file — is a clean,
zero-risk `apply-candidate`. Production `suite_layout.py` itself has no redundant
conjuncts or narrative comments; it reads clean.

## Findings

### F-1 — backlog — tautological conjunct in `_literal_key_present`

- **File/line:** `tests/unit/test-suite-layout.py:414`
- **Summary:** `and not any(ch in trailing for ch in "*?[")` can never be `False`.
- **Concrete cost:** `trailing = core[last_wildcard + 1:]` where `last_wildcard`
  is defined one line above as the *maximum* index of any wildcard character in
  `core`. By construction, no character after that index can be a wildcard, so
  the conjunct is a tautology. Verified by enumerating every string up to length
  6 over the alphabet `{t,e,s,*,?,[,],.,p,y}` (10^6 combinations) through the
  real slicing logic: zero produced a `trailing` containing a wildcard char. A
  future auditor of this anchoring-sensitive helper (case 11's hygiene half,
  the subject of D-01's longest decision text) will re-derive this same proof
  from scratch, since nothing marks the conjunct as intentionally defensive.
- **Alternative:** drop the conjunct, leaving
  `if trailing.startswith(".") and any(trailing.endswith(ext) for ext in suite_layout.SOURCE_EXTENSIONS): return True`.
  Verified behavior-preserving — this only removes a check that already always
  passes, so it changes no reachable input's classification, and case 11's
  assertions, positive control and INAPPLICABLE branch are untouched.
- **Why backlog and not apply:** settled item 5 protects case 11 outright, and
  this conjunct lives inside its hygiene-half machinery. The gain here is a few
  seconds spared for a rare future reader; the pass has a one-fix ceiling on the
  single most panel-scrutinized function in the change. Not worth spending the
  slot on a cosmetic no-op inside code this sensitive.

### F-2 — backlog — unreachable `".."` disjunct in `_is_inside_tests`

- **File/line:** `tests/unit/test-suite-layout.py:399`
- **Summary:** `normalized in (".", "..")` — the `".."` alternative can never
  match, because the function already rejects any pattern containing a literal
  `".."` segment three lines earlier.
- **Concrete cost:** line 390-391 (`if ".." in segments: return False`) checks
  the pattern's *full* segment list, and `prefix_segments` (line 392-396) is
  built only by taking a prefix of that same list up to the first wildcard
  segment — so `prefix_segments` can never contain a literal `".."` either.
  `posixpath.normpath` cannot synthesize a `".."` component from segments that
  contain no literal `".."` (verified by enumerating every 1-3 segment pattern
  over `{a,b,.,tests,*}` with no literal `".."` segment: none normalized to
  `".."`). Same cost class as F-1: a rare future reader re-proves this by hand.
- **Alternative:** `normalized in (".", "..")` -> `normalized == "."`, with a
  one-line comment: "the segments-level check above already excludes any `..`
  component, so normpath can never produce one here." Verified
  behavior-preserving for the same reason as F-1.
- **Why backlog and not apply:** identical reasoning to F-1 — this is inside
  `_is_inside_tests`, the other half of case 11's certifier, protected by the
  same settled item and the same one-fix ceiling. Two zero-value applies inside
  the same guarded function in one pass is exactly the trap this dispatch warns
  against, even when each individually is provably inert.

### F-3 — apply-candidate — narrative comment in Case 5

- **File/line:** `tests/unit/test-suite-layout.py:251`
- **Summary:** `# Case 5: the existing non-git legal_tree() is unaffected by
  the new clause.` narrates the change ("the new clause") instead of stating
  the present fact the case verifies — exactly the pattern this angle's
  dispatch calls out by name.
- **Concrete cost:** six months from now "the new clause" has no referent; a
  reader has to diff against history (or re-read the whole file) to learn which
  clause is meant, when the present fact — that the tracked-outside-tests
  clause never fires on a tree with no `.git` — is stateable in the same
  sentence.
- **Alternative:** `# Case 5: a non-git tree is unaffected by the
  tracked-outside-tests clause, which never fires without a .git index.`
  Comment-only change; no assertion, fixture or behavior touched.

## Candidates considered and dropped

- **`_disposition` in `tests/manual/suite-census.py` re-spells part of
  `is_test_shaped`'s restricted/extension logic inline** (lines 87-94). This is
  a same-fact-in-two-places question, which is the REUSE angle's territory
  (constants/predicate restated where an importable one exists), not mine —
  dropped from this angle rather than duplicated across readers.
- **Collapsing `violations()`'s four sequential `continue` guards
  (lines 140-147 of `suite_layout.py`) into one compound `if`.** Dropped: each
  guard (`tests/` prefix, planted-by-bin-clause, documented-exception,
  not-test-shaped) is independently exercised by a distinct unit case (cases
  1/2, 4/9, 6, 8/10), and this exact ordering is D-03's toplevel/self-ownership
  precondition made concrete. A compound `if` would read no more simply and
  would risk an operator-precedence slip in code the plan spent real cycles
  anchoring — the trap this dispatch names explicitly.
- **Collapsing `is_test_shaped`'s agnostic-then-restricted two-step into one
  boolean expression.** Dropped outright: D-01's entire point is that the
  extension restriction applies to `RESTRICTED_NAME_PATTERNS` only, and any
  single-expression collapse risks applying it to the agnostic group too. This
  *is* the anchoring the dispatch warns not to trim.
- **`tests/manual/suite-census.py`'s stale module docstring** (`"""One-shot
  and review-time census tools for FEAT-47."""`, line 2) predates this
  feature's diff (confirmed via `git show 5f76d6b1` — the docstring line is
  untouched context, not an added line) and is out of this feature's scope per
  the dispatch's non-goals framing of the code surface as "what each was
  required to do" for BUG-1286. Not flagged.
- Read `.claude/skills/harness/bin/suite_layout.py` end to end for redundant
  conjuncts and narrative comments: none found. Its comments state present
  facts ("the sole implementation of the vocabulary…") rather than narrating
  the change, and every compound boolean expression's conjuncts each carry
  distinct, independently-tested work.

## Verification note

F-1 and F-2's "always true / never reached" claims were confirmed by running
the real slicing/normalization code over exhaustive small-alphabet corpora
(shell + Python, not committed — scratch only), not by inspection alone, per
this angle's governing limit that a finding is not ready until the alternative
is shown to keep the anchoring the original code fought for.
