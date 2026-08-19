# Receipt — harness-backend-dev — T-01 (c1)

## Summary

Added `file_at_ref(repo, path, ref)` to `.claude/skills/harness/bin/factory_gh.py`: reads one
file's content from a repository at a ref through the REST contents endpoint, asking gh for the
`content` field alone via `--jq ".content"`, and decodes it from base64 to a `str`. Goes through
`run_gh` exactly like every other function in the module. Every failure path raises `GhError`
(repo/path/ref not found, unauthenticated gh, content field absent, content that does not
base64-decode) — none returns a sentinel. `GhError`'s `value` is built as `f"{repo} {path}@{ref}"`
so the message names all three, in order, and is constructed with `factory_cli.body` the same way
every other GhError in this module is (via the class's own `__init__`). No caller added — this
task adds none; T-02 is the caller. Module docstring gained the one sentence placing `file_at_ref`
among the others (it is the only function reading repository CONTENT).

Tests added to `.claude/skills/harness/bin/test-factory-gh.py`, inserted between the existing
`default_branch_sha` block and the existing `delete_ref` block — no existing case removed or
renumbered. Five cases total: the four named in the plan, plus one extra
(`file_at_ref: an absent content field raises rather than defaulting`) covering intent bullet 3's
"a content field that is absent" clause, which none of the four named ok-lines exercises on its
own. The extra case does not collide with or replace any of the four required lines.

## RED first, then GREEN

Confirmed RED before writing any production code: ran the suite immediately after adding the five
new test blocks (function not yet defined) — it crashed with
`AttributeError: module 'factory_gh' has no attribute 'file_at_ref'`, which is a defined-before-
test violation surfaced as a crash rather than a graceful FAIL for every subsequent case. This is
the expected RED shape for adding a wholly new function — the whole suite goes red, not a scoped
`FAIL` line, because nothing under that name exists yet. Then implemented `file_at_ref` and
`import base64` / `import binascii`; suite went to 162/162 green.

## Per-case RED provability (mutate → observe the NAMED case redden → restore → hash check)

Baseline sha256 of `factory_gh.py` (post-implementation, all tests green):
`a3014aa26aef78d550fb7a9ff2e93c6838c54eb244f7ceb247d6bab0a022d08e`

1. **`file_at_ref: returns the decoded file body`** — mutated `return decoded.decode("utf-8")` to
   `return raw` (return the still-base64-encoded string). Ran suite:
   `FAIL  file_at_ref: returns the decoded file body`. Restored. Hash matched baseline.
2. **`file_at_ref: hits the contents path with the ref`** — mutated the query param key from
   `ref=` to `revision=`. Ran suite: `FAIL  file_at_ref: hits the contents path with the ref`.
   Restored. Hash matched baseline.
3. **`file_at_ref: a missing file raises GhError naming repo, path and ref`** — mutated `value` to
   drop `path` (`f"{repo}@{ref}"`). Ran suite:
   `FAIL  file_at_ref: a missing file raises GhError naming repo, path and ref`. Restored. Hash
   matched baseline.
4. **`file_at_ref: undecodable content raises rather than returning empty`** — first tried
   dropping `validate=True` from `b64decode`; the fixture string `"not-valid-base64!!!"` still
   raised `binascii.Error` on bad padding, so that mutation did not redden the case (recorded here
   per the "no net change" discipline, not silently discarded). Second mutation: caught the
   decode error and `return ""` instead of raising. Ran suite:
   `FAIL  file_at_ref: undecodable content raises rather than returning empty`. Restored. Hash
   matched baseline.
5. **`file_at_ref: an absent content field raises rather than defaulting`** (extra case) —
   mutated the guard from `if not raw or raw == "null":` to `if not raw:`, so the literal `"null"`
   jq prints for an absent `.content` field falls through to `b64decode`. `"null"` is valid
   base64 (4 valid chars, correctly padded) and decodes to bytes that are not valid UTF-8, so the
   suite **crashed** with an uncaught `UnicodeDecodeError` inside `file_at_ref` rather than
   printing a graceful `FAIL` line — this is still a proof the case can fail (it does not
   vacuously pass), just via a crash instead of an assertion failure. Restored. Hash matched
   baseline.

After every mutation cycle, `shasum -a 256` on `factory_gh.py` reproduced
`a3014aa26aef78d550fb7a9ff2e93c6838c54eb244f7ceb247d6bab0a022d08e`, and the final
`git diff --stat` shows only the intended additive changes (43 insertions, 0 deletions) — no
residual mutation.

## Why each of the five named `has "..."` clauses in the plan's verify can fail

- `file_at_ref: returns the decoded file body` — proven in mutation 1 above.
- `file_at_ref: hits the contents path with the ref` — proven in mutation 2 above.
- `file_at_ref: a missing file raises GhError naming repo, path and ref` — proven in mutation 3
  above.
- `file_at_ref: undecodable content raises rather than returning empty` — proven in mutation 4
  above.
- `default_branch_sha: returns the sha` — pre-existing case, untouched; it is exactly the case
  the plan calls out to catch a case being dropped by accident. Its test block was not moved,
  edited, or renumbered — confirmed by `git diff` showing only additive lines in
  `test-factory-gh.py` at the insertion point between it and `delete_ref`, nothing changed inside
  the `default_branch_sha` block itself.

## Case 3 — the three-separate-assertions requirement

`file_at_ref: a missing file raises GhError naming repo, path and ref` asserts
`"o/r" in str(exc) and "missing/file.txt" in str(exc) and "release-branch" in str(exc)` — three
separate `in` membership tests on `str(exc)` combined by `and`, not one substring check on a
concatenated string. Repo (`o/r`), path (`missing/file.txt`) and ref (`release-branch`) are three
distinct literals chosen so none is a substring of either of the others.

## `verify:` — literal stdout

Verified the plan.yaml `T-01` `verify:` block is byte-identical to the one quoted in this
dispatch before running it (`python3 -c "import yaml; ..."` dump of the task, cross-checked by
eye against the quoted string — identical).

```
T-01 GREEN
```

## Files touched

- `.claude/skills/harness/bin/factory_gh.py` — added `file_at_ref`, `import base64`,
  `import binascii`, one docstring sentence. 43 insertions, 0 deletions.
- `.claude/skills/harness/bin/test-factory-gh.py` — added five new test cases (four named +
  one extra) and `import base64`. 55 insertions, 0 deletions.

No other files touched. `git status --porcelain` at return time shows only these two modified,
plus pre-existing unrelated dirt (`.claude/skills/harness/templates/harness.json` modified before
this task started, and four untracked FEAT-25/26/27 feature dirs) that this task's hard exclusions
name as not mine — left untouched.

Not committed, per instruction.
