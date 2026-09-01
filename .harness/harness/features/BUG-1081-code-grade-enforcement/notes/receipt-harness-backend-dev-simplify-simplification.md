# SIMPLIFICATION angle — BUG-1081 code-grade-enforcement

**Verdict: one real, appliable finding. Everything else read clean.**

Scope read: `code_grade.py`'s new `classify`/`_classify_record`/`_blocks`/`_severity`/
`_is_test_path`/`_patterns`/`TestKindsError` seam; `code-grade.py`'s consumption of it;
`validate-digest.py`'s seven new helpers (`_repo_root_for_feature`, `_git_line_or_none`,
`_default_branch_or_none`, `_merge_base_or_none`, `_canonical_review_range`,
`_load_test_kinds`, `_classify_canonical_range`, `_mechanical_code_grade`,
`code_grade_enforcement_error`) and `validate()`'s call site; `harness-code-review/SKILL.md`'s
new "enum is an audit claim" section; the test files' new BUG-1081 sections.

## Finding 1 — APPLIABLE

**File:** `.claude/skills/harness/bin/validate-digest.py:776` (`code_grade_enforcement_error`,
lines 761–785)

**Summary:** `code_grade_enforcement_error` re-validates the digest's `reviewed` field shape
and resolvability by calling `reviewed_python_change(root, reviewed)` and discarding its
answer (`_discarded`) — but `code_grade_bound_to_review` (`validate-digest.py:1031`) already
performs the identical validation, with the identical error strings, over the identical
`(root, reviewed)`, unconditionally, immediately before this function is ever called
(`validate-digest.py:1309` runs before the `if code_grade in CODE_GRADE_VALUES` block at
line 1314 that reaches this function).

**Cost:** Two things, to whoever reads or maintains this path. (1) `reviewed_python_change`
doesn't just parse and resolve — it also runs a real `git diff --name-only` over the
resolved range to answer "did any `.py` path change", and that answer is thrown away
(`_discarded`); this now runs on *every* `harness-code-reviewer` digest of any `code_grade`
value (before BUG-1081 the same call existed but only fired for `code_grade == "n_a"`), so
the change measurably widens a wasted-diff pattern from one code_grade value to four.
(2) The function's own docstring claims one responsibility — "check a code reviewer's
`code_grade` claim against the result this repository computes" — but the code silently
carries a second, undocumented one (shape re-validation) that duplicates a sibling function's
job under a different name and a different, heavier mechanism. A future reader fixing a
`reviewed`-shape bug has two call sites to find and reconcile instead of one.

**Alternative:** Delete lines 775–778 (`root = _repo_root_for_feature(feature_dir)` stays,
needed by `_mechanical_code_grade`; drop the `_discarded, shape_error = ...` block). The
`reviewed` field's shape and resolvability are already asserted by
`code_grade_bound_to_review`'s `binding_error`, appended to `err` at `validate-digest.py:1313`
in the same `validate()` call — a malformed `reviewed` still surfaces the identical message
text, just from the one function whose docstring already claims that job. Verified no test
asserts the discarded return specifically (`grep` for `reviewed_python_change`/`_discarded`
in `test-validate-digest.py` returns nothing; existing tests only substring-match on the
shared error text, which is unaffected).

**Nature:** `bug` (dead/wasteful work silently added scope with no test coverage forcing it) —
arguably `chore` if you consider it pre-existing style rather than a defect; tagging `bug`
because the change is what widened it from one code_grade value to all four.

**Not appliable as a weaker-assertion concern:** this is not "the same fact asserted twice"
in the sense the pass's ceiling excludes (that clause protects assertions the qa gate
counted as coverage). This is dead, discarded computation with no assertion attached to it
at all — removing it drops zero checks and zero coverage.

## Checked and clean

- `code_grade.py`'s new `classify`/`_classify_record`/`_blocks`/`_severity`/`_is_test_path`/
  `_patterns` seam (lines 431–507): straight relocation from the CLI, no added complexity.
  `_blocks`/`_severity`/`classify`'s three-way precedence (`fail` > `grade_2` > `pass`) is a
  minimal, non-redundant `if`/`elif`/`else`.
- `code-grade.py`: no leftover comments describing rules that moved out; no dead branches;
  `_paths_report`/`_diff_report` are a clean pass-through to `code_grade.classify`.
- `validate-digest.py`'s other six new helpers (`_repo_root_for_feature`, `_git_line_or_none`,
  `_default_branch_or_none`, `_merge_base_or_none`, `_canonical_review_range`,
  `_load_test_kinds`, `_classify_canonical_range`): each is a genuine single-purpose seam
  (not a shallow pass-through — each adds its own None/error mapping over the git or json
  call it wraps), and `_canonical_review_range`'s four fail-closed branches each name a
  distinct, non-overlapping repair (D-05, not re-litigated).
- `harness-code-review/SKILL.md`'s new section: no dead references to the pre-move shape
  (still correctly describes `validate-digest.py` recomputing over the canonical range).
- Test files' new sections (`test-validate-digest.py`'s ~400-line BUG-1081 block,
  `test-code-grade.py`, `test-code-grade-cli.py`): the RED-run comment block, fixture
  builders, and per-case docstrings are load-bearing evidence of the measured pre-fix defect
  (this repo's established convention — see `_body_hashes`/SEC-01-style commentary
  elsewhere), not narration to trim.

## Not flagged, considered and rejected

- `_mechanical_code_grade` formats `(base_oid, head_oid)` into a `"oid..oid"` string and
  passes it to `reviewed_python_change`, which re-splits and re-resolves both (two more
  `git rev-parse` calls on already-known OIDs). Real, but this is reuse of a shared
  parser/differ to avoid a second diff-and-check implementation — the cost is a couple of
  cheap subprocess spawns, not an added branch or reader-facing complexity. Judged an
  efficiency question, not a simplification one; left to that angle.

```yaml
VERDICT: PASS
DIGEST:
  headline: one appliable finding — code_grade_enforcement_error redundantly re-validates and discards a reviewed-field diff already validated by code_grade_bound_to_review
  tests_added: 0
  suite: n/a
  task: none
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1081-code-grade-enforcement/notes/receipt-harness-backend-dev-simplify-simplification.md
  expertise_update: []
artifact: .harness/harness/features/BUG-1081-code-grade-enforcement/notes/receipt-harness-backend-dev-simplify-simplification.md
```
