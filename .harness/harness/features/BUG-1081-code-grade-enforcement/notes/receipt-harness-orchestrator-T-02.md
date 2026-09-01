# Receipt — T-02, Recompute code grade in digest validation

**BLUF.** `validate-digest.py` now COMPUTES the code-grade result for every ordinary
code review over a range the repository derives, and rejects a `harness-code-reviewer`
digest whose `code_grade` disagrees with it. Executed directly by the orchestrator under
DEC-174 (the enforcement layer may not be changed through the enforcement path being
changed). Both suites green; four mutations proven to red the new assertions.

## What changed

`.claude/skills/harness/bin/validate-digest.py`

- `_repo_root_for_feature(feature_dir)` — ONE repository basis. Every default-branch
  lookup, merge base, commit resolution, canonical diff and `gated_set()` call is now
  addressed at the checkout that owns the feature directory (`git -C` /
  `commit_oid(root, ...)`). `resolve_reviewed_commit`, `reviewed_python_change`,
  `_default_branch_or_none` and `_merge_base_or_none` all take that root; their
  docstrings no longer describe the superseded cwd basis, and `_current_branch_or_none`
  routes through the same helper instead of re-deriving the path inline.
- `_canonical_review_range(root, review_sha)` — `merge-base(<default branch>,
  review_sha)..review_sha`, fail-closed with a named repair on an unresolvable default
  branch, an unresolvable `review_sha`, no merge base, and a degenerate range.
- `_load_test_kinds(root)` — the grade bars come from the checkout under review's own
  `.harness/harness.json`, never from `review_config_path()`; missing or empty is a
  named refusal, never an implicit production bar.
- `_classify_canonical_range` / `_mechanical_code_grade` — `n_a` is decided here and
  only here (the canonical range changed no `.py` path); a deletion-only Python range is
  `pass` per D-04; everything else goes to T-01's `code_grade.classify`, which owns the
  bars and the `fail > grade_2 > pass` precedence.
- `code_grade_enforcement_error` — the comparison. Every mismatch names BOTH the claimed
  and the expected value.
- `validate()`'s reviewer block: the `n_a`-only confirmation is replaced by enforcement
  for all four enum values. `_is_plan_review` still short-circuits it, so DEC-207 plan
  mode never calls the grader.
- Deleted: `_derived_reviewed_python_change` (superseded) and `resolve_review_sha` (no
  caller left — enforcement needs the feature DIRECTORY as well as the SHA, so it uses
  `_resolve_feature_dir` + `_read_review_sha` directly, which is all the wrapper was).

## The availability trade, deliberately taken (D-05)

FEAT-43 exempted `pass`/`fail`/`grade_2` from base derivation so an unresolvable default
branch could not brick reviewer validation. That exemption IS the bypass: a checkout that
cannot derive the repository-owned range cannot prove any mechanical result, and falling
back to the digest's base would restore digest-chosen grading. Every derivation failure
now refuses and names its repair. `check_unresolvable_default_branch` and
`check_no_merge_base` were inverted accordingly and now assert the refusal for all four
values.

## TDD — RED before any production edit

Measured against the unmodified tree, with cwd inside the fixture repo, because the
pre-fix validator resolved commits against the process cwd and that is how the hook ran
in production. (The first attempt was run from elsewhere and every case failed with
`reviewed range could not be resolved to commit revisions.` — a cwd artifact, not the
defect. Recorded because it is the shape that would have made this evidence worthless.)

```
--- blocking production function (src/blocking.py, grade 1, bar 4)
    canonical range : a77e55df096f..9a4fc0a7a211
    digest claims   : code_grade: pass
    validate()      : errors=[]
    --hook exit     : 0
    --hook stderr   : ''
--- committed syntax error (src/broken.py, `def broken(:`)
    canonical range : a77e55df096f..c09ced91c984
    digest claims   : code_grade: pass
    validate()      : errors=[]
    --hook exit     : 0
    --hook stderr   : ''
```

Both ACCEPTED at exit 0 with the grader never invoked. That block is committed verbatim
in `test-validate-digest.py`'s BUG-1081 section header (SC-10).

## Suites

| Suite | Command | Result |
|---|---|---|
| integration | `run-unit-tests.sh --kind integration` | exit 0, 0 `^FAIL ` lines, 588 `PASS` |
| unit | `run-unit-tests.sh --kind unit` | exit 0, 0 `^FAIL ` lines |
| self-grading | `test-code-grade.py` | PASS — every new `validate-digest.py` function clears bar 4, and `SELF_GRADING_ALLOWLIST` has no stale entry |

## Mutation evidence

Each mutation was applied to a COPY in a staged `bin/`, run through
`VALIDATE_DIGEST_BIN`, and compared against a CONTROL run of the UNMUTATED staged copy —
staging alone produces four failures of its own, so only the delta is evidence.
`validate-digest.py`'s sha256 was identical before and after (`e1e8e6ec42ac5cd3`).

| Mutation | New failures over control |
|---|---|
| M1 bypass the comparison (`if True: return None`) | 15 — every mismatch assertion, plus the hook's `got 0` |
| M2 grading exception → `return "pass", None` | 1 (after the gap below was closed) |
| M3 `SyntaxError` → `return "pass", None` | 2 — `a committed syntax error must refuse the digest at exit 2, got 0` |
| M4 fall back to a digest-reachable base | 2 — `the refusal must carry its repair, not only its cause` |

**M2 first reddened NOTHING.** The generic grader-exception branch was unreachable from
the suite, so its greenness meant nothing. `check_malformed_test_kinds` was added for the
reachable production shape of it — a `test_kinds` kind with no `detect`, which
`_load_test_kinds` cannot see inside, so the failure surfaces in `classify` as
`TestKindsError`. M2 reds after that.

## Criteria covered

SC-01, SC-02 (`check_hook_rejects_false_pass`, real `--hook`, exit 2 vs exit 0);
SC-03 (`check_mechanical_result_discrimination`, all four results, accept and reject);
SC-04 (`check_committed_syntax_error`); SC-05 (`check_digest_base_cannot_move_result`);
SC-06 (T-01's `test-code-grade.py`, bars unchanged); SC-07
(`check_plan_review_never_grades`, the seam is traced and never called); SC-08
(`check_judgment_outranks_clean_grade`); SC-10 (RED block above, committed);
SC-11 (`check_unresolvable_default_branch`, `check_no_merge_base`,
`check_derived_base_range`'s degenerate case, `check_missing_test_kinds`,
`check_malformed_test_kinds`).
