# Receipt — harness-backend-dev — fix-c3

Task: T-01 (`.harness/harness/features/FEAT-24-config-responsibility-split/plan.yaml:295`) —
close the base64 `validate` fail-open gap in `test-factory-gh.py`.

## Fixture

`aGV!sbG8=` — reduces to 8 base64-alphabet chars (8 % 4 == 0), so it never trips a padding
error; it can only be caught by `validate=True` rejecting the embedded `!`. Fed through the
existing `recorder(...)` fake as `Result(0, stdout="aGV!sbG8=")`.

`path` argument: `"path/lax"` (distinct from the existing case's `"path/x"`).

## New ok-line (verbatim)

    file_at_ref: non-alphabet character in otherwise valid-length base64 raises

## Baseline (before adding the case)

    163/163 checks passed.

sha256 of `factory_gh.py` before any mutation:
`88f5d83c82fb1bc90965b38ce71391e3873b7f38b6ab747f8d59fc5236fde08d`

## After adding the case (green)

    165/165 checks passed.

## Mutation: `validate=True` → `validate=False` at `factory_gh.py:456`

FAIL line (literal):

    FAIL  file_at_ref: non-alphabet character in otherwise valid-length base64 raises

Count line (literal):

    1 of 164 FAILING.

Delta vs. step-3 green run (165/165):
- ok lines: 165 → 163 (−2) — matches expected
- FAIL lines: 0 → 1 (+1) — matches expected
- RAN (total checks): 165 → 164 (−1) — matches expected

Confirmed the existing `"not-valid-base64!!!"` case (`undecodable content raises rather than
returning empty`) stayed **green** under the mutation (line 105 of mutated output:
`ok    file_at_ref: undecodable content raises rather than returning empty`) — it cannot see the
`validate` flag, which is the reason the new fixture exists.

## Restore proof

sha256 after restore:
`88f5d83c82fb1bc90965b38ce71391e3873b7f38b6ab747f8d59fc5236fde08d`
(matches pre-mutation hash byte-for-byte)

    $ git diff --exit-code -- .claude/skills/harness/bin/factory_gh.py; echo "diff exit=$?"
    diff exit=0

    $ git status --porcelain .claude/skills/harness/bin/
     M .claude/skills/harness/bin/test-factory-gh.py

Only `test-factory-gh.py` is modified; `factory_gh.py` is clean; no stray `.bak`/`-e` file left.

## T-01 verify (run after restore)

Command (verbatim, cross-checked against `plan.yaml:306-316`, matches the dispatch string exactly):

    out=$(python3 .claude/skills/harness/bin/test-factory-gh.py 2>&1); rc=$?
    has() { printf '%s\n' "$out" | sed -E 's/^(ok|PASS)[ -]+//' | grep -qxF "$1"; }
    has "file_at_ref: returns the decoded file body" || { echo "T-01: the happy-path case did not pass or did not run"; exit 1; }
    has "file_at_ref: hits the contents path with the ref" || { echo "T-01: the argv case did not pass or did not run"; exit 1; }
    has "file_at_ref: a missing file raises GhError naming repo, path and ref" || { echo "T-01: the missing-file case did not pass or did not run"; exit 1; }
    has "file_at_ref: undecodable content raises rather than returning empty" || { echo "T-01: the undecodable case did not pass or did not run"; exit 1; }
    has "default_branch_sha: returns the sha" || { echo "T-01: a pre-existing case vanished"; exit 1; }
    printf '%s\n' "$out" | grep -E "^FAIL" && { echo "T-01: a case failed"; exit 1; }
    test "$rc" = 0 || { echo "T-01: the suite exited $rc"; exit 1; }
    echo "T-01 GREEN"

Output: `T-01 GREEN`

## Full suite

`.claude/skills/harness/bin/run-unit-tests.sh --kind all`, run last, on the restored tree.

Red set: empty (no `FAIL` lines). Exit code: 0.

`test-check-state.py`: PASS. Not investigated per instructions (separate, unrelated finding the
operator is handling).

## files_touched

- `.claude/skills/harness/bin/test-factory-gh.py`
- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/receipt-harness-backend-dev-fix-c3.md`

`factory_gh.py` is NOT in this list — restore confirmed byte-identical above.

## Pure-addition diff (no forbidden weakening)

    $ git diff -- .claude/skills/harness/bin/test-factory-gh.py | grep '^-' | grep -v '^---'
    (no output, exit 1)

Empty — the diff removes nothing. This is direct evidence (not inference) that the existing
`"not-valid-base64!!!"` fixture string and the protected ok-line
`file_at_ref: undecodable content raises rather than returning empty` are byte-identical, and
that no assertion was deleted or swapped.
