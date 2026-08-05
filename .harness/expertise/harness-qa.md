# Expertise — harness-qa

## Patterns (max 15)
- P-01: WHEN citing a test as SC evidence DO read the invocation and the assertion at that line,
  not the test's own label string — a label can name a different verb than the one actually
  invoked, and an unchecked label propagates as a false measurement up the review chain.
- P-02: WHEN scoping a negative assertion (e.g. "X was not closed") DO confirm it filters a
  structured call log to the specific operation, not a stdout substring check — a substring check
  can pass vacuously if unrelated output happens to contain the same text.
- P-03: WHEN a fixture's premise is "this code path is never reached" DO grep the function body
  directly for the call in question rather than trusting the fixture's own comment or name.
- P-04: WHEN a gate reports a single boolean like `matrix_ok: true` DO also state what fraction of
  the diff's tasks the matrix actually required a kind for — a gate can be matrix-correct while
  binding one task and asserting nothing about the rest; the denominator is the finding.
- P-05: WHEN crediting a test as coverage for a change DO confirm the test file is itself part of
  the diff, not pre-existing — only a test added or changed alongside the code demonstrates it
  exercises this change rather than merely happening to exist nearby.

## Gotchas (max 15)
- G-01: WHEN proving a test runner's MISCONFIGURED exit path live by creating a stray
  `test-*.py` probe DO delete it and confirm with `git status --porcelain` before finishing — an
  explicit-list-plus-glob drift detector makes any leftover probe file exit 2 for every run after.

## Outcomes (max 10)

## Open (max 5)
