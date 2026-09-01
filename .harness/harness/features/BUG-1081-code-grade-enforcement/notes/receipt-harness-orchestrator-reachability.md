# Receipt — measured reachability for the three fixtures qa could only reason about

**BLUF.** qa's gate PASSED but recorded three fixtures whose assertion strength was
*reasoned, not measured*, because `bash-write-guard` denies that squad the scratch copy a
perturbation proof needs. All three are now measured discriminating. No production file
was modified: every mutation ran against a copy in a staged `bin/`, driven through
`VALIDATE_DIGEST_BIN`, and `validate-digest.py`'s sha256 was `e1e8e6ec42ac5cd3` before and
after every run.

Method note: a CONTROL run of the UNMUTATED staged copy is taken first and only the DELTA
is reported. Staging alone changes what `harness_boundary` resolves and produces failures
of its own — reading the raw failure list would have credited the mutation with them.

| Mutation | New failures over control | The assertion it reds |
|---|---|---|
| M5 `_merge_base_or_none` returns None → grade the whole history instead of refusing | 5 | `code_grade='pass'/'fail'/'grade_2'/'n_a' must be REFUSED when the canonical range cannot be derived ('no merge base')` |
| M6 grader exception → `return "pass", None` | 3 | `a grader exception must become a NAMED refusal, never an acceptance` |
| M7 degenerate range → accept it as empty | 2 | `a review_sha already merged into the default branch must refuse with its own named error` |

M5's failure text is worth reading: with the merge base gone the validator falls back to
`head..head`, which grades `n_a`, so `pass`, `fail` and `grade_2` all fail on the MISMATCH
rather than on the derivation. That is the fallback-to-an-empty-range shape D-05 exists to
refuse, and the fixture catches it.

## Why this was needed at all

This feature's own history contains the answer. During T-02, a mutation that turned the
grader's catch-all exception into an acceptance reddened **nothing** — the branch was
unreachable from the suite and its greenness meant nothing. `check_malformed_test_kinds`
was written for the reachable production shape of it (a `test_kinds` kind with no
`detect`, which `_load_test_kinds` cannot see inside), and M6 above is that same mutation
re-run against the closed gap. Correct-today and pinned-against-regression are separate
claims, and only the second one survives a refactor.

## The residual, carried to the briefing rather than fixed here

qa's Q2 is a real harness gap, not a defect in this change: no member of the validation
squad can produce its own mutation evidence, because the write guard denies the scratch
copy and no disposable worktree is provisioned. Today that work falls to whoever holds
Bash at the orchestrator tier, which is why this receipt exists. It belongs on the backlog,
not in this feature's diff.
